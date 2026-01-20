# settings_manager.py - Manages reading and writing to YimMenu's settings.json.
import os
import json
import logging
import shutil
from paths import YIMMENU_SETTINGS_FILE_PATH, YIMMENUV2_SETTINGS_FILE_PATH

logger = logging.getLogger(__name__)

# 存储两个版本的文件路径
SETTINGS_FILE_PATHS = {
    "v1": YIMMENU_SETTINGS_FILE_PATH,
    "v2": YIMMENUV2_SETTINGS_FILE_PATH
}

class SettingsManager:
    """管理YimMenu设置的单例类，确保两个版本的设置完全独立"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SettingsManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._settings_cache = {
                "v1": None,
                "v2": None
            }
            self._last_modified = {
                "v1": 0,
                "v2": 0
            }
            self._initialized = True
    
    def _get_file_path(self, yim_version: str) -> str:
        """获取指定版本的设置文件路径"""
        version_key = "v2" if yim_version == "v2" else "v1"
        return SETTINGS_FILE_PATHS[version_key]
    
    def _read_json_safely(self, file_path: str):
        """安全读取JSON文件，处理BOM或损坏"""
        if not os.path.exists(file_path):
            return {}
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            logger.warning(f"Failed to read {file_path}: {e}")
            return {}
    
    def _write_json_safely(self, file_path: str, data: dict, version: str) -> bool:
        """安全写入JSON文件"""
        temp_file = file_path + ".tmp"
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
            
            shutil.move(temp_file, file_path)
            
            # 更新缓存和修改时间
            self._settings_cache[version] = data
            self._last_modified[version] = os.path.getmtime(file_path)
            
            logger.info(f"Successfully wrote to {file_path}")
            return True
        except OSError as e:
            logger.error(f"Failed to write settings file {file_path}: {e}")
            return False
    
    def _get_settings_with_cache(self, yim_version: str) -> dict:
        """使用缓存获取设置，避免频繁读取文件"""
        version_key = "v2" if yim_version == "v2" else "v1"
        file_path = self._get_file_path(yim_version)
        
        # 如果文件不存在，返回空字典
        if not os.path.exists(file_path):
            return {}
        
        try:
            # 检查文件是否已被修改
            current_mtime = os.path.getmtime(file_path)
            
            # 如果缓存为空或文件已被修改，重新读取
            if (self._settings_cache[version_key] is None or 
                self._last_modified[version_key] != current_mtime):
                self._settings_cache[version_key] = self._read_json_safely(file_path)
                self._last_modified[version_key] = current_mtime
            
            return self._settings_cache[version_key]
        except OSError:
            return {}
    
    def get_setting(self, key_path: str, default=None, yim_version: str = "v1"):
        """
        读取嵌套设置
        
        Args:
            key_path: 设置键路径，如 "lua.auto_reload_changed_scripts"
            default: 默认值
            yim_version: YimMenu版本，可选 "v1" 或 "v2"
        """
        data = self._get_settings_with_cache(yim_version)
        
        keys = key_path.split(".")
        value = data
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def set_setting(self, key_path: str, value, yim_version: str = "v1") -> bool:
        """
        写入嵌套设置，确保父键存在
        
        Args:
            key_path: 设置键路径，如 "lua.auto_reload_changed_scripts"
            value: 要设置的值
            yim_version: YimMenu版本，可选 "v1" 或 "v2"
        """
        version_key = "v2" if yim_version == "v2" else "v1"
        file_path = self._get_file_path(yim_version)
        
        # 获取当前设置
        data = self._get_settings_with_cache(yim_version)
        
        # 遍历并设置嵌套键
        keys = key_path.split(".")
        d = data
        try:
            for i, key in enumerate(keys[:-1]):
                if key not in d or not isinstance(d[key], dict):
                    d[key] = {}
                d = d[key]
            
            d[keys[-1]] = value
        except Exception as e:
            logger.error(f"Error traversing settings dict for {yim_version}: {e}")
            return False
        
        # 写入文件并更新缓存
        return self._write_json_safely(file_path, data, version_key)
    
    def ensure_settings_file_exists(self, yim_version: str = "v1"):
        """
        确保设置文件存在，如果不存在则创建一个默认的
        
        Args:
            yim_version: YimMenu版本，可选 "v1" 或 "v2"
        """
        file_path = self._get_file_path(yim_version)
        
        if not os.path.exists(file_path):
            # 版本特定的默认设置
            default_settings = {
                "lua": {
                    "auto_reload_scripts": False,
                    "auto_reload_changed_scripts": False
                },
                "debug": {
                    "external_console": False
                },
                "theme": {
                    "light_mode": False
                }
            }
            
            # 创建默认设置文件
            version_key = "v2" if yim_version == "v2" else "v1"
            success = self._write_json_safely(file_path, default_settings, version_key)
            if success:
                logger.info(f"Created default settings file for YimMenu {yim_version} at {file_path}")
            else:
                logger.error(f"Failed to create default settings file for YimMenu {yim_version}")
    
    # ===== 特定功能设置方法 =====
    
    def get_auto_reload_changed_scripts(self, yim_version: str = "v1") -> bool:
        """
        获取指定版本的 Auto-reload changed scripts 设置
        
        注意：这个方法只读取 auto_reload_changed_scripts 设置，
        与 auto_reload_scripts 完全独立
        """
        return self.get_setting(
            "lua.auto_reload_changed_scripts", 
            default=False, 
            yim_version=yim_version
        )
    
    def set_auto_reload_changed_scripts(self, value: bool, yim_version: str = "v1") -> bool:
        """
        设置指定版本的 Auto-reload changed scripts 设置
        
        注意：这个方法只设置 auto_reload_changed_scripts，
        不影响 auto_reload_scripts 设置
        """
        return self.set_setting(
            "lua.auto_reload_changed_scripts", 
            value, 
            yim_version=yim_version
        )
    
    def get_auto_reload_scripts(self, yim_version: str = "v1") -> bool:
        """
        获取指定版本的 Auto-reload scripts 设置
        """
        return self.get_setting(
            "lua.auto_reload_scripts", 
            default=False, 
            yim_version=yim_version
        )
    
    def set_auto_reload_scripts(self, value: bool, yim_version: str = "v1") -> bool:
        """
        设置指定版本的 Auto-reload scripts 设置
        """
        return self.set_setting(
            "lua.auto_reload_scripts", 
            value, 
            yim_version=yim_version
        )
    
    # ===== 独立版本管理方法 =====
    
    def get_both_auto_reload_settings(self):
        """
        获取两个版本的 Auto-reload changed scripts 设置
        
        Returns:
            dict: 包含两个版本设置的字典
        """
        return {
            "v1": self.get_auto_reload_changed_scripts("v1"),
            "v2": self.get_auto_reload_changed_scripts("v2")
        }
    
    def set_both_auto_reload_settings(self, v1_value: bool, v2_value: bool) -> bool:
        """
        分别设置两个版本的 Auto-reload changed scripts 设置
        
        Returns:
            bool: 两个设置都成功返回True，否则返回False
        """
        success_v1 = self.set_auto_reload_changed_scripts(v1_value, "v1")
        success_v2 = self.set_auto_reload_changed_scripts(v2_value, "v2")
        return success_v1 and success_v2
    
    def sync_auto_reload_settings(self, source_version: str = "v1", target_version: str = "v2") -> bool:
        """
        将一个版本的 Auto-reload 设置同步到另一个版本
        
        Args:
            source_version: 源版本 ("v1" 或 "v2")
            target_version: 目标版本 ("v1" 或 "v2")
            
        Returns:
            bool: 同步成功返回True，否则返回False
        """
        if source_version == target_version:
            logger.warning("Source and target versions are the same, no sync needed")
            return True
        
        value = self.get_auto_reload_changed_scripts(source_version)
        return self.set_auto_reload_changed_scripts(value, target_version)


# ===== 全局单例实例 =====
settings_manager = SettingsManager()

# ===== 兼容性函数（保持接口一致） =====

def get_setting(key_path: str, default=None, yim_version: str = "v1"):
    """兼容性函数，使用设置管理器"""
    return settings_manager.get_setting(key_path, default, yim_version)

def set_setting(key_path: str, value, yim_version: str = "v1") -> bool:
    """兼容性函数，使用设置管理器"""
    return settings_manager.set_setting(key_path, value, yim_version)

def ensure_settings_file_exists(yim_version: str = "v1"):
    """兼容性函数，使用设置管理器"""
    return settings_manager.ensure_settings_file_exists(yim_version)

def get_auto_reload_setting(yim_version: str = "v1") -> bool:
    """兼容性函数，获取 Auto-reload 设置（注意：这个函数可能会同时影响两个设置）"""
    # 为了向后兼容，这里返回 auto_reload_changed_scripts 的值
    return settings_manager.get_auto_reload_changed_scripts(yim_version)

def set_auto_reload_setting(value: bool, yim_version: str = "v1") -> bool:
    """兼容性函数，设置 Auto-reload 设置（注意：这个函数可能会同时设置两个值）"""
    # 为了向后兼容，同时设置两个键
    success1 = settings_manager.set_setting("lua.auto_reload_scripts", value, yim_version=yim_version)
    success2 = settings_manager.set_setting("lua.auto_reload_changed_scripts", value, yim_version=yim_version)
    return success1 and success2

# ===== 独立功能函数 =====

def get_auto_reload_changed_scripts(yim_version: str = "v1") -> bool:
    """独立获取 Auto-reload changed scripts 设置"""
    return settings_manager.get_auto_reload_changed_scripts(yim_version)

def set_auto_reload_changed_scripts(value: bool, yim_version: str = "v1") -> bool:
    """独立设置 Auto-reload changed scripts 设置"""
    return settings_manager.set_auto_reload_changed_scripts(value, yim_version)