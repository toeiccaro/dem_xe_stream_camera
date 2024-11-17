#!/bin/bash

LOG_FILE="/home/hello/project/stream_camera/check_cam_sau.log"

# Function to check and reset log file if it exceeds 5000 lines
check_log_file_size() {
    line_count=$(wc -l < "$LOG_FILE")
    if [ "$line_count" -gt 3000 ]; then
        echo "Log file exceeded 5000 lines. Resetting log file." > "$LOG_FILE"
    fi
}

# Function to log with timestamps
log_with_timestamp() {
    check_log_file_size  # Kiểm tra log file mỗi lần log
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

# Function to check if port 8000 is listening
check_port_8009() {
    if ! nc -z 192.168.1.112 8009; then
        log_with_timestamp "Port 8009 is not listening. Starting the application with pm2."

        cd /
        # Change directory to the project folder
        cd /home/hello/project/stream_camera || exit 1  # Ensure the script stops if the directory can't be accessed

        # Activate the Python virtual environment
        source camera_ai_env/bin/activate || exit 1  # Exit if the virtual environment can't be activated

        source /home/hello/.nvm/nvm.sh || exit 1  # Load nvm

        # Use the specific node version (adjust to the version you need)
        nvm use 18 || exit 1  # Ensure you're using the right node version (adjust as necessary)

        node -v
        # Start the application with pm2
        /home/hello/.nvm/versions/node/v18.18.2/bin/pm2 start /home/hello/project/stream_camera/ecosystem.config.js  || exit 1  # Ensure pm2 starts correctly

        sleep 15
        response=$(curl -s -X 'GET' 'http://192.168.1.112:8009/camera_ai' -H 'accept: application/json')

    else
        log_with_timestamp "Port 8009 is already listening."
    fi
}

# Check if port 8000 is listening
check_port_8009

