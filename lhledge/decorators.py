"""
Custom decorators for the project.

This file contains decorators (wrappers) to log some important
events and variables of the process
"""

from functools import wraps
import time

def log_time_elapsed(func):
    """https://calmcode.io/decorators/optional-inputs.html"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        tic = time.time()
        result = func(*args, **kwargs)
        time_taken = time.time() - tic
        print(f"It took {time_taken:.2f}")
        return result
    return wrapper
