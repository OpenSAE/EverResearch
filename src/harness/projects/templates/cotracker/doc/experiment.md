# Tracking experiments

## Purpose and main function

Locate tracking coordinates, visibility values, overlays, and execution records.

## Scope of application

Use this page to inspect results from the managed offline tracking command.

The tracking command writes under `experiment/video_tracking/tracking/tracking/<study>/`. Choose a fresh descriptive study name with `--subname` for another run. Use `cotracker inspect <study-directory>` to read the manifest and verify that its declared files exist. `artifacts/tracks.npz` contains the arrays `tracks` and `visibility`. `artifacts/video.mp4` contains rendered trajectories. `metadata/config.json` and `metadata/manifest.json` record the effective settings and execution state. The four-frame startup check is recorded in `reports/precheck.json`. An invalid query is recorded with the reason and the formal calculation stays blocked.

## Bounded formal run profiles

Use the [formal run choices](maintenance.md#formal-run-choices) to reproduce each profile.
A managed run writes its effective configuration, startup checks, and result manifest into
the copied project. Use `cotracker inspect <run-directory>` to verify the declared files.

| Workflow | Evidence to retain |
| --- | --- |
| Offline and online point tracking | Input frame count, checkpoint identity, elapsed time, coordinates and visibility where available, and a readable overlay. |
| TAP-Vid DAVIS evaluation | The split, query protocol, model and runtime, per-clip scores, and aggregate metrics. |
| Kubric supervised training | Measured optimizer steps, validation and checkpoint writes. For a blocked recipe record the last completed stage. |
| Real-video fine-tuning | Loader acceptance, teacher weights, and a representative optimizer step when the required dataset adapter is available. |
| Interactive grid demo | Elapsed time for independent requests and the returned overlay files. |
