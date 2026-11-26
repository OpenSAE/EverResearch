# LeRobot experiments and formal run choices

## Purpose and main function

Choose a LeRobot workload using measured runtimes, reproduce its inputs and commands, and find the original adoption check.

## Scope of application

Use this page for local dataset work, training, simulation, and robot operation. Run the commands from the project root after selecting a workload. The estimates describe the tested machine and input revisions.

## Source adoption check

The adoption check used one generated demonstration with eight frames, one CPU training step, and one simulated episode limited to two steps.

- Run manifest records the inputs, commands, and output paths.
- Effective training configuration shows the options that reached training.
- Evaluation results record the rollout metrics, including zero successful episodes out of one.
- Policy checkpoint archive contains the saved local `pretrained_model` directory. Extract it and pass that directory to `lerobot-eval --policy.path` using the simulator options from the manifest.

## Formal run choices

Reference timings were measured during adoption. Reproduce them with the data, weights, and commands below; run artifacts belong to your copied project.
These estimates use the local filesystem, Python 3.12.15, PyTorch 2.11.0 with CUDA 12.8, and one RTX 5090 with 32 GB of memory. CPU commands use the same environment with one OpenMP thread. The current timing runs target about ten workload units and stop within five minutes, including startup, precheck and output writes. Dataset acquisition, staging and waiting for the shared GPU are outside the clock. A batch of eight uses two full batches to reach the target. Whole trajectories, clips and shards stay intact. Training and benchmark workloads beyond the timing trials await selection.

