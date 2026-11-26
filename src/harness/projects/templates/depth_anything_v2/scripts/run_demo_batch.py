"""Submit a local batch to the official demo and record end-to-end request timings.

Run with the demo extra installed and DEPTH_ANYTHING_WEIGHTS set.
"""

import argparse
import os
from pathlib import Path
import socket
import subprocess
from tempfile import TemporaryDirectory
from time import perf_counter, sleep
from types import SimpleNamespace
from urllib.request import urlopen

from gradio_client import Client, handle_file
from PIL import Image

from depth_anything_v2.research.records import RunRecord, write_json


def wait_for_demo(server, url):
    deadline = perf_counter() + 60
    while perf_counter() < deadline:
        try:
            with urlopen(url, timeout=1):
                return
        except OSError:
            if server.poll() is not None:
                raise RuntimeError(f"Demo command exited with code {server.returncode}")
            sleep(0.25)
    raise RuntimeError("The demo server did not become ready within 60 seconds.")


def stop_demo(server):
    server.terminate()
    try:
        server.wait(timeout=15)
    except subprocess.TimeoutExpired:
        server.kill()
        server.wait()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image-list", required=True, type=Path)
    parser.add_argument("--study", default="demo_workload")
    parser.add_argument("--workspace", type=Path, default=Path.cwd())
    args = parser.parse_args()
    args.workspace = args.workspace.resolve()
    files = [Path(line).resolve() for line in args.image_list.read_text().splitlines() if line.strip()]
    if not files or not all(file.is_file() for file in files):
        raise ValueError("The demo batch needs a nonempty list of existing image paths.")

    weights = Path(os.environ.get("DEPTH_ANYTHING_WEIGHTS", args.workspace / "checkpoints")).resolve()
    checkpoint = weights / "depth_anything_v2_vitl.pth"
    config = {
        "dataset": "image_files",
        "model": "depth_anything_large",
        "task": "demo",
        "checkpoint": str(checkpoint),
        "batch_size": 1,
        "input_size": 518,
    }
    options = SimpleNamespace(outdir=None, study=args.study, workspace=args.workspace)
    record = RunRecord(options, config, files)
    with socket.socket() as endpoint:
        endpoint.bind(("127.0.0.1", 0))
        port = endpoint.getsockname()[1]
    command = [
        "depth-anything", "--workspace", str(args.workspace), "demo", "--encoder", "vitl",
        "--load-from", str(checkpoint), "--port", str(port),
    ]
    url = f"http://127.0.0.1:{port}"
    started = perf_counter()
    try:
        with TemporaryDirectory() as scratch:
            directory = Path(scratch)
            server = subprocess.Popen(
                command,
                env={**os.environ, "GRADIO_ANALYTICS_ENABLED": "False",
                     "GRADIO_TEMP_DIR": str(directory / "service"), "TMPDIR": str(directory)},
            )
            try:
                wait_for_demo(server, url)
                client = Client(url, verbose=False, download_files=directory / "downloads", analytics_enabled=False)
                ready = perf_counter()
                record.start_work({
                    "samples_checked": 1,
                    "elapsed_seconds": ready - started,
                    "scope": "Demo automatic example check and readiness of the loopback service",
                })
                timings = []
                for index, image in enumerate(files, 1):
                    request = perf_counter()
                    outputs = client.predict(handle_file(str(image)), api_name="/on_submit")
                    for filename in outputs[1:]:
                        with Image.open(filename) as result:
                            result.verify()
                    timings.append({"image": str(image), "seconds": perf_counter() - request})
                    if index % 20 == 0:
                        print(f"Demo completed {index}/{len(files)} requests", flush=True)
            finally:
                stop_demo(server)
        write_json(record.artifact("request_timings", ".json"), {
            "command": command,
            "samples": len(files),
            "server_ready_seconds": ready - started,
            "elapsed_seconds": perf_counter() - started,
            "requests": timings,
        })
    except KeyboardInterrupt as error:
        record.finish("interrupted", error)
        raise
    except Exception as error:
        record.finish("failed", error)
        raise
    record.finish("succeeded")
    print(record.directory)


if __name__ == "__main__":
    main()
