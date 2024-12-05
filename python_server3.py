import concurrent.futures
import os
import time
import psutil
import subprocess
import logging
import queue
import threading


logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[logging.FileHandler("local_service.log"), logging.StreamHandler()],
    )
logger = logging.getLogger("LocalService")


class ResourceManager:
    def __init__(self):
        self.threshold = 90

    def is_resource_available(self):
        cpu_usage = psutil.cpu_percent(interval=1)
        memory_usage = psutil.virtual_memory().percent
        logger.info(f"CPU Usage: {cpu_usage}%, Memory Usage: {memory_usage}%")
        return cpu_usage < self.threshold and memory_usage < self.threshold


class CommandProcessor:
    def __init__(self, folder_to_watch, resource_manager):
        self.folder_to_watch = folder_to_watch
        self.resource_manager = resource_manager
        self.command_queue = queue.Queue()
        self.running = True
        self.executor = concurrent.futures.ProcessPoolExecutor(max_workers=4)
        self.process_map = {}
        self.lock = threading.Lock()
        self.seen_files = set()


    def monitor_folder(self):
        while self.running:
            try:
                current_files = set(os.listdir(self.folder_to_watch))
                new_files = current_files - self.seen_files
                for file in new_files:
                    full_path = os.path.join(self.folder_to_watch, file)
                    if os.path.isfile(full_path):
                        with self.lock:
                            self.command_queue.put(full_path)
                            logger.info(f"File added to queue: {full_path}")
                        self.seen_files.add(file)
            except Exception as e:
                logger.error(f"Error while monitoring folder: {e}")
            time.sleep(1)

    def process_commands(self):
        while self.running:
            try:
                command_file = self.command_queue.get(timeout=1)
                
                print(f"Got command: {command_file}")
                with open(command_file, "r") as f:
                    command_line = f.read().strip()
                self.handle_command(command_line, command_file)
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error processing command file {command_file}: {e}")


    def handle_command(self, command_line, command_file):
        try:
            command, folder, filename = command_line.split()
            key = f"{folder}_{filename}"

            if command == "start":
                if key not in self.process_map:
                    if self.resource_manager.is_resource_available():
                        future = self.executor.submit(self.run_script, folder, filename)
                        self.process_map[key] = future
                        logger.info(f"Started processing: {folder}/{filename}")
                    else:
                        logger.warning("Resource unavailable. Cannot start processing.")
                else:
                    logger.info(f"Processing already running for: {folder}/{filename}")
            elif command == "stop":
                if key in self.process_map:
                    future = self.process_map[key]

                    if not future.cancel():
                        logger.warning(f"Could not stop {key}. It may already be running.")
                    else:
                        logger.info(f"Requested to stop {key}.")
                    
                    del self.process_map[key]
                else:
                    logger.info(f"No running process found for: {folder}/{filename}")
            
            os.remove(command_file)
            logger.info(f"Deleted command file: {command_file}")
        except ValueError:
            logger.error(f"Invalid command format: {command}")
        except Exception as e:
            logger.error(f"Error handling command: {e}")

    def run_script(self, folder, filename):
        print("script Running")
        script_path = "hello_world.py"
        command = ["python3.12", script_path, folder, filename]

        try:
            subprocess.run(command, check=True)
            logger.info(f"Script executed successfully with folder={folder} and file={filename}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Script execution failed: {e}")

    def stop(self):
        self.running = False
        self.executor.shutdown(wait=True)
        logger.info("Stopped processing service.")


def main():
    folder_to_watch = "files_to_process"
    os.makedirs(folder_to_watch, exist_ok=True)

    resource_manager = ResourceManager()
    processor = CommandProcessor(folder_to_watch, resource_manager)

    monitor_thread = threading.Thread(target=processor.monitor_folder)
    processor_thread = threading.Thread(target=processor.process_commands)

    monitor_thread.start()
    processor_thread.start()

    logger.info("Service started.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.warning("KeyboardInterrupt received. Stopping...")
        processor.stop()
        monitor_thread.join()
        processor_thread.join()

    logger.info("Service stopped.")

if __name__ == "__main__":
    main()
