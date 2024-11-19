import threading
import time

# Flag to stop the background task
stop_thread = False

# Function to run in the background
def background_task():
    global stop_thread
    while not stop_thread:
        print("Background task is running...")
        time.sleep(1)
    print("Background task stopped.")

# Function to start the background task
def start_background_task():
    global stop_thread
    stop_thread = False  # Ensure stop flag is reset
    thread = threading.Thread(target=background_task)
    thread.daemon = True  # Daemonize the thread so it exits when the main program exits
    thread.start()

# Function to stop the background task
def stop_background_task():
    global stop_thread
    stop_thread = True
    print("Stop signal sent to background task.")

# Example usage
if __name__ == "__main__":
    # Start the background task
    start_background_task()

    # Let the background task run for a while
    time.sleep(5)

    # Stop the background task
    stop_background_task()
    
    # Sleep for a short time to allow the background task to stop
    time.sleep(1)
