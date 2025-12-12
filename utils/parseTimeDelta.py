from datetime import timedelta
from typing import Optional
import re
import os
import sys

def parse_time_delta_string(time_str: str) -> timedelta:
    """
    Parses a string like '1h', '3d', '1M', '1Y' into a datetime.timedelta object.
    
    NOTE: 'M' (Month) and 'Y' (Year) are converted to approximate days (30 and 365).
    
    Args:
        time_str: The string representation of the time delta (e.g., '24h', '7d', '1M').
        
    Returns:
        A datetime.timedelta object.
        
    Raises:
        ValueError: If the string format or unit is invalid.
    
    (AI)
    """
    # Regex extended to include 'M' (month) and 'Y' (year)
    match = re.fullmatch(r'(\d+)\s*([hdwmsy])', time_str.lower().strip())
    
    if not match:
        raise ValueError(
            f"Invalid time delta format: '{time_str}'. Expected format is '1d', '3h', '1M', '1Y', etc. "
            f"Units allowed: h(our), d(ay), w(eek), m(inute), s(econd), M(onth), Y(ear)."
        )
    
    value = int(match.group(1))
    unit = match.group(2)
    
    if unit == 'h':
        return timedelta(hours=value)
    elif unit == 'd':
        return timedelta(days=value)
    elif unit == 'w':
        return timedelta(weeks=value)
    elif unit == 'm':
        return timedelta(minutes=value)
    elif unit == 's':
        return timedelta(seconds=value)
    elif unit == 'M':
        # --- WARNING: Approximation for Months ---
        print("WARNING: 'M' (Month) is being approximated as 30 days.", file=sys.stderr)
        return timedelta(days=value * 30)
    elif unit == 'y':
        # --- WARNING: Approximation for Years ---
        print("WARNING: 'Y' (Year) is being approximated as 365 days.", file=sys.stderr)
        return timedelta(days=value * 365)
    else:
        # Should be caught by regex, but for safety
        raise ValueError(f"Invalid time unit: '{unit}'.")
    

def print_all_files_recursive(directory_path: str):
    """
    Prints the full path of all regular files within a given directory
    and its subdirectories.
    
    Args:
        directory_path: The root directory to start the recursive search from.

    (AI)
    """
    
    # Check if the provided path is a valid directory
    if not os.path.isdir(directory_path):
        print(f"Error: '{directory_path}' is not a valid directory.", file=sys.stderr)
        return

    print(f"--- Files in: {directory_path} ---")
    
    # os.walk() is a generator that yields a 3-tuple for each directory:
    # (root, dirs, files)
    for root, _, files in os.walk(directory_path):
        # 'files' is a list of filenames (not full paths) in the current 'root' directory
        
        for filename in files:
            # os.path.join correctly combines the root directory with the filename 
            # using the OS-appropriate separator (e.g., / or \)
            full_file_path = os.path.join(root, filename)
            print(full_file_path)