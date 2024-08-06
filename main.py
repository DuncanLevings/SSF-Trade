import logging
from multiprocessing import Process, Queue, set_start_method, freeze_support
from capture import key_listener
from parse_capture import parse_copied_content
import uvicorn
import webbrowser
import time
import requests
import os
import sys
from pathlib import Path
import signal

logging.basicConfig(level=logging.INFO)

def run_fastapi_app():
    uvicorn.run("app:app", host="127.0.0.1", port=8000)

def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return Path(sys._MEIPASS) / relative_path
    return Path(__file__).parent / relative_path

def terminate_processes(processes):
    for process in processes:
        logging.info(f"Terminating process {process.pid}")
        process.terminate()
        process.join()

def signal_handler(sig, frame):
    logging.info("Signal received, shutting down processes...")
    terminate_processes(processes)
    sys.exit(0)

if __name__ == "__main__":
    freeze_support()
    set_start_method("spawn")
    logging.info("Starting processes...")

    queue = Queue()

    listener_process = Process(target=key_listener, args=(queue,))
    parser_process = Process(target=parse_copied_content, args=(queue,))
    fastapi_process = Process(target=run_fastapi_app)

    processes = [listener_process, parser_process, fastapi_process]

    for process in processes:
        process.start()

    logging.info("Opening web browser...")
    webbrowser.open('http://127.0.0.1:8000')

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        for process in processes:
            process.join()
    except KeyboardInterrupt:
        logging.info("Keyboard interrupt received, shutting down processes...")
        terminate_processes(processes)
        logging.info("Processes terminated.")
