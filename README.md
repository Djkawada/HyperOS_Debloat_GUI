# HyperOS_Debloat_GUI

A user-friendly graphical interface (GUI) tool to simplify debloating (removing or disabling pre-installed applications) on Xiaomi, Poco, or Redmi phones running HyperOS or MIUI, using ADB commands. This tool allows you to safely uninstall or disable pre-installed applications for the current user without requiring root access.

**Disclaimer:** Use this tool at your own risk. While the tool primarily targets applications often considered bloatware and uses safe (per-user) uninstall/disable methods, removing certain system applications can potentially lead to unexpected behavior, broken features, or in rare cases, system instability. Always understand what an app does before removing it.

## Features

* Scans your connected phone via ADB to find installed applications matching a known bloatware database.
* Displays found apps in a list with Package Name, Description, Safety Level, and Category.
* Allows selecting multiple apps using the GUI or built-in selection buttons (Select All, Select Safe, etc.).
* Provides a review screen showing the selected apps before processing.
* Attempts to uninstall selected apps for the current user (`pm uninstall --user 0`).
* If uninstall fails, it attempts to disable the app for the current user (`pm disable-user --user 0`).
* Does **not** require root access.
* Does **not** permanently remove apps from the system partition (apps may reappear after a factory reset or system update).

## Prerequisites

Even if you use the executable (.exe) version, certain prerequisites related to connecting to your phone are still necessary:

1.  **ADB (Android Debug Bridge) installed and in PATH:** ADB must be installed on your computer and its location added to your system's PATH environment variable.
    * Download My Other tool to check and Install the latest ADB to your Path at : https://github.com/Djkawada/ADB-Path-Checker-Installer
