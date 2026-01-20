# lua_manager.py - Handles enabling and disabling of Lua scripts by moving files.
import os
import shutil
import logging
from typing import Dict, List
from paths import (
    YIMMENU_APPDATA_DIR, 
    YIMMENU_SCRIPTS_DIR, 
    YIMMENU_DISABLED_SCRIPTS_DIR,
    YIMMENUV2_APPDATA_DIR,  # 新增
    YIMMENUV2_SCRIPTS_DIR,   # 新增
)

logger = logging.getLogger(__name__)

# Legacy paths for YimMenu v1
YIM_FOLDER_PATH = YIMMENU_APPDATA_DIR
SCRIPTS_PATH = YIMMENU_SCRIPTS_DIR
DISABLED_SCRIPTS_PATH = YIMMENU_DISABLED_SCRIPTS_DIR

# New paths for YimMenuV2
YIMV2_FOLDER_PATH = YIMMENUV2_APPDATA_DIR
SCRIPTS_PATH_V2 = YIMMENUV2_SCRIPTS_DIR
DISABLED_SCRIPTS_PATH_V2 = os.path.join(YIMMENUV2_SCRIPTS_DIR, "disabled")


def _get_lua_files(directory: str) -> List[str]:
    """Helper function to find all .lua files in a directory."""
    if not os.path.isdir(directory):
        return []

    return [
        f
        for f in os.listdir(directory)
        if f.endswith(".lua") and os.path.isfile(os.path.join(directory, f))
    ]


def get_scripts(version: str = "v1") -> Dict[str, List[str]]:
    """
    Returns a dictionary with lists of enabled and disabled lua scripts,
    with the '.lua' suffix removed for display.
    
    Args:
        version: "v1" for YimMenu (legacy), "v2" for YimMenuV2 (enhanced)
    """
    if version == "v2":
        scripts_dir = SCRIPTS_PATH_V2
        disabled_dir = DISABLED_SCRIPTS_PATH_V2
        logger.debug(f"Getting scripts for YimMenuV2 from {scripts_dir}")
    else:
        scripts_dir = SCRIPTS_PATH
        disabled_dir = DISABLED_SCRIPTS_PATH
        logger.debug(f"Getting scripts for YimMenu v1 from {scripts_dir}")
    
    # Ensure directories exist
    os.makedirs(scripts_dir, exist_ok=True)
    os.makedirs(disabled_dir, exist_ok=True)

    enabled_scripts_full = _get_lua_files(scripts_dir)
    disabled_scripts_full = _get_lua_files(disabled_dir)

    enabled_display = [s.removesuffix(".lua") for s in sorted(enabled_scripts_full)]
    disabled_display = [s.removesuffix(".lua") for s in sorted(disabled_scripts_full)]

    logger.debug(f"Found enabled scripts ({version}): {enabled_display}")
    logger.debug(f"Found disabled scripts ({version}): {disabled_display}")

    return {"enabled": enabled_display, "disabled": disabled_display}


def enable_script(filename: str, version: str = "v1") -> bool:
    """
    Moves a script from the 'disabled' folder to the 'scripts' folder.
    
    Args:
        filename: Name of the script without .lua extension
        version: "v1" for YimMenu (legacy), "v2" for YimMenuV2 (enhanced)
    """
    if version == "v2":
        scripts_dir = SCRIPTS_PATH_V2
        disabled_dir = DISABLED_SCRIPTS_PATH_V2
    else:
        scripts_dir = SCRIPTS_PATH
        disabled_dir = DISABLED_SCRIPTS_PATH
    
    actual_filename = f"{filename}.lua"

    src = os.path.join(disabled_dir, actual_filename)
    dest = os.path.join(scripts_dir, actual_filename)

    if not os.path.exists(src):
        logger.error(
            f"Cannot enable script '{actual_filename}' for {version}, it does not exist in the disabled folder."
        )
        return False

    try:
        # Ensure destination directory exists
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        
        shutil.move(src, dest)
        logger.info(f"Enabled script {actual_filename} for {version}")
        return True
    except (IOError, OSError) as e:
        logger.exception(f"Error enabling script {actual_filename} for {version}: {e}")
        return False


