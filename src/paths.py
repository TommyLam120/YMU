# paths.py - Defines, creates, and manages all application file paths.
import os
import sys

LOCAL_VERSION = "v1.1.7"
APP_URL = "https://github.com/tommylam120/YMU"
USER_AGENT = f"YMU/{LOCAL_VERSION} (+{APP_URL})"


def get_required_env(env_var: str) -> str:
    """Gets an environment variable that is required for the app to run."""
    value = os.getenv(env_var)
    if value is None:
        raise EnvironmentError(f"Required environment variable '{env_var}' is not set.")
    return value


def _create_path(path: str) -> str:
    """Helper function to ensure a directory exists and return its absolute path."""
    os.makedirs(path, exist_ok=True)
    return os.path.abspath(path)


# Base paths
APPDATA_PATH = get_required_env("APPDATA")

# ========== YMU Application Paths ==========
YMU_APPDATA_DIR = _create_path(os.path.join(APPDATA_PATH, "YMU"))
YMU_DLL_DIR = _create_path(os.path.join(YMU_APPDATA_DIR, "dll"))
YMU_LANG_DIR = _create_path(os.path.join(YMU_APPDATA_DIR, "lang"))
YMU_LOG_FILE_PATH = os.path.join(YMU_APPDATA_DIR, "ymu.log")
YMU_CONFIG_FILE_PATH = os.path.join(YMU_APPDATA_DIR, "config.json")

# ========== YimMenu (Legacy v1) Paths ==========
YIMMENU_APPDATA_DIR = _create_path(os.path.join(APPDATA_PATH, "YimMenu"))
YIMMENU_SCRIPTS_DIR = _create_path(os.path.join(YIMMENU_APPDATA_DIR, "scripts"))
YIMMENU_DISABLED_SCRIPTS_DIR = _create_path(os.path.join(YIMMENU_SCRIPTS_DIR, "disabled"))
YIMMENU_SETTINGS_FILE_PATH = os.path.join(YIMMENU_APPDATA_DIR, "settings.json")

# ========== YimMenuV2 (Enhanced) Paths ==========
YIMMENUV2_APPDATA_DIR = _create_path(os.path.join(APPDATA_PATH, "YimMenuV2"))
YIMMENUV2_SCRIPTS_DIR = _create_path(os.path.join(YIMMENUV2_APPDATA_DIR, "scripts"))
YIMMENUV2_DISABLED_SCRIPTS_DIR = _create_path(os.path.join(YIMMENUV2_SCRIPTS_DIR, "disabled"))
YIMMENUV2_SETTINGS_FILE_PATH = os.path.join(YIMMENUV2_APPDATA_DIR, "settings.json")

# ========== Helper Functions ==========
def get_yimmenu_paths(version: str = "v1") -> dict:
    """
    Get all paths for a specific YimMenu version.
    
    Args:
        version: "v1" for YimMenu (legacy), "v2" for YimMenuV2 (enhanced)
        
    Returns:
        Dictionary with all paths for the specified version
    """
    if version.lower() == "v2":
        return {
            "appdata_dir": YIMMENUV2_APPDATA_DIR,
            "scripts_dir": YIMMENUV2_SCRIPTS_DIR,
            "disabled_dir": YIMMENUV2_DISABLED_SCRIPTS_DIR,
            "settings_file": YIMMENUV2_SETTINGS_FILE_PATH
        }
    else:
        return {
            "appdata_dir": YIMMENU_APPDATA_DIR,
            "scripts_dir": YIMMENU_SCRIPTS_DIR,
            "disabled_dir": YIMMENU_DISABLED_SCRIPTS_DIR,
            "settings_file": YIMMENU_SETTINGS_FILE_PATH
        }


def resource_path(relative_path: str) -> str:
    """
    Gets the absolute path to a resource.
    Works for:
    1. PyInstaller (_MEIPASS)
    2. Nuitka (sys.argv[0] dir or __file__)
    3. Normal Python Script
    
    Args:
        relative_path: Relative path to the resource
        
    Returns:
        Absolute path to the resource
    """
    try:
        # PyInstaller support
        if hasattr(sys, "_MEIPASS"):
            base_path = sys._MEIPASS
        else:
            # Try sys.argv[0] directory first
            base_path = os.path.dirname(os.path.abspath(sys.argv[0]))
            
            # If not found, try __file__ directory
            if not os.path.exists(os.path.join(base_path, relative_path)):
                base_path = os.path.dirname(os.path.abspath(__file__))
        
        full_path = os.path.join(base_path, relative_path)
        return os.path.normpath(full_path)
        
    except Exception as e:
        print(f"Error getting resource path for '{relative_path}': {e}")
        # Fallback to current directory
        return os.path.normpath(os.path.join(os.getcwd(), relative_path))


# ========== Version Information ==========
def get_version_info() -> dict:
    """Get version information for all components."""
    return {
        "ymu_version": LOCAL_VERSION,
        "app_url": APP_URL,
        "user_agent": USER_AGENT,
        "yimmenu_v1_path": YIMMENU_APPDATA_DIR,
        "yimmenu_v2_path": YIMMENUV2_APPDATA_DIR,
        "ymu_path": YMU_APPDATA_DIR
    }


def print_paths() -> None:
    """Print all paths for debugging purposes."""
    print("=" * 60)
    print("YMU Paths:")
    print("=" * 60)
    print(f"YMU AppData: {YMU_APPDATA_DIR}")
    print(f"YMU DLL Dir: {YMU_DLL_DIR}")
    print(f"YMU Lang Dir: {YMU_LANG_DIR}")
    print(f"YMU Log File: {YMU_LOG_FILE_PATH}")
    print(f"YMU Config: {YMU_CONFIG_FILE_PATH}")
    print()
    
    print("=" * 60)
    print("YimMenu (v1) Paths:")
    print("=" * 60)
    print(f"AppData: {YIMMENU_APPDATA_DIR}")
    print(f"Scripts: {YIMMENU_SCRIPTS_DIR}")
    print(f"Disabled: {YIMMENU_DISABLED_SCRIPTS_DIR}")
    print(f"Settings: {YIMMENU_SETTINGS_FILE_PATH}")
    print()
    
    print("=" * 60)
    print("YimMenuV2 (v2) Paths:")
    print("=" * 60)
    print(f"AppData: {YIMMENUV2_APPDATA_DIR}")
    print(f"Scripts: {YIMMENUV2_SCRIPTS_DIR}")
    print(f"Disabled: {YIMMENUV2_DISABLED_SCRIPTS_DIR}")
    print(f"Settings: {YIMMENUV2_SETTINGS_FILE_PATH}")
    print("=" * 60)


# Test if running directly
if __name__ == "__main__":
    print_paths()
    print("\nVersion Info:")
    print(get_version_info())