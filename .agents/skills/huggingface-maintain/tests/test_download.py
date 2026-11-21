"""Purpose and main function: Check for restoration and editing retention of fixed version copies through local warehouse samples.

Scope of application: Users perform download back check as required; use local SDK The double. All the temporarys are in the skills..
"""
import importlib.util
import json
import os
from pathlib import Path
import tempfile
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import patch

SKILL = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('download_assets', SKILL / 'scripts/download_assets.py')
downloads = importlib.util.module_from_spec(spec)
spec.loader.exec_module(downloads)


class DownloadRecovery(unittest.TestCase):
    def test_resume_each_copy_phase_and_preserve_edits(self):
        for failure in ('source', 'checkout', 'repository'):
            with self.subTest(failure=failure):
                results = SKILL / 'results'
                results.mkdir(exist_ok=True)
                with tempfile.TemporaryDirectory(prefix='check-download-', dir=results) as temporary:
                    home = Path(temporary)
                    snapshot = home / 'pinned'
                    snapshot.mkdir()
                    (snapshot / 'README.md').write_text('Original source\n')
                    sdk = ModuleType('huggingface_hub')
                    sdk.HfApi = lambda: SimpleNamespace(repo_info=lambda *a, **k: SimpleNamespace(
                        sha='a' * 40, private=False, siblings=[SimpleNamespace(rfilename='README.md', size=16)]))
                    snapshot_calls = []
                    def fetch(*args, **kwargs):
                        snapshot_calls.append(kwargs['revision'])
                        return str(snapshot)
                    sdk.snapshot_download = fetch
                    real_copy, real_save = downloads.shutil.copytree, downloads.save
                    interrupted = False

                    def copy(source, target, **kwargs):
                        nonlocal interrupted
                        if Path(target).name == '.' + failure + '-copying' and not interrupted:
                            interrupted = True
                            Path(target).mkdir()
                            (Path(target) / 'partial.txt').write_text('interrupted')
                            raise OSError('Simulated interrupted copy')
                        return real_copy(source, target, **kwargs)

                    def save(task, path, value, content):
                        nonlocal interrupted
                        if failure == 'repository' and path.name == 'repository.json' and not interrupted:
                            interrupted = True
                            raise OSError('Simulated interrupted record')
                        return real_save(task, path, value, content)

                    with patch.object(downloads, 'SKILL', home), patch.dict('sys.modules', {'huggingface_hub': sdk}), patch.dict(os.environ):
                        with patch.object(downloads.shutil, 'copytree', copy), patch.object(downloads, 'save', save):
                            self.assertEqual(downloads.download('example', [('space', 'sample/repository')]), 1)
                        self.assertEqual(downloads.download('example', [('space', 'sample/repository')], resume=True), 0)
                        repository = home / 'results/example/sample/spaces/repository'
                        (repository / 'checkout/README.md').write_text('Local edits\n')
                        self.assertEqual(downloads.download('example', [('space', 'sample/repository')], resume=True), 0)
                        if failure != 'source':
                            self.assertEqual(len(snapshot_calls), 1)
                        self.assertEqual((repository / 'source/README.md').read_text(), 'Original source\n')
                        self.assertEqual((repository / 'checkout/README.md').read_text(), 'Local edits\n')
                        self.assertEqual(json.loads((home / 'results/example/inventory.json').read_text())['repositories'][0]['phase'], 'complete')


if __name__ == '__main__':
    unittest.main()
