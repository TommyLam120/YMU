> [!NOTE]
> **GTA V Enhanced Support Resolved**
>
> The detection issues regarding the "Enhanced" version of GTA V have been **fixed** in version **v1.1.7**. Please update to the latest version to ensure full compatibility.

## ✅ Safe & Secure

Your security is the top priority.

- **Clean Scan Results:** The application is regularly checked with VirusTotal to ensure it's free from threats.
- ~~**Microsoft SmartScreen:** YMU is recognized as a safe application, so you won't get any annoying warnings.~~ (v1.1.5 is whitelisted, v1.1.6 still needs to be approved)
- **Full Source Code Available:** Don't just trust it, verify it. The entire source code is available right here on GitHub for you to review.

---

## ✨ Features

- **Automated DLL Management:** Download and update YimMenu with a single click.
- **Smart Updates:** Automatically checks for new DLL versions on startup.
- **Lua Script Manager:** Easily manage your favorite Lua scripts.
- **Integrated Game Launcher:** Start GTA V and inject the menu directly from the app.
- **Modern UI/UX:** A sleek interface with light and dark themes.

---

## 🚀 Getting Started

Get the latest release directly from the downloads page. Just download and run the `YMU.exe`.

| [Download YMU.exe (Latest Release)](https://github.com/tommylam120/YMU/releases/latest) |
| :---------------------------------------------------------------------------------: |

---

## 🖼️ Screenshots

### Dark Theme

<div align="center">
  <img src="https://github.com/user-attachments/assets/6c322c71-5ed9-4476-a091-22da12772fe6?raw=true" alt="YMU Dark Theme: Settings" width="32%"/>
  <img src="https://github.com/user-attachments/assets/ddf5b40f-3925-43cf-b536-24b833d56889?raw=true" alt="YMU Dark Theme: Inject" width="32%"/>
  <img src="https://github.com/user-attachments/assets/23ac7acb-071b-4412-9b03-dbc071eefe02?raw=true" alt="YMU Dark Theme: Download" width="32%"/>
</div>

### Light Theme

<div align="center">
  <img src="https://github.com/user-attachments/assets/2d111d22-7344-4a71-ad5e-899d7bd091bf?raw=true" alt="YMU Light Theme: Settings" width="32%"/>
  <img src="https://github.com/user-attachments/assets/19fcf98e-83e2-4083-bbb5-717cb4bb86fe?raw=true" alt="YMU Light Theme: Inject" width="32%"/>
  <img src="https://github.com/user-attachments/assets/857f8c8c-3746-4a1d-800c-f926613a03d2?raw=true" alt="YMU Light Theme: Download" width="32%"/>
</div>

---

### Full Changelog



</details>

---

## 📦 Building from Source

<details>
<summary><b>Click to expand instructions for developers</b></summary>
  
### First things first - get the source

| [Download Source Code](https://github.com/tommylam120/YMU/archive/refs/heads/main.zip) |
| :--------------------------------------------------------------------------------: |

### Requirements and Dependencies

| Programming Language: | [Python](https://python.org) |
| :-------------------- | :--------------------------- |

> I'm using Python `3.12.10` while coding YMU

#### Libraries

| Library                                            | pip command                       |
| :------------------------------------------------- | :-------------------------------- |
| Install all Libraries                              | `pip install -r requirements.txt` |
| [PySide6](https://pypi.org/project/PySide6/)       | `pip install pyside6`             |
| [requests](https://pypi.org/project/requests/)     | `pip install requests`            |
| [psutil](https://pypi.org/project/psutil/)         | `pip install psutil`              |
| [pyinjector](https://pypi.org/project/pyinjector/) | `pip install pyinjector`          |
| [pywin32](https://pypi.org/project/pywin32/)       | `pip install pywin32`             |
| [packaging](https://pypi.org/project/packaging/)   | `pip install packaging`           |

### Creating the Executable (.exe)

This project uses **Nuitka** (instead of PyInstaller) to create a high-performance, compact executable.

1.  **Install Nuitka & Dependencies:**

    ```bash
    pip install nuitka zstandard
    ```

2.  **Run the build command:**
    Navigate to the root directory of the project in your terminal and run the following command. This will create the `YMU.exe` in the `dist` folder.

    ```bash
    python -m nuitka --onefile --standalone --enable-plugin=pyside6 --windows-icon-from-ico=src/assets/icons/logo_dark.ico --include-data-dir=src/assets=assets --windows-console-mode=disable --output-dir=dist --output-filename=YMU.exe src/gui.py

    nuitka --onefile --standalone --enable-plugin=pyside6 --windows-icon-from-ico=src/assets/icons/ymu.ico --include-data-dir=src/assets=assets --windows-console-mode=disable --output-dir=dist --output-filename=YMU.exe src/gui.py

    ```

    **Command Breakdown:**

    - **`--onefile`**: Bundles everything into a single `.exe` file.
    - **`--enable-plugin=pyside6`**: Optimizes the build for Qt/PySide6.
    - **`--windows-console-mode=disable`**: Prevents the black console window.
    - **`--include-data-dir`**: Bundles the assets folder.

</details>

---

## ⭐ Support the Project

> [!IMPORTANT]
> **Show your support by giving this Project a ⭐. Thanks <3!**

---

## Disclaimer

> [!WARNING]
> Use this project for educational purposes only and use it at your own risk.

> [!CAUTION]
> I am not liable or responsible for any direct or indirect consequences that may result from the use of YMU or YimMenu.

---

## Credits
| **Menu**         | [**YimMenu**](https://yim.gta.menu/)                                                                                |
| **Logo**         | [**Made with Figma**](https://figma.com)                                                                            |
| **Icons**        | [**Feather**](https://feathericons.dev/)                                                                            |
| **Fonts**        | [**Manrope**](https://fonts.google.com/specimen/Manrope) & [**JetBrains Mono**](https://www.jetbrains.com/lp/mono/) |
