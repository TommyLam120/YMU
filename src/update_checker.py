import release_service
import subprocess
import logging
import sys
import os
import tempfile
import shutil
import requests
import json
from paths import YMU_APPDATA_DIR, LOCAL_VERSION

logger = logging.getLogger(__name__)

REPO = "tommylam120/YMU"
UPDATER_REPO = "tommylam120/YMU-Updater"
# 確保 YMU_APPDATA_DIR 存在
os.makedirs(YMU_APPDATA_DIR, exist_ok=True)
UPDATER_EXE_PATH = os.path.join(YMU_APPDATA_DIR, "ymu_self_updater.exe")

_update_cache = {}
CACHE_DURATION_SECONDS = 300

# --- STATUS CONSTANTS ---
STATUS_ERROR = "ERROR"
STATUS_UPDATE_AVAILABLE = "UPDATE_AVAILABLE"
STATUS_UP_TO_DATE = "UP_TO_DATE"
STATUS_AHEAD = "AHEAD"


def check_for_updates(*args, **kwargs):
    """
    Returns tuple: (STATUS_CODE, DATA)
    DATA is either the remote version string or the error message/object.
    """
    import time
    from packaging.version import parse

    current_time = time.time()

    if REPO in _update_cache:
        cached_data, timestamp = _update_cache[REPO]
        if (current_time - timestamp) < CACHE_DURATION_SECONDS:
            return cached_data

    logger.info("Checking for YMU updates...")
    try:
        provider = release_service.GitHubAPIProvider(
            repository=REPO, asset_extension=".exe"
        )
        latest_release = provider.get_latest_release()

        if not latest_release:
            return (STATUS_ERROR, "Could not fetch release info")

        remote_version = latest_release.version_tag

        local = parse(LOCAL_VERSION)
        remote = parse(remote_version)

        result = None
        if remote > local:
            result = (STATUS_UPDATE_AVAILABLE, remote_version)
        elif remote == local:
            result = (STATUS_UP_TO_DATE, remote_version)
        else:
            result = (STATUS_AHEAD, remote_version)

        _update_cache[REPO] = (result, current_time)
        return result

    except Exception as e:
        logger.exception(f"Update check failed: {e}")
        return (STATUS_ERROR, str(e))


def download_updater_directly(progress_signal=None):
    """
    直接從 GitHub 下載 updater，不使用 release_service
    """
    logger.info(f"Directly downloading updater from {UPDATER_REPO}")
    
    try:
        # 直接獲取 latest 發布的信息
        api_url = f"https://api.github.com/repos/{UPDATER_REPO}/releases/latest"
        
        # 添加 User-Agent 頭部
        headers = {
            "User-Agent": "YMU-Updater",
            "Accept": "application/vnd.github.v3+json"
        }
        
        response = requests.get(api_url, headers=headers, timeout=30)
        response.raise_for_status()
        
        release_data = response.json()
        
        # 尋找 ymu_self_updater.exe
        asset_url = None
        for asset in release_data.get("assets", []):
            if asset["name"] == "ymu_self_updater.exe":
                asset_url = asset["browser_download_url"]
                break
        
        if not asset_url:
            # 如果沒有找到，嘗試下載第一個 asset
            if release_data.get("assets"):
                asset_url = release_data["assets"][0]["browser_download_url"]
            else:
                return False, "No assets found in the latest release"
        
        # 下載文件
        logger.info(f"Downloading updater from: {asset_url}")
        download_response = requests.get(asset_url, headers=headers, stream=True, timeout=60)
        download_response.raise_for_status()
        
        # 獲取文件總大小
        total_size = int(download_response.headers.get('content-length', 0))
        
        # 下載到臨時文件
        temp_path = UPDATER_EXE_PATH + ".tmp"
        
        with open(temp_path, 'wb') as f:
            downloaded = 0
            for chunk in download_response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    # 更新進度（如果提供了信號）
                    if progress_signal and total_size > 0:
                        progress = int((downloaded / total_size) * 100)
                        progress_signal.emit(progress)
        
        # 下載完成後替換原文件
        if os.path.exists(UPDATER_EXE_PATH):
            os.remove(UPDATER_EXE_PATH)
        
        shutil.move(temp_path, UPDATER_EXE_PATH)
        
        # 驗證文件
        if not os.path.exists(UPDATER_EXE_PATH):
            return False, "Downloaded file not found"
        
        file_size = os.path.getsize(UPDATER_EXE_PATH)
        if file_size == 0:
            return False, "Downloaded file is empty"
        
        logger.info(f"Updater downloaded successfully: {UPDATER_EXE_PATH} ({file_size} bytes)")
        return True, "Updater downloaded successfully"
        
    except requests.RequestException as e:
        logger.exception(f"Failed to download updater: {e}")
        return False, f"Network error: {str(e)}"
    except Exception as e:
        logger.exception(f"Unexpected error downloading updater: {e}")
        return False, f"Download error: {str(e)}"


