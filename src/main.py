import tkinter as tk
from gui import ProcessorGUI
import logging
import os

# Set log file path to the same directory as the script
script_dir = os.path.dirname(os.path.abspath(__file__))
log_file_path = os.path.join(script_dir, 'processor.log')
print(f"Log file will be saved at: {log_file_path}")

# Configure logging with explicit file path and error handling
try:
    logging.basicConfig(
        filename=log_file_path,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logging.info("Logging initialized successfully")
except Exception as e:
    print(f"Failed to initialize logging: {str(e)}")

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = ProcessorGUI(root)
        root.mainloop()
    except Exception as e:
        print(f"Error starting application: {str(e)}")
        logging.error(f"Error starting application: {str(e)}")