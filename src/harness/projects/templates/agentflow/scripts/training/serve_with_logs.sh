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
LOG_DIR="${AGENTFLOW_TRAINING_LOGS:-$PROJECT_DIR/experiment/training_logs}/${PUBLIC_IP}/serve_log"

# 2. Define the prefix for output files
LOG_PREFIX="serving_output_$(date -u +%Y%m%d%H%M%S)_"

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
    fi
fi

# 6. The Python command you want to run (enclosed in quotes)
PYTHON_COMMAND="python -m agentflow.training.run_rollout"
# Or a more complex command, for example:
# PYTHON_COMMAND="python -m agentflow.verl algorithm.adv_estimator=grpo data.train_batch_size=8"

# --- Function: calculate digit length of a number ---
suffix_length() {
    # This is a more concise way to get the length of a number in bash
    echo "${#1}"
}

# Remove and recreate the log directory
mkdir -p "$LOG_DIR"

# Calculate suffix digit length: we need to represent up to (MAX_LOG_FILES - 1)
SUFFIX_DIGITS=$(suffix_length $((MAX_LOG_FILES - 1)))

echo "Starting the task... Log files will use $SUFFIX_DIGITS-digit suffixes (000... to $((MAX_LOG_FILES - 1)))"

# Use split with dynamic suffix length
PYTHONUNBUFFERED=1 $PYTHON_COMMAND 2>&1 | \
    split -b "$LOG_SIZE" -d -a "$SUFFIX_DIGITS" - "$LOG_DIR/$LOG_PREFIX"

command_status=( "${PIPESTATUS[@]}" )
SPLIT_EXIT_CODE=${command_status[0]:-1}
if [ "$SPLIT_EXIT_CODE" -eq 0 ]; then
    SPLIT_EXIT_CODE=${command_status[1]:-1}
fi

if [ $SPLIT_EXIT_CODE -eq 0 ]; then
    echo "Task completed successfully."
else
    echo "Error: The task or log splitting failed with exit code $SPLIT_EXIT_CODE."
    exit $SPLIT_EXIT_CODE
fi

# Clean up: keep only the newest MAX_LOG_FILES files (by modification time)
echo "Cleaning up old log files, keeping the latest $MAX_LOG_FILES..."
ls -1t "$LOG_DIR"/"$LOG_PREFIX"* 2>/dev/null | \
    tail -n +$((MAX_LOG_FILES + 1)) | \
    xargs rm -f

echo "Log files are saved in: $LOG_DIR"