OR 
    * Download the latest [SDK Platform-Tools for Windows](https://developer.android.com/tools/releases/platform-tools).
    * Extract the downloaded zip file to a stable location (e.g., `C:\platform-tools`).
    * **Add the `platform-tools` folder path to your system's PATH:**
        * Search for "environment variables" in the Windows search bar and select "Edit environment variables for your account" or "Edit the system environment variables".
        * In the "Environment Variables" window, find the `Path` variable under "System variables" and select it.
        * Click "Edit".
        * Click "New" and paste the full path to your `platform-tools` folder (e.g., `C:\platform-tools`).
        * Click OK on all windows to save the changes.
        * Open a **new** Command Prompt or PowerShell window and type `adb version` to verify it's working.
2.  **USB Debugging enabled on your device :
    * Go to `Settings` > `About phone`.
    * Tap on the `HyperOS version` (or MIUI version) multiple times (usually 7 times) until you see a message that "Developer options are now enabled".
    * Go back to `Settings` > `Additional settings` > `Developer options`.
    * Enable the `USB debugging` toggle.
    * Consider enabling `Install via USB` and `USB debugging (Security settings)` if available, as they can sometimes help.
3.  **Authorize your computer:** Connect your phone to the computer via a USB cable. You should see an "Allow USB debugging?" pop-up on your phone screen. **Check "Always allow from this computer"** and tap **Allow**. If you don't see it, try revoking USB debugging authorizations in Developer options, unplugging/replugging the cable, toggling USB debugging off/on, or changing the USB connection mode (e.g., File Transfer/MTP).
4.  **USB Cable:** Use a reliable USB data cable.

## How to Use (Executable Version - .exe for Windows)

This version does **not** require Python or PyInstaller to be installed.

1.  Go to the release page : https://github.com/Djkawada/HyperOS_Debloat_GUI/releases/tag/v1.0.0
2.  Download the latest Windows executable (`.exe`) file. Look in the "Assets" section of the latest release. (If a `--onedir` version was built, the asset will be a `.zip` file containing the `.exe` and other files - download and extract this zip).
3.  Save the downloaded `.exe` file (or the extracted folder from the zip) to a convenient location on your computer, for example, on your Desktop or in a dedicated folder.
4.  Ensure you have completed all the **Prerequisites** above (ADB, USB Debugging, Authorization, Cable).
5.  Connect your phone to the computer via USB.
6.  **Run the `.exe` file** you downloaded (double-click it in File Explorer, or run it from the command line).
7.  The Graphical User Interface (GUI) application window should appear.
8.  Click the **Connect & Scan Apps** button.
9.  Monitor the "Status Log" at the bottom for feedback on the connection and scanning process.
10. If the scan is successful, the list in the middle will populate with detected pre-installed apps matching the tool's database.
11. **Select apps** you wish to remove/disable by clicking on their rows in the list (selected rows are highlighted in blue).
12. Use the **Select All**, **Select None**, **Select Safe**, **Select Caution**, or **Select Risky** buttons to assist with selections.
13. Use the **Filter Safety** and **Filter Category** dropdowns to narrow down the list of apps displayed.
14. Once you have selected the apps you wish to process, click the **Process Selected Apps** button.
15. A "Review Selected Apps" window will pop up, listing the apps you selected. **Review this list carefully.**
16. If you are sure you want to proceed, click **Confirm and Process** in the review window. If you need to change your selection, click **Cancel** and adjust the selection in the main window.
17. The tool will then attempt to uninstall (user 0) or disable (user 0) each selected app, showing the progress in the main window's Status Log.
18. After processing is complete, it is recommended to **restart your phone** for changes to take full effect.

## How to Use (From Python Script)

If you prefer to run the tool directly from the Python source code, follow these steps. This requires Python to be installed.

1.  Ensure you have **Python** installed (see Prerequisites).
2.  Ensure you have completed the other **Prerequisites** (ADB, USB Debugging, Authorization, Cable).
3.  Save the content of the `HyperOS_Debloat_GUI.py` script from this repository to your computer.
4.  Connect your phone to the computer via USB.
5.  Open a Command Prompt or PowerShell window.
6.  Navigate to the folder where you saved the script.
7.  Run the script:
    ```bash
    python HyperOS_Debloat_GUI.py
    ```
    (Or use the full path to `python.exe` if necessary).
8.  Continue from step 7 of the "How to Use (Executable Version)" section.

## Safety Levels Explained

* **SAFE:** These are generally third-party apps or non-essential Xiaomi/Google apps that are widely considered safe to remove/disable without impacting core phone functionality (e.g., Facebook, Netflix, GetApps, Analytics). You will lose the specific functionality of the removed app.
* **CAUTION:** These apps might be related to system features that some users use, or their removal might have minor or unexpected side effects on non-core functionality (e.g., certain Google Assistant components, Mi Browser, Mi RCS). Evaluate if you use the related feature before removing it.
* **RISKY:** These applications are potentially critical system components. Removing or disabling them can lead to serious issues like bootloops, crashes, or broken essential functions (e.g., Package Installer, core Messaging Frameworks, IMS Service, Device Health). **Removing RISKY apps is strongly discouraged unless you know exactly what you are doing and accept the risk.**

**This tool marks potentially dangerous apps as RISKY based on common knowledge. Always research a package name if you are unsure.**

## Adding More Apps to the Database

If you find other pre-installed applications on your device that are not in the list, you can add them to the `known_bloatware_db` dictionary in the script's code.

1.  Find the package name of the app on your phone (e.g., using a package name viewer app or the command `adb shell pm list packages`).
2.  Edit the `HyperOS_Debloat_GUI.py` file.
3.  Locate the `known_bloatware_db` dictionary near the top of the file.
4.  Add a new entry in the format:
    ```python
    "com.example.packagename": ("Brief description of the app", "SAFETY_LEVEL", "Category"),
    ```
    Replace `"com.example.packagename"` with the actual package name, `"Brief description..."` with a description, `"SAFETY_LEVEL"` with "SAFE", "CAUTION", or "RISKY", and `"Category"` with an appropriate category (e.g., "Other_ThirdParty", "Game", "Xiaomi", "Google", etc.). Be very cautious when assigning safety levels to system apps.
5.  Save the file and run the script again (or rebuild the executable if you are using that version). The newly added app should now appear if it's installed on your device.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