| Run | Complete workload and output | Measured evidence | Estimated wall time |
| --- | --- | --- | --- |
| Review Aloha episodes | Export all **50 episodes and 20,000 frames** in one pass, batch 32 and four workers per command. Writes 50 compressed Rerun recordings for reviewing cameras and joint trajectories, about 360 MB total. No model input. | **Ten complete episodes**, each with 400 consecutive frames, took **66.3 s**. For each invocation, opening the dataset and starting the logger took **3.1–4.7 s**. Decoding, recording and exit took another **2.4–3.9 s**. All ten files passed Rerun readback. Timing and recordings | **4.5–7.5 min** |
| Export an Aloha train and validation split | Split all **50 episodes and 20,000 frames** into two standalone v3 datasets, with **45 episodes and 18,000 frames** for training and **5 episodes and 2,000 frames** for validation. One command and one pass. No model input. | **Ten episodes and 4,000 frames** took **3.65 s** and produced a 9/1 episode split. The sample dataset was staged before timing. Timing and split dataset | **3–8 s** |
| Index Aloha video for streaming | Build a streaming MP4 byte index for **one MP4 spanning 50 episodes and 20,000 frames**, with eight probe workers. Writes a reusable NPZ index, about 150 KiB. No model input. | The complete **one-shard** run took **3.64 s** with pinned metadata in the local cache. Indexing took **0.03 s** and readback found 20,000 presentation timestamps and offsets. Index and console timing | **3–8 s** with local video |
| Preview camera augmentations | Render the **first camera frame of Aloha episode 24** with the six default image transforms and combined variants. One source frame is the full workload of this command. Writes the original and transformed PNGs. No model input. | Reused the complete **one-frame** run, **5.02 s**, including image decoding and PNG writes. Gallery and console timing | **4–7 s** |
| Train ACT on physical SO-101 demonstrations | **50 episodes and 26,647 frames**, 30 Hz, two cameras at 640 × 480. Train on **45 episodes and 23,982 frames**. Validate on **5 episodes and 2,665 frames**. Fresh ACT layers with ImageNet ResNet-18, **five passes**, 14,990 optimizer batches, batch 8, four PyAV loader workers. Saves one checkpoint with model and optimizer state per pass and logs full validation loss. | **16 training and 16 validation frames** in **38.14 s**. Precheck **5.08 s**, first optimizer result at **30.64 s**, second batch **0.049 s**, held-out pass **4.27 s** including loader startup, and checkpoint plus exit **3.19 s**.  | **13–20 min** |
| Reproduce the Aloha ACT training budget | **50 episodes and 20,000 frames**, 50 Hz, one 640 × 480 camera. Train on **45 episodes and 18,000 frames**. Validate on **5 episodes and 2,000 frames**. Fresh ACT layers with ImageNet ResNet-18, **100,000 optimizer batches**, about 44.4 passes, batch 8, four PyAV loader workers. Logs held-out loss and saves five checkpoints every 20,000 updates, around 2.9 GiB total. | **16 training and 16 validation frames** in **42.80 s**. Precheck **8.25 s**, first optimizer result at **35.25 s**, second batch **0.030 s**, held-out pass **4.13 s** including loader startup, and checkpoint plus exit **3.39 s**.  | **45–75 min** |
| Train a FAST action tokenizer | Read all **20,000 Aloha action frames** once. Sample 10% of overlapping ten-frame windows across all **50 episodes**, **1,950 chunks** at 14 action dimensions, mean and standard deviation normalization, vocabulary 1,024. Fits a new tokenizer using the published FAST processor and writes tokenizer files and compression statistics. CPU, sequential by episode. | The smallest complete public input is **one episode**. Its 400 action frames yielded **39 chunks** at the formal sampling fraction in **3.62 s**. About **2.99 s** elapsed before reading the episode, then **0.63 s** for reading, fitting, writing and exit. Tokenizer and timing | **4–9 s** after processor setup |
| Score the published ACT policy in Aloha | Published cube-transfer ACT weights, **50 full MuJoCo episodes**, seed 1000 onward, two synchronous environments per batch, maximum 400 steps each. Writes per-episode rewards, success rate and interval, and up to ten videos. | **Ten full episodes** across five vector batches took **32.43 s**. Startup and exit took **6.02 s** and evaluation plus ten videos took **26.41 s**. After the first batch the measured batches took **4.1–4.7 s**. Seven episodes succeeded. Metrics, videos and timing | **1.5–2.8 min** |
| Score ACT with a separate environment server | Same **50 episodes**, checkpoint and two-environment batches, with MuJoCo in a second process and raw frames over Zenoh loopback. Writes evaluation metrics and a server log. | **Ten full episodes** in **35.13 s**, with **6.34 s** for startup and exit and **28.79 s** inside evaluation. After the first batch, each batch took **4.8–5.0 s**. Seven episodes succeeded. The server supplied a floating-point frame rate that PyAV rejected, so only metrics were saved. Server config and results | **1.8–3 min** on loopback |
| Measure policy serving on recorded observations | Send **1,000 independent RGB and state observations** evenly spaced across the published Aloha demonstrations to the ACT server over Zenoh loopback. Single outstanding request, one 100-step-by-14-joint response per request. Writes per-request timing, response validation, and the effective server configuration. | **Ten independent requests** took **11.28 s** end to end. Server startup after Python imports took **5.55 s**, and the ten frame reads plus requests took **0.169 s**. Request latency was **8.7 ms** median and **15.4 ms** at the 95th percentile. Request timings and server settings | **20–45 s** |
| Record ACT rollouts in simulation | Capture **20 simulator episodes** at 50 Hz with the published ACT checkpoint, up to 8 s or 400 frames each. One run, up to 8,000 frames. Writes video, observations and actions as a LeRobot dataset. | **Ten complete recorded episodes** and **3,215 frames** in **83.45 s**. Recording started at **5.33 s**. The remaining **78.12 s** includes paced control, video encoding and closing the dataset. Dataset and timing | **2.3–3.5 min** |
| Replay a recorded simulator episode | Replay episode 0 from the retained ACT rollout dataset in the matching Aloha simulator, **258 recorded action frames** at 50 Hz. No model input. Writes cadence information to the console. | Reused the complete **258-frame** replay, **9.24 s**, including about 4 s of startup. Replay sustained **49.83 Hz**. Timing and cadence log | **8–12 s** |

