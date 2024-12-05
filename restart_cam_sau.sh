#!/bin/bash

LOG_FILE="/home/hello/project/stream_camera/check_cam_sau.log"

# Function to check and reset log file if it exceeds 3000 lines
check_log_file_size() {
    line_count=$(wc -l < "$LOG_FILE")
    if [ "$line_count" -gt 3000 ]; then
        echo "Log file exceeded 3000 lines. Resetting log file." > "$LOG_FILE"
    fi
}

# Function to log with timestamps
log_with_timestamp() {
    check_log_file_size  # Check log file size before logging
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

# Function to kill processes running on port 8009
kill_port_8009() {
    log_with_timestamp "Killing any process using port 8009..."
    pids=$(lsof -t -i:8009)
    if [ -n "$pids" ]; then
        for pid in $pids; do
            kill -9 "$pid" && log_with_timestamp "Successfully killed process $pid on port 8009." || log_with_timestamp "Failed to kill process $pid on port 8009."
        done
    else
        log_with_timestamp "No process found on port 8009."
    fi
}

# Restart the application
restart_application() {
    log_with_timestamp "Restarting the application."

    cd /home/hello/project/stream_camera || {
        log_with_timestamp "Failed to access project directory."
        exit 1
    }

    # Activate Python virtual environment
    source camera_ai_env/bin/activate || {
        log_with_timestamp "Failed to activate Python virtual environment."
        exit 1
    }

    # Load nvm and use Node.js version 18
    source /home/hello/.nvm/nvm.sh || {
        log_with_timestamp "Failed to load nvm."
        exit 1
    }
    nvm use 18 || {
        log_with_timestamp "Failed to use Node.js version 18."
        exit 1
    }
    log_with_timestamp "before start application"
    # Start the application with pm2
    /home/hello/.nvm/versions/node/v18.18.2/bin/pm2 start ecosystem.config.js || {
        log_with_timestamp "Failed to start the application with pm2."
        exit 1
    }
    log_with_timestamp "before sleep"
    sleep 10
    log_with_timestamp "prepare sleep"
    response=$(curl -s -X 'GET' 'http://192.168.1.112:8009/camera_ai' -H 'accept: application/json')
    log_with_timestamp "after sleep"

    log_with_timestamp "Application started successfully...."
}

# Execute the script
kill_port_8009
restart_application
