import os
import glob

def get_available_action_groups():
    """Get list of available action groups from ./action_groups directory.
    
    Returns:
        list: List of action group names (without .d6a extension)
    """
    pattern = os.path.join("action_groups", "*.d6a")
    files = glob.glob(pattern)
    return [os.path.splitext(os.path.basename(f))[0] for f in files]