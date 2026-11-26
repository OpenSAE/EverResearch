#!/bin/bash

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$PROJECT_DIR" || exit 1


# Pub IP
PUBLIC_IP=$(curl -s ifconfig.me)

if [ -z "$PUBLIC_IP" ]; then
  echo "No valid IP get!"
  exit 1
fi

LAST_TWO_OCTETS=$(echo "$PUBLIC_IP" | awk -F'.' '{print $3"."$4}')

# --- Configuration Section ---
# 1. Define the log directory
LOG_DIR="${AGENTFLOW_TRAINING_LOGS:-$PROJECT_DIR/experiment/training_logs}/${PUBLIC_IP}/train_log"

# 2. Define the prefix for output files
LOG_PREFIX="training_output_$(date -u +%Y%m%d%H%M%S)_"

# 3. Define the maximum size of a single log file (1MB)
LOG_SIZE='1M'

# 4. Define the maximum number of log files to keep (mimics backupCount behavior)
MAX_LOG_FILES=5000

# 5. Read CUDA_VISIBLE_DEVICES from config.yaml if available
if [ -f "conf/config.yaml" ]; then
    CUDA_DEVICES=$(grep -m1 "CUDA_VISIBLE_DEVICES:" conf/config.yaml | sed "s/.*CUDA_VISIBLE_DEVICES: *['\"]\\([^'\"]*\\)['\"].*/\\1/")
    if [ -n "$CUDA_DEVICES" ]; then
        export CUDA_VISIBLE_DEVICES="$CUDA_DEVICES"
        echo "Setting CUDA_VISIBLE_DEVICES=$CUDA_VISIBLE_DEVICES from config.yaml"

        # Restart Ray to apply GPU settings
        echo "Restarting Ray to apply GPU settings..."
        ray stop -v --force --grace-period 60 2>/dev/null || true
        env RAY_DEBUG=legacy HYDRA_FULL_ERROR=1 VLLM_USE_V1=1 CUDA_VISIBLE_DEVICES="$CUDA_DEVICES" ray start --head --dashboard-host=0.0.0.0
    fi
fi

# 6. The Python command you want to run (enclosed in quotes)
PYTHON_COMMAND="python -m agentflow.training.train_agent"
# Or a more complex command, for example:
# PYTHON_COMMAND="python -m agentflow.verl algorithm.adv_estimator=grpo data.train_batch_size=8"

# --- Main Logic ---

# Remove and recreate the log directory for a clean start
mkdir -p "$LOG_DIR" # Using -p is safer, it doesn't error if the directory exists

# Calculate the required number of digits for the suffix based on MAX_LOG_FILES
# For example, if MAX_LOG_FILES is 5000, the largest index is 4999, which has 4 digits.
MAX_INDEX=$((MAX_LOG_FILES - 1))
SUFFIX_DIGITS=${#MAX_INDEX}

echo "Starting the task... Log files will use $SUFFIX_DIGITS-digit suffixes (e.g., 0001, 0002...)"

# Execute the Python command and pipe its output to 'split'
# -d uses numeric suffixes
# -a specifies the length of the suffix, automatically adding leading zeros
PYTHONUNBUFFERED=1 $PYTHON_COMMAND 2>&1 | \
    split -b "$LOG_SIZE" -d -a "$SUFFIX_DIGITS" - "$LOG_DIR/$LOG_PREFIX"

# Get the exit status of the 'split' command from the pipe
command_status=( "${PIPESTATUS[@]}" )
SPLIT_EXIT_CODE=${command_status[0]:-1}
if [ "$SPLIT_EXIT_CODE" -eq 0 ]; then
    SPLIT_EXIT_CODE=${command_status[1]:-1}
fi

# Check if the command executed successfully
if [ $SPLIT_EXIT_CODE -eq 0 ]; then
    echo "Task completed successfully."
else
    echo "Error: The task or log splitting failed with exit code $SPLIT_EXIT_CODE."
    exit $SPLIT_EXIT_CODE
fi

# Clean up: keep only the newest MAX_LOG_FILES files (by modification time)
# This is a robust way to handle cleanup for a single, long-running process
echo "Cleaning up old log files, keeping the latest $MAX_LOG_FILES..."
ls -1t "$LOG_DIR"/"$LOG_PREFIX"* 2>/dev/null | \
    tail -n +$((MAX_LOG_FILES + 1)) | \
    xargs rm -f

echo "Log files are saved in: $LOG_DIR"
