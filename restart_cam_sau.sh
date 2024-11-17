LOG_FILE="/home/hello/project/dem_xe_be/cron_error_restart_be.log"

# Function to check and reset log file if it exceeds 5000 lines
check_log_file_size() {
    line_count=$(wc -l < "$LOG_FILE")
    if [ "$line_count" -gt 5000 ]; then
        echo "callhere"
        # Reset log file if line count exceeds 5000
        echo "Log file exceeded 5000 lines. Resetting log file." > "$LOG_FILE"
    fi
}

# Function to log with timestamps
log_with_timestamp() {
    check_log_file_size  # Kiểm tra log file mỗi lần log
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

# Function to restart the "be" application using pm2
restart_be() {
    log_with_timestamp "Restarting the 'be' application using pm2."

    source /home/hello/.nvm/nvm.sh || exit 1  # Load nvm
    
    # Restart the 'be' application (it assumes 'be' is the name or id of your pm2 app)
    /home/hello/.nvm/versions/node/v18.18.2/bin/pm2 restart camera_ai_sau || exit 1

    # Optionally, you can ensure it's restarted correctly, or do any additional checks
    log_with_timestamp "'be' application has been restarted."

    # If you need to start it fresh after restart
    # /home/hello/.nvm/versions/node/v18.18.2/bin/pm2 restart /home/hello/project/stream_camera/ecosystem.config.js || exit 1
    log_with_timestamp "'be' application started successfully."
}

# Example usage:
# Call the restart_be function whenever you need to restart the 'be' application
restart_be