def disable_script(filename: str, version: str = "v1") -> bool:
    """
    Moves a script from the 'scripts' folder to the 'disabled' folder.
    
    Args:
        filename: Name of the script without .lua extension
        version: "v1" for YimMenu (legacy), "v2" for YimMenuV2 (enhanced)
    """
    if version == "v2":
        scripts_dir = SCRIPTS_PATH_V2
        disabled_dir = DISABLED_SCRIPTS_PATH_V2
    else:
        scripts_dir = SCRIPTS_PATH
        disabled_dir = DISABLED_SCRIPTS_PATH
    
    actual_filename = f"{filename}.lua"

    src = os.path.join(scripts_dir, actual_filename)
    dest = os.path.join(disabled_dir, actual_filename)

    if not os.path.exists(src):
        logger.error(
            f"Cannot disable script '{actual_filename}' for {version}, it does not exist in the scripts folder."
        )
        return False

    try:
        # Ensure destination directory exists
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        
        shutil.move(src, dest)
        logger.info(f"Disabled script {actual_filename} for {version}")
        return True
    except (IOError, OSError) as e:
        logger.exception(f"Error disabling script {actual_filename} for {version}: {e}")
        return False


# Legacy functions for backward compatibility (default to v1)
def get_scripts_v1() -> Dict[str, List[str]]:
    """Get scripts for YimMenu v1 (legacy)"""
    return get_scripts("v1")


def enable_script_v1(filename: str) -> bool:
    """Enable script for YimMenu v1 (legacy)"""
    return enable_script(filename, "v1")


def disable_script_v1(filename: str) -> bool:
    """Disable script for YimMenu v1 (legacy)"""
    return disable_script(filename, "v1")


# New functions for YimMenuV2
def get_scripts_v2() -> Dict[str, List[str]]:
    """Get scripts for YimMenuV2 (enhanced)"""
    return get_scripts("v2")


def enable_script_v2(filename: str) -> bool:
    """Enable script for YimMenuV2 (enhanced)"""
    return enable_script(filename, "v2")


def disable_script_v2(filename: str) -> bool:
    """Disable script for YimMenuV2 (enhanced)"""
    return disable_script(filename, "v2")


# Convenience function to get script paths for both versions
def get_script_paths(version: str = "v1") -> Dict[str, str]:
    """
    Get all script-related paths for a specific YimMenu version.
    
    Args:
        version: "v1" for YimMenu (legacy), "v2" for YimMenuV2 (enhanced)
        
    Returns:
        Dictionary with paths
    """
    if version == "v2":
        return {
            "appdata_dir": YIMV2_FOLDER_PATH,
            "scripts_dir": SCRIPTS_PATH_V2,
            "disabled_dir": DISABLED_SCRIPTS_PATH_V2
        }
    else:
        return {
            "appdata_dir": YIM_FOLDER_PATH,
            "scripts_dir": SCRIPTS_PATH,
            "disabled_dir": DISABLED_SCRIPTS_PATH
        }


# Function to copy scripts between versions
def copy_script_between_versions(filename: str, from_version: str, to_version: str, enabled: bool = True) -> bool:
    """
    Copy a script from one YimMenu version to another.
    
    Args:
        filename: Script filename without .lua extension
        from_version: Source version ("v1" or "v2")
        to_version: Destination version ("v1" or "v2")
        enabled: Whether to copy to enabled folder (True) or disabled folder (False)
        
    Returns:
        True if successful, False otherwise
    """
    if from_version not in ["v1", "v2"] or to_version not in ["v1", "v2"]:
        logger.error(f"Invalid version: from={from_version}, to={to_version}")
        return False
    
    actual_filename = f"{filename}.lua"
    
    # Get source paths
    from_paths = get_script_paths(from_version)
    if enabled:
        src_dir = from_paths["scripts_dir"]
    else:
        src_dir = from_paths["disabled_dir"]
    src = os.path.join(src_dir, actual_filename)
    
    # Get destination paths
    to_paths = get_script_paths(to_version)
    if enabled:
        dest_dir = to_paths["scripts_dir"]
    else:
        dest_dir = to_paths["disabled_dir"]
    dest = os.path.join(dest_dir, actual_filename)
    
    # Check if source exists
    if not os.path.exists(src):
        logger.error(f"Script '{actual_filename}' not found in {from_version}")
        return False
    
    try:
        # Ensure destination directory exists
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        
        # Copy the file
        shutil.copy2(src, dest)
        logger.info(f"Copied script '{actual_filename}' from {from_version} to {to_version}")
        return True
        
    except (IOError, OSError) as e:
        logger.exception(f"Error copying script '{actual_filename}' from {from_version} to {to_version}: {e}")
        return False