import logging
import os

def get_log_file_path():
    """Get the path to the processor.log file."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, 'processor.log')