Aloha is the project's published human-operated simulator dataset. The SO-101 option uses real robot demonstrations and two cameras. Both timing recipes keep the last five episodes of their single task for validation. They use the project's current validation interface and locally cached ImageNet weights. The Aloha recipe takes the publisher's 100,000-update training budget and adds the held-out loss pass. Simulator scoring can use any compatible training checkpoint after the run is selected. The separately published ACT checkpoint gives a reference with known inputs. [Publisher dataset](https://huggingface.co/datasets/lerobot/aloha_sim_transfer_cube_human) · [ACT release](https://huggingface.co/lerobot/act_aloha_sim_transfer_cube_human) · [SO-101 demonstrations](https://huggingface.co/datasets/Gowshigan/pick-and-place-so101)

The training estimates allow **0.025–0.042 s** per optimizer batch for Aloha and **0.045–0.068 s** for SO-101, plus validation and checkpoint writes. The bounded validation loader read the first 16 frames of the first held-out episode in each case. The validation projection uses those measurements and allows additional decode time across the other episodes. The reported validation time combines worker launch and two batches. The single warm training batch measures queued input, so complete-run storage behavior remains an uncertainty. The full-run ranges allow these startup and decoding effects, along with five checkpoints of about 592 MiB each. Simulator estimates charge startup once and project per-batch rates. Local evaluation renders its ten-video budget during the first five batches. Later batches only write scores. The sampled success counts are recorded with the sampled seeds. A separate physical run still needs a matching controller, camera calibration and task reset procedure.

### Start a selected run

Activate the [project environment](environment/README.md). The commands below use the supported interpreter and dependencies. Give every selected run a fresh output path. The pinned dataset directories contain metadata, parquet records, and the original MP4 shards.

```bash
export OMP_NUM_THREADS=1 HF_HUB_OFFLINE=1 MUJOCO_GL=egl
: "${LEROBOT_DATA_ROOT:?Set a directory containing the datasets and checkpoints described below}"
export TORCH_HOME="${LEROBOT_DATA_ROOT}/torch"
aloha_id=lerobot/aloha_sim_transfer_cube_human
aloha_revision=6a43d500f101255823a9d2b9dc244eeb01a2cd31
aloha="${LEROBOT_DATA_ROOT}/aloha_sim_transfer_cube_human/$aloha_revision"
physical_id=Gowshigan/pick-and-place-so101
physical_revision=f92cac7aad5d46086b718bbacc9ebaacd47c82d7
physical="${LEROBOT_DATA_ROOT}/pick_and_place_so101/$physical_revision"
policy_revision=ba73b2766f1371cdc133ca4efb97eb090d744625
original_policy="${LEROBOT_DATA_ROOT}/act_aloha_sim_transfer_cube_human/$policy_revision"
policy=${original_policy}_migrated
work="$PWD/tmp/selected_workload"
mkdir -p "$work"
```

Stage the files required by your selected run with the Hugging Face CLI:

```bash
env -u HF_HUB_OFFLINE hf download "$aloha_id" --repo-type dataset --revision "$aloha_revision" --local-dir "$aloha"
env -u HF_HUB_OFFLINE hf download "$physical_id" --repo-type dataset --revision "$physical_revision" --local-dir "$physical"
env -u HF_HUB_OFFLINE hf download lerobot/act_aloha_sim_transfer_cube_human --revision "$policy_revision" --local-dir "$original_policy"
```

The pinned Aloha files took **11.4 s** to stage (67 MiB). The physical SO-101 data took **87.6 s** to stage (about 447 MiB). The ACT release took **30.5 s** (197 MiB), the ImageNet ResNet-18 backbone took **7.4 s** (45 MiB), and the simulator dependencies were already installed. The published checkpoint keeps normalization inside the original state dictionary. Run the bundled migration to place those statistics in the current input and output processors. The migration took **4.3 s** after download and uses the Hub's model-card validation endpoint. [Migration details](code/reference/source/backwardcomp.mdx)