def download_and_launch_updater(progress_signal=None, *args, **kwargs):
    """
    Downloads updater, passes sys.executable to it.
    """
    logger.info(f"Downloading and launching updater from {UPDATER_REPO}")
    
    # 先嘗試使用 release_service，如果失敗則使用直接下載
    use_direct_download = True  # 設置為 True 直接使用我們的新方法
    
    if not use_direct_download:
        try:
            logger.info("Attempting to download updater via release_service...")
            provider = release_service.GitHubAPIProvider(
                repository=UPDATER_REPO, asset_extension=".exe"
            )
            latest_release = provider.get_latest_release()

            if not latest_release:
                logger.warning("release_service failed, using direct download...")
                success, message = download_updater_directly(progress_signal)
            else:
                success = release_service.download_and_verify_release(
                    latest_release, progress_signal
                )
                message = "Downloaded via release_service" if success else "Failed via release_service"
        except Exception as e:
            logger.warning(f"release_service error: {e}, using direct download...")
            success, message = download_updater_directly(progress_signal)
    else:
        # 直接使用我們的新方法
        success, message = download_updater_directly(progress_signal)

    if not success:
        return (False, message)

    # 驗證文件
    if not os.path.exists(UPDATER_EXE_PATH):
        return (False, f"Updater file not found at: {UPDATER_EXE_PATH}")
    
    if os.path.getsize(UPDATER_EXE_PATH) < 1024:
        return (False, f"Updater file is too small: {os.path.getsize(UPDATER_EXE_PATH)} bytes")
    
    logger.info(f"Verifying updater file: {UPDATER_EXE_PATH}")
    
    # 在 Windows 上檢查 PE 文件標誌
    if sys.platform == "win32":
        try:
            with open(UPDATER_EXE_PATH, 'rb') as f:
                header = f.read(2)
                if header != b'MZ':
                    return (False, "Downloaded file is not a valid Windows executable")
        except Exception as e:
            logger.warning(f"Could not verify PE header: {e}")

    try:
        logger.info(f"Launching updater: {UPDATER_EXE_PATH}")
        current_exe = sys.executable
        
        # 確保當前執行文件路徑正確
        if not os.path.exists(current_exe):
            logger.warning(f"sys.executable not found: {current_exe}")
            # 嘗試使用 argv[0]
            if os.path.exists(sys.argv[0]):
                current_exe = sys.argv[0]
                logger.info(f"Using sys.argv[0] instead: {current_exe}")
        
        cmd = [UPDATER_EXE_PATH, current_exe]
        logger.info(f"Command: {cmd}")
        
        # 啟動 updater
        if sys.platform == "win32":
            # 在 Windows 上使用多種方式嘗試
            try:
                # 方法1: 使用 DETACHED_PROCESS
                subprocess.Popen(
                    cmd,
                    creationflags=subprocess.DETACHED_PROCESS,
                    close_fds=True,
                )
            except Exception as e1:
                logger.warning(f"Method 1 failed: {e1}, trying method 2...")
                try:
                    # 方法2: 使用 CREATE_NO_WINDOW
                    CREATE_NO_WINDOW = 0x08000000
                    subprocess.Popen(
                        cmd,
                        creationflags=CREATE_NO_WINDOW,
                    )
                except Exception as e2:
                    logger.warning(f"Method 2 failed: {e2}, trying method 3...")
                    try:
                        # 方法3: 簡單啟動
                        subprocess.Popen(cmd)
                    except Exception as e3:
                        logger.error(f"All methods failed: {e3}")
                        raise
        else:
            # 非 Windows 系統
            subprocess.Popen(cmd)

        logger.info("Updater launched successfully")
        return (True, "Updater launched successfully")
        
    except Exception as e:
        logger.exception(f"Failed to launch updater: {e}")
        
        # 提供詳細的錯誤信息
        error_details = f"Failed to launch updater: {str(e)}\n"
        error_details += f"Updater path: {UPDATER_EXE_PATH}\n"
        error_details += f"File exists: {os.path.exists(UPDATER_EXE_PATH)}\n"
        if os.path.exists(UPDATER_EXE_PATH):
            error_details += f"File size: {os.path.getsize(UPDATER_EXE_PATH)} bytes\n"
        error_details += f"Current exe: {current_exe}\n"
        error_details += f"Current exe exists: {os.path.exists(current_exe)}"
        
        return (False, error_details)


# 新增一個調試函數
def debug_updater_download():
    """調試函數：測試 updater 下載和啟動"""
    print("=== Debug Updater Download ===")
    print(f"YMU_APPDATA_DIR: {YMU_APPDATA_DIR}")
    print(f"UPDATER_EXE_PATH: {UPDATER_EXE_PATH}")
    print(f"Directory exists: {os.path.exists(YMU_APPDATA_DIR)}")
    
    # 測試直接下載
    print("\nTesting direct download...")
    success, message = download_updater_directly()
    print(f"Success: {success}")
    print(f"Message: {message}")
    
    if os.path.exists(UPDATER_EXE_PATH):
        print(f"File downloaded: {UPDATER_EXE_PATH}")
        print(f"File size: {os.path.getsize(UPDATER_EXE_PATH)} bytes")
        
        # 嘗試啟動
        print("\nTesting launch...")
        try:
            result = download_and_launch_updater()
            print(f"Launch result: {result}")
        except Exception as e:
            print(f"Launch failed: {e}")
    else:
        print("File not downloaded successfully")
    
    print("=== End Debug ===")


if __name__ == "__main__":
    # 如果直接運行此腳本，執行調試
    debug_updater_download()