```bash
env -u HF_HUB_OFFLINE CUDA_VISIBLE_DEVICES='' \
  python base/lerobot_library/processor/migrate_policy_normalization.py \
  --pretrained-path "$original_policy" --output-dir "$policy"
```

To review or prepare the demonstrations, select the applicable command. The exported split is a standalone data handoff. The training command forms its own ordered hold-out directly from the original data.

```bash
for episode in $(seq 0 49); do
  lerobot-dataset-viz --repo-id "$aloha_id" --root "$aloha" \
    --episode-index "$episode" --save 1 --output-dir "$work/episode_review" \
    --batch-size 32 --num-workers 4 --display-compressed-images
done

lerobot-edit-dataset --repo_id="$aloha_id" --root="$aloha" \
  --new_repo_id=local/aloha_review_split --new_root="$work/edited_split" \
  --operation.type=split --operation.splits='{"train":0.9,"validation":0.1}' --push_to_hub=false

lerobot-build-mp4-sidecar --repo-id "$aloha_id" \
  --revision "$aloha_revision" --data-root "$aloha" \
  --output "$work/video_index.npz" --workers 8

view="$work/transform_preview"
mkdir -p "$view/$aloha_id"
for part in meta data videos; do ln -s "$aloha/$part" "$view/$aloha_id/$part"; done
(cd "$view" && HF_LEROBOT_HOME="$view" lerobot-imgtransform-viz \
  --repo_id="$aloha_id" --episodes='[24]' --video_backend=pyav --image_transforms.enable=true)
```

For offline training, choose one dataset and use the precheck with the same arguments as the training command. The following two calls are independent. Activate or install the training extra to run them.

```bash
train_act() {
  local repo_id=$1 root=$2 steps=$3 interval=$4 out=$5
  local args=(
    --dataset.repo_id="$repo_id" --dataset.root="$root" --dataset.video_backend=pyav
    --dataset.eval_split=0.1 --policy.type=act --policy.device=cuda --policy.push_to_hub=false
    --batch_size=8 --num_workers=4 --steps="$steps" --eval_steps="$interval"
    --save_freq="$interval" --env_eval_freq=0 --output_dir="$out"
  )
  lerobot-precheck "${args[@]}" && lerobot-train "${args[@]}"
}

train_act "$physical_id" "$physical" 14990 2998 "$work/train_so_robot"
train_act "$aloha_id" "$aloha" 100000 20000 "$work/train_aloha"
```

To train the tokenizer, point `HF_HOME` at the prepared offline FAST processor cache. The published processor has no model-type metadata for its tokenizer, and Transformers 5.22.2 requires it. The original Hub snapshot is preserved. The prepared local copy adds only `config.json` to the snapshot root and its `bpe_tokenizer/` folder with `{"model_type":"bert","tokenizer_class":"TokenizersBackend"}`. Use the local copy only with offline Hub access.

```bash
HF_HOME=${LEROBOT_DATA_ROOT}/fast_tokenizer_compatible_hub \
  lerobot-train-tokenizer --repo_id="$aloha_id" --root="$aloha" \
  --action_horizon=10 --sample_fraction=0.1 --encoded_dims=0:14 \
  --normalization_mode=MEAN_STD --vocab_size=1024 --scale=10.0 \
  --output_dir="$work/fast_tokenizer" --push_to_hub=false
```

To score the checkpoint, run local evaluation, or start the environment server using the measured server configuration and run served evaluation from a second terminal. The served and policy-serving options use the `remote` extra. Stop the environment server when the selected evaluation ends.

```bash
eval_args=(
  --env.type=aloha --env.task=AlohaTransferCube-v0 --env.episode_length=400
  --policy.path="$policy" --policy.device=cuda --eval.n_episodes=50
  --eval.batch_size=2 --eval.use_async_envs=false
)
lerobot-eval "${eval_args[@]}" --output_dir="$work/evaluation"

lerobot-env-server --config_path=experiment/lerobot_dataset/policies/act/evaluation/served_aloha_timing/reports/server_config.yaml
# Second terminal, with the same environment and variables
lerobot-eval "${eval_args[@]}" --env.server.endpoint=tcp/127.0.0.1:17448 \
  --output_dir="$work/served_evaluation"

python scripts/benchmarks/profile_aloha_service.py --dataset-root "$aloha" \
  --policy "$policy" --requests 1000 --output "$work/policy_service"
```

To record a deployment exercise at the simulator's control rate, run episodic rollout. Replay the original traced episode by extracting `artifacts/rollout_dataset.tar` from the timed rollout into `$work`.

```bash
task='Pick up the cube with the right arm and transfer it to the left arm.'
lerobot-rollout --robot.type=sim --robot.env.type=aloha --robot.env.task=AlohaTransferCube-v0 \
  --robot.env.episode_length=400 --policy.path="$policy" --device=cuda --fps=50 \
  --inference.type=sync --strategy.type=episodic --strategy.reset_to_initial_position=false \
  --return_to_initial_position=false --play_sounds=false --dataset.no_stamp=true \
  --dataset.repo_id=local/rollout_aloha --dataset.root="$work/recording" \
  --dataset.single_task="$task" --dataset.num_episodes=20 --dataset.episode_time_s=8 \
  --dataset.reset_time_s=0 --dataset.fps=50 --dataset.push_to_hub=false

# The preceding lerobot-record command writes "$work/rollout_dataset".
lerobot-replay --robot.type=sim --robot.env.type=aloha --robot.env.task=AlohaTransferCube-v0 \
  --robot.env.episode_length=400 --dataset.repo_id=local/rollout_aloha_sample \
  --dataset.root="$work/rollout_dataset" --dataset.episode=0 --play_sounds=false
```

### Physical SO-101 workflows

Use one calibrated SO-101 follower and its matching camera setup. Recording and teleoperation also need a calibrated leader. The device probe found no serial motor ports or video capture devices on this machine, so the durations in this table are configured motion and reset time. An actual session must also include connection and calibration, operator resets and retakes, output encoding where applicable, and optional upload. Measure a complete episode on the intended robot to turn these configured durations into a wall-time estimate. [SO-101 setup and commands](code/agent_guide.md#4-so-101-end-to-end-cheat-sheet)

| Workflow | Priority input and planned workload | Output and timing basis |
| --- | --- | --- |
| Teleoperate then record fresh demonstrations | Calibrated leader and follower, a front and wrist camera at 30 Hz, and an operator performing a single pick-and-place task. A one-minute teleoperation check precedes 50 episodes of up to 30 s each, with 10 s between episodes. No input dataset or policy model. | Camera frames, observed joint positions and demonstrated actions. **33 min 10 s** of configured recording and reset windows, plus the one-minute check and operator and encoding time. |
| Replay a physical trajectory | Use episode 0 of the published SO-101 demonstrations only after checking matching joint order, calibration convention, arm body, and scene placement, or use episode 0 from the fresh recording with that exact setup. The published episode has **533 actions at 30 Hz**. No model input. | Reproduces the selected trajectory and prints control cadence. The selected recording has **17.8 s** of nominal playback before connection and shutdown. The retained simulated replay exercises the same command with the matching simulated robot. |
| Score a trained policy on the physical robot | Use the SO-101 ACT training option or a compatible checkpoint trained on that exact camera and calibration setup. Collect ten episodic rollouts at 30 Hz, up to 30 s each, with a 10 s reset between episodes. | Writes a LeRobot dataset for operator success scoring. **6 min 30 s** of configured episode and reset windows, with additional setup, target placement and encoding time. The Aloha capture is a computer-only exercise of the rollout and recording path. |

Run these commands on the machine connected to the arms. Set `FOLLOWER_PORT`, `LEADER_PORT`, and `SO_CAMERAS` to the actual configuration. `SO_CAMERAS` must define the front and wrist cameras under the same names used for training. Set `SO_TASK` to the operator’s task instruction and `SO_POLICY` to the selected training run's `checkpoints/last/pretrained_model`.

```bash
follower=(--robot.type=so101_follower --robot.port="$FOLLOWER_PORT" --robot.id=pick_follower)
leader=(--teleop.type=so101_leader --teleop.port="$LEADER_PORT" --teleop.id=pick_leader)
lerobot-calibrate "${follower[@]}"
lerobot-calibrate "${leader[@]}"
lerobot-teleoperate "${follower[@]}" "${leader[@]}" --robot.cameras="$SO_CAMERAS" \
  --fps=30 --teleop_time_s=60
lerobot-record "${follower[@]}" "${leader[@]}" --robot.cameras="$SO_CAMERAS" \
  --dataset.repo_id=local/pick_demonstrations --dataset.root="$work/physical_demonstrations" \
  --dataset.single_task="$SO_TASK" --dataset.num_episodes=50 --dataset.fps=30 \
  --dataset.episode_time_s=30 --dataset.reset_time_s=10 --dataset.no_stamp=true \
  --dataset.push_to_hub=false

lerobot-replay "${follower[@]}" --dataset.repo_id="$physical_id" \
  --dataset.root="$physical" --dataset.episode=0 --play_sounds=false

lerobot-rollout "${follower[@]}" --robot.cameras="$SO_CAMERAS" --policy.path="$SO_POLICY" \
  --strategy.type=episodic --fps=30 --dataset.fps=30 \
  --dataset.repo_id=local/rollout_pick_and_place --dataset.root="$work/physical_rollout" \
  --dataset.single_task="$SO_TASK" --dataset.num_episodes=10 \
  --dataset.episode_time_s=30 --dataset.reset_time_s=10 --dataset.no_stamp=true \
  --dataset.push_to_hub=false
```

### Language annotation and human-in-the-loop reinforcement learning

| Run | Inputs, workload and outputs | Timing status |
| --- | --- | --- |
| Generate language annotations | Use the complete published Aloha set, **50 episodes and 20,000 frames**, and the pinned Qwen2.5-VL-3B-Instruct weights below. The plan module samples at 2 Hz and reads roughly **16 keyframes per episode**. It makes describe and segment requests and then plan and memory requests at generated subtask boundaries. One sequential pass rewrites a copy of the three parquet data shards with language columns. | Ten evenly spaced **complete episodes** took **103.62 s**. The planning phase began at **19.56 s** and episodes took **3.7–13.4 s** each. Readback found persistent annotations on **4,000 frames**. The projected full run is **6–11 min** with the same sequential settings. Model download took **9 min 20 s** for 7.1 GiB. Annotated dataset and timing |
| Train online with a human in the loop | Use the published **30 demonstrations and 458 frames** for Franka Panda cube pickup, a Gaussian actor and Soft Actor Critic initialized for the task, and the published ResNet-10 vision encoder. The publisher's Gym HIL example uses **1,000,000 online actor steps at 10 Hz**, learner batch 256 drawn from offline and online experience, and begins learning after 100 online transitions. Save policy and optimizer checkpoints, replay data and actor/learner logs. | The bounded keyboard CPU run used the required **100-step warmup**, then **10 more actor steps** and **one full learner batch of 256**. The first learner update took **19.4 s**. The run reached actor completion and saved model and optimizer files, then stopped at **59.11 s** when offline replay export rejected floating-point pixel values above 1. The configured GPU control intervals total **27 h 47 min**. A reliable complete runtime needs a successful replay export and timing on the intended GPU with operator intervention. Timing, logs and partial checkpoint |

Annotation uses a fresh dataset copy and a local server in the project environment. Its optional OpenAI-compatible serving dependencies are available on this machine. The `--only_episodes` option limits a calibration run to episodes 0, 5, 11, 16, 22, 27, 33, 38, 44 and 49. Leave it off for the complete selection. [Annotation model](https://huggingface.co/Qwen/Qwen2.5-VL-3B-Instruct/tree/66285546d2b821cf421d4f5eb2576359d3770cd3)

```bash
vlm=${LEROBOT_DATA_ROOT}/qwen_vision_language/66285546d2b821cf421d4f5eb2576359d3770cd3
mkdir -p "$work/annotations"
cp -a "$aloha"/{meta,data,videos} "$work/annotations/"
lerobot-annotate --root="$work/annotations" --video_backend=pyav \
  --vlm.model_id="$vlm" --vlm.api_base=http://127.0.0.1:18451/v1 --vlm.serve_port=18451 \
  --vlm.serve_command="transformers serve $vlm --host 127.0.0.1 --port {port} --device cuda:0 --dtype bfloat16" \
  --vlm.max_new_tokens=384 --vlm.request_timeout_s=120 --vlm.client_concurrency=1 \
  --executor.episode_parallelism=1 --plan.n_task_rephrasings=0 \
  --interjections.enabled=false --vqa.enabled=false --push_to_hub=false
```

For online reinforcement learning, start the learner first, then the actor from a terminal with the simulator display and intervention input. When the actor logs that its policy loop has finished, wait for any learner checkpoint write and stop the learner so the actor can close its parameter stream. This machine staged the publisher's demonstrations and encoder in **36.4 s**. The sample configuration uses a gamepad. For a session with a keyboard, select `PandaPickCubeKeyboard-v0` and set `env.processor.control_mode` to `keyboard`. The keyboard session performs the same cube pickup with a different intervention device. The CPU trial reproduced the keyboard actor's observation loop without operator interventions. It used an Xvfb display, `LIBGL_ALWAYS_SOFTWARE=1`, `--policy.device=cpu`, and `TORCHDYNAMO_DISABLE=1`. With compilation enabled on CPU the learner ended with a segmentation fault after the first recorded episode. CPU compiler attempt [Gym HIL instructions](code/reference/source/hilserl_sim.mdx) · [Pinned publisher recipe](https://huggingface.co/datasets/lerobot/config_examples/blob/4803f5f379568ddc77763f5a4dd7cd56973d6a10/rl/gym_hil/train_config.json) · [Demonstration data](https://huggingface.co/datasets/lilkm/pick_cube_franka_panda_30/tree/f80a680a117d0c8573ab453e3fd9e792e308dfa4) · [Encoder](https://huggingface.co/lerobot/resnet10/tree/60e4365989619db6365ba92b1169d5dcc143d165)

```bash
panda=${LEROBOT_DATA_ROOT}/panda_pick_cube/f80a680a117d0c8573ab453e3fd9e792e308dfa4
export HF_HOME=${LEROBOT_DATA_ROOT}/hil_hub
curl -fsSL https://huggingface.co/datasets/lerobot/config_examples/raw/4803f5f379568ddc77763f5a4dd7cd56973d6a10/rl/gym_hil/train_config.json \
  -o "$work/panda_publisher.json"
jq --arg input "$panda" --arg output "$work/panda" '
  del(.wandb) | .trackio = {enable: false} | .dataset.root = $input |
  .dataset.video_backend = "pyav" | .output_dir = $output |
  .policy.vision_encoder_name = "lerobot/resnet10@60e4365989619db6365ba92b1169d5dcc143d165" |
  .policy.trust_remote_code = true | .save_freq = 10000
' "$work/panda_publisher.json" >"$work/panda_config.json"
python -m lerobot.rl.learner --config_path="$work/panda_config.json"
# Second terminal, with the same environment and variables
python -m lerobot.rl.actor --config_path="$work/panda_config.json" --output_dir="$work/panda_actor"
```

`lerobot-info`, port and camera discovery, motor identification, CAN setup, and joint-limit tools provide setup checks for workflows on the relevant hardware. The `lerobot-convert-dcp` utility is for sharded training checkpoints. The selected ACT recipes produce whole safetensors checkpoints and use their checkpoint directories directly.

### Earlier timing records

The previous larger samples remain available for comparison. The formal estimates above use the bounded runs and the complete single-unit measurements identified in the table. Extended Aloha training · Extended SO-101 training · Earlier policy service · Earlier tokenizer · Earlier annotation · Earlier keyboard simulation
