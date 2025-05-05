# Add this print statement at the very beginning of the file
print("--- Script Loading Started ---")

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import subprocess
import sys
import time
import threading
import traceback # Import traceback for detailed error printing

# --- Internal Database of Known Bloatware/Removable Apps ---
# This dictionary maps package names to a tuple: (Description, Safety Level, Category)
# Safety Levels:
#   SAFE: Generally safe to remove/disable without impacting core functions.
#   CAUTION: May affect specific features, check if you use them.
#   RISKY: Removing can cause instability, broken core functions, or bootloops. Proceed with extreme caution.
# Categories:
#   Android_System: Core Android OS components (can be risky)
#   Google: Apps/Services from Google (some are core GMS, some are optional)
#   Xiaomi: Apps/Services from Xiaomi/MIUI/HyperOS (mix of bloat and core)
#   Facebook: Facebook suite of apps
#   Other_ThirdParty: Other pre-installed non-Google, non-Xiaomi apps
#   Manufacturer_Test: Factory/Carrier test apps
#   Game: Pre-installed games or game-related services
#
# This list is based on common knowledge and previous user-provided lists.
# It is NOT exhaustive of ALL possible bloatware or ALL Xiaomi apps.
known_bloatware_db = {
    # Android System Components (Often safe to remove if not used, but be aware)
    "com.android.bluetoothmidiservice": ("Bluetooth MIDI Service", "SAFE", "Android_System"),
    "com.android.calllogbackup": ("Android Call Log Backup Service", "SAFE", "Android_System"),
    "com.android.cellbroadcastreceiver": ("Android Cell Broadcast Receiver (Emergency Alerts)", "CAUTION", "Android_System"), # Keep if you need emergency alerts
    "com.android.cellbroadcastreceiver.overlay.common": ("Overlay for Cell Broadcast Receiver", "CAUTION", "Android_System"), # Keep if you need emergency alerts
    "com.android.dreams.basic": ("Basic Screensaver", "SAFE", "Android_System"),
    "com.android.dreams.phototable": ("Photo Table Screensaver", "SAFE", "Android_System"),
    "com.android.managedprovisioning": ("Work Profile/Device Provisioning", "SAFE", "Android_System"), # Only if you don't use work profiles
    "com.android.ons": ("OMA Notification Service (Carrier)", "CAUTION", "Android_System"), # Carrier specific, hard to judge universally
    "com.android.providers.calendar": ("Android Calendar Storage", "RISKY", "Android_System"), # Essential for calendar apps
    "com.android.providers.partnerbookmarks": ("Partner Bookmarks Provider", "SAFE", "Android_System"),
    "com.android.providers.userdictionary": ("User Dictionary Storage", "SAFE", "Android_System"),
    "com.android.sharedstoragebackup": ("Shared Storage Backup Service", "SAFE", "Android_System"),
    "com.android.smspush": ("SMS Push Service (Carrier/Messaging)", "CAUTION", "Android_System"),
    "com.android.theme.font.notoserifsource": ("Noto Serif Font", "SAFE", "Android_System"),
    "com.android.traceur": ("System Tracing Tool (Developer)", "SAFE", "Android_System"),
    "com.android.wallpaperbackup": ("Wallpaper Backup Service", "SAFE", "Android_System"),

    # Facebook Apps (Common Third-Party Bloat)
    "com.facebook.appmanager": ("Facebook App Manager", "SAFE", "Facebook"),
    "com.facebook.katana": ("Facebook App", "SAFE", "Facebook"),
    "com.facebook.services": ("Facebook Services", "SAFE", "Facebook"),
    "com.facebook.system": ("Facebook System", "SAFE", "Facebook"),

    # Other Third-Party Apps (Common Bloat)
    "com.netflix.mediaclient": ("Netflix App", "SAFE", "Other_ThirdParty"),
    "com.spotify.music": ("Spotify App", "SAFE", "Other_ThirdParty"), # Package name might vary
    "com.ss.android.ugc.trill": ("TikTok App (Global)", "SAFE", "Other_ThirdParty"),
    "org.ifaa.aidl.manager": ("IFAA Service (Payment/Authentication)", "SAFE", "Other_ThirdParty"),

    # Manufacturer/Carrier Test Apps (Often Safe)
    "com.fido.asm": ("FIDO ASM (Authentication)", "SAFE", "Manufacturer_Test"),
    "com.goodix.gftest": ("Goodix Fingerprint Test", "SAFE", "Manufacturer_Test"),
    "com.quicinc.voice.activation": ("Qualcomm Voice Activation", "SAFE", "Manufacturer_Test"), # If you don't use voice wake-up
    "com.longcheertel.AutoTest": ("Longcheer Auto Test (Factory)", "SAFE", "Manufacturer_Test"),
    "com.longcheertel.cit": ("Longcheer CIT (Factory Test)", "SAFE", "Manufacturer_Test"),
    "com.longcheertel.sarauth": ("Longcheer SAR Auth (Factory)", "SAFE", "Manufacturer_Test"),

    # Google Apps (Can be Bloat depending on usage, but core to Android/GMS)
    "com.google.android.apps.photos": ("Google Photos App", "SAFE", "Google"), # If you use another gallery
    "com.google.android.apps.restore": ("Google Restore", "SAFE", "Google"), # After initial setup
    "com.google.android.apps.subscriptions.red": ("Google Subscriptions (YouTube Premium)", "SAFE", "Google"), # If you don't manage subs here
    "com.google.android.apps.tachyon": ("Google Duo (Meet)", "SAFE", "Google"), # If you don't use Duo/Meet
    "com.google.android.apps.turbo": ("Device Health Services / Adaptive Battery", "RISKY", "Google"), # Can impact battery management
    "com.google.android.apps.wellbeing": ("Digital Wellbeing", "SAFE", "Google"),
    "com.google.android.apps.youtube.music": ("YouTube Music App", "SAFE", "Google"), # If you use another music app
    "com.google.android.as": ("Android System Intelligence", "CAUTION", "Google"), # Provides smart features like Live Caption
    "com.google.android.as.oss": ("Android System Intelligence OSS", "CAUTION", "Google"), # Related to AS
    "com.google.android.cellbroadcastreceiver": ("Google Cell Broadcast Receiver", "CAUTION", "Google"), # Emergency Alerts
    "com.google.android.cellbroadcastservice": ("Google Cell Broadcast Service", "CAUTION", "Google"), # Emergency Alerts
    "com.google.android.feedback": ("Google Feedback Service", "SAFE", "Google"),
    "com.google.android.gms.location.history": ("Google Location History", "SAFE", "Google"), # If you don't use it
    "com.google.android.gms.supervision": ("Google Family Link (Supervision)", "SAFE", "Google"), # If you don't use Family Link
    "com.google.android.googlequicksearchbox": ("Google App / Search / Assistant", "CAUTION", "Google"), # Core Google features
    "com.google.android.ims": ("IMS Service (VoLTE/VoWiFi)", "RISKY", "Google"), # Can break calls
    "com.google.android.marvin.talkback": ("TalkBack (Accessibility)", "SAFE", "Google"), # Unless you need it
    "com.google.android.onetimeinitializer": ("One Time Initializer", "SAFE", "Google"), # After setup
    "com.google.android.partnersetup": ("Partner Setup", "SAFE", "Google"), # After setup
    "com.google.android.printservice.recommendation": ("Print Service Recommendation", "SAFE", "Google"),
    "com.google.android.projection.gearhead": ("Android Auto", "SAFE", "Google"), # If you don't use Android Auto
    "com.google.android.syncadapters.calendar": ("Google Calendar Sync", "CAUTION", "Google"), # Breaks Google Calendar sync
    "com.google.android.tts": ("Google Text-to-speech", "SAFE", "Google"), # If you use another TTS engine or none
    "com.google.android.videos": ("Google TV (Play Movies)", "SAFE", "Google"), # If you don't use Google TV
    "com.google.android.youtube": ("YouTube App", "SAFE", "Google"), # If you use browser or another app

    # Xiaomi/MIUI/HyperOS Apps (Mix of Bloat and Core Components)
    "android.autoinstalls.config.Xiaomi.model": ("Xiaomi Auto Installs Config", "SAFE", "Xiaomi"), # After initial setup
    "com.mi.globalbrowser": ("Mi Browser (Global)", "SAFE", "Xiaomi"), # If you use another browser
    "com.mi.globalminusscreen": ("App Vault", "SAFE", "Xiaomi"), # If you don't use App Vault
    "com.miui.analytics": ("MIUI/HyperOS Analytics", "SAFE", "Xiaomi"), # Stops sending usage data
    "com.miui.audioeffect": ("MIUI/HyperOS Audio Effects", "SAFE", "Xiaomi"), # If you don't use them
    "com.miui.audiomonitor": ("MIUI/HyperOS Audio Monitor", "SAFE", "Xiaomi"), # If you don't use voice features
    "com.miui.backup": ("MIUI/HyperOS Backup", "SAFE", "Xiaomi"), # If you use other backup methods
    "com.miui.bugreport": ("MIUI/HyperOS Bug Report", "SAFE", "Xiaomi"),
    "com.miui.cleaner": ("MIUI/HyperOS Cleaner", "SAFE", "Xiaomi"),
    "com.miui.cloudbackup": ("Mi Cloud Backup", "SAFE", "Xiaomi"), # If you use other backup methods
    "com.miui.cloudservice": ("Mi Cloud Services", "SAFE", "Xiaomi"), # If you don't use Mi Cloud
    "com.miui.daemon": ("MIUI/HyperOS Daemon", "RISKY", "Xiaomi"), # Can cause instability
    "com.miui.global.packageinstaller": ("MIUI/HyperOS Package Installer", "RISKY", "Xiaomi"), # ESSENTIAL - DO NOT REMOVE
    "com.miui.micloudsync": ("Mi Cloud Sync", "SAFE", "Xiaomi"), # If you don't use Mi Cloud sync
    "com.miui.miservice": ("Mi Service / Xiaomi Service", "SAFE", "Xiaomi"), # Often not critical
    "com.miui.msa.global": ("MSA (MIUI System Ads - Global)", "SAFE", "Xiaomi"), # Major source of ads - Highly Recommended
    "com.miui.phrase": ("Quick Phrases / Smart Assistant", "SAFE", "Xiaomi"), # If you don't use these features
    "com.miui.yellowpage": ("Yellow Pages / Dialer Features", "SAFE", "Xiaomi"), # If you don't use these features
    "com.xiaomi.calendar": ("Xiaomi Calendar App", "SAFE", "Xiaomi"), # If you use another calendar
    "com.xiaomi.glgm": ("Xiaomi Game Center / Service", "GAME", "Xiaomi"), # Game related service - Marked as GAME category
    "com.xiaomi.mipicks": ("GetApps (Xiaomi App Store)", "SAFE", "Xiaomi"), # If you use Google Play Store
    "com.xiaomi.mircs": ("Mi RCS Service", "CAUTION", "Xiaomi"), # May affect Xiaomi messaging features
    "com.xiaomi.mtb": ("Mi Telephony/Messaging Component", "CAUTION", "Xiaomi"), # Related to basic phone functions
    "com.xiaomi.payment": ("Xiaomi Payment / Mi Pay", "SAFE", "Xiaomi"), # If you don't use this service
    "com.xiaomi.simactivate.service": ("SIM Activation Service", "SAFE", "Xiaomi"), # After SIM activated
    "com.xiaomi.xmsf": ("Xiaomi Messaging Framework (Core)", "RISKY", "Xiaomi"), # Breaks Mi Account, push notifications
    "com.xiaomi.xmsfkeeper": ("Xiaomi Messaging Framework Keeper", "RISKY", "Xiaomi"), # Related to XMSF

    # Add potential game package names you find here, with description, safety, and category ("Game")
    # Use a package name viewer app or adb shell pm list packages on your phone
    # "com.example.preinstalled_game1": ("Example Preinstalled Game 1", "SAFE", "Game"),
    # "com.example.preinstalled_game2": ("Example Preinstalled Game 2", "SAFE", "Game"),
}

# Add print to confirm database is loaded
print("--- Database loaded ---")

# --- Helper function to run ADB commands ---
# This function now returns a dict indicating success or failure,
# including stdout/stderr and returncode on success, or error details on failure.
def run_adb_command(command, package_name="N/A", step_desc="execute command"):
    """Runs an ADB command and returns a dict indicating success or failure."""
    try:
        # print(f"  Executing: {' '.join(command)}") # Uncomment for verbose ADB commands
        # Use Popen to manage the process. CREATE_NO_WINDOW prevents a console window from flashing.
        # stderr is directed to stdout so we capture all command output in stdout.
        # Added creationflags for Windows
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0)

        # Use communicate with timeout to avoid deadlocks and handle timeout
        stdout, _ = process.communicate(timeout=60)
        returncode = process.returncode

        # Command completed without Python exception or timeout.
        return {"error": False, "returncode": returncode, "stdout": stdout, "stderr": ""} # Return stderr as empty string as it's captured in stdout

    except FileNotFoundError:
        # This error happens if the 'adb' executable itself is not found
        return {"error": True, "type": "ADB_NOT_FOUND", "message": f"\nError: ADB command 'adb' not found. Ensure ADB is in your system's PATH.\n"}
    except subprocess.TimeoutExpired:
        # This error happens if the command times out
        try: # Try to terminate gracefully first
            process.terminate()
            stdout, _ = process.communicate(timeout=5) # Read any remaining output
        except: # If terminate fails, kill
            process.kill()
            stdout, _ = process.communicate(timeout=5) # Read any remaining output

        return {"error": True, "type": "TIMEOUT", "message": f"  Error: ADB command timed out while trying to {step_desc} {package_name}.\n", "stdout_on_timeout": stdout} # Include partial output

    except Exception as e:
        # Catch any other unexpected Python-level errors during subprocess creation/communication
        return {"error": True, "type": "PYTHON_ERROR_SUBPROCESS", "message": f"\nAn unexpected Python error during subprocess for {step_desc} {package_name}: {e}\nTraceback:\n{traceback.format_exc()}\n"}


# --- GUI Application Class ---
class PocoAppManagerGUI:
    def __init__(self, master):
        # Add a print to confirm we enter __init__
        print("--- Entering PocoAppManagerGUI __init__ ---")
        self.master = master
        master.title("Poco X6 Pro App Manager")
        # Set minimum window size (optional)
        master.minsize(800, 600)


        # --- Styles ---
        style = ttk.Style()
        style.configure("Treeview.Heading", font=('TkDefaultFont', 10, 'bold'))
        style.configure("TButton", font=('TkDefaultFont', 9))
        # Configure tags for colors (run once in __init__)
        self.tree_tags_configured = False # Flag to ensure tags are configured only once


        # --- Frames ---
        self.controls_frame = ttk.Frame(master, padding="10")
        self.controls_frame.grid(row=0, column=0, sticky="ew")

        self.filter_frame = ttk.Frame(master, padding="0 5 0 5") # Add padding top/bottom
        self.filter_frame.grid(row=0, column=1, sticky="ew", padx=10) # Place next to controls

        self.list_frame = ttk.Frame(master, padding="0 10 0 10") # Add padding top/bottom
        self.list_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10) # Span across columns

        self.status_frame = ttk.Frame(master, padding="10")
        self.status_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10) # Span across columns

        master.grid_columnconfigure(0, weight=1) # Make control column expandable
        master.grid_columnconfigure(1, weight=1) # Make filter column expandable
        master.grid_rowconfigure(1, weight=1) # Allow list frame to expand

        # --- Controls ---
        self.scan_button = ttk.Button(self.controls_frame, text="Connect & Scan Apps", command=self.start_scan)
        self.scan_button.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.process_button = ttk.Button(self.controls_frame, text="Process Selected Apps", command=self.start_process, state=tk.DISABLED)
        self.process_button.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        # --- Selection Buttons ---
        self.select_all_button = ttk.Button(self.controls_frame, text="Select All", command=self.select_all_apps, state=tk.DISABLED)
        self.select_all_button.grid(row=0, column=2, padx=5, pady=5)
        print("--- select_all_button created ---") # Added print

        self.select_none_button = ttk.Button(self.controls_frame, text="Select None", command=self.select_none_apps, state=tk.DISABLED)
        self.select_none_button.grid(row=0, column=3, padx=5, pady=5)
        print("--- select_none_button created ---") # Added print

        self.select_safe_button = ttk.Button(self.controls_frame, text="Select Safe", command=lambda: self.select_by_safety("SAFE"), state=tk.DISABLED)
        self.select_safe_button.grid(row=0, column=4, padx=5, pady=5)
        print("--- select_safe_button created ---") # Added print


        self.select_caution_button = ttk.Button(self.controls_frame, text="Select Caution", command=lambda: self.select_by_safety("CAUTION"), state=tk.DISABLED)
        self.select_caution_button.grid(row=0, column=5, padx=5, pady=5)
        print("--- select_caution_button created ---") # Added print

        self.select_risky_button = ttk.Button(self.controls_frame, text="Select Risky", command=lambda: self.select_by_safety("RISKY"), state=tk.DISABLED)
        self.select_risky_button.grid(row=0, column=6, padx=5, pady=5)
        print("--- select_risky_button created ---") # Added print


        # Add category selection combobox/buttons if desired (more complex layout)
        # self.category_label = ttk.Label(self.filter_frame, text="Select Category:")
        # self.category_label.grid(row=1, column=0, padx=5, pady=5)
        # categories = sorted(list(set(info[2] for info in known_bloatware_db.values())))
        # self.category_combobox = ttk.Combobox(self.filter_frame, values=categories, state="readonly", width=15)
        # self.category_combobox.grid(row=1, column=1, padx=5, pady=5)
        # self.category_combobox.bind("<<ComboboxSelected>>", lambda event: self._apply_filters())


        # --- Filter Controls ---
        self.filter_safety_label = ttk.Label(self.filter_frame, text="Filter Safety:")
        self.filter_safety_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.safety_filter_options = ["All", "SAFE", "CAUTION", "RISKY"]
        self.safety_filter_combobox = ttk.Combobox(self.filter_frame, values=self.safety_filter_options, state="readonly", width=10)
        self.safety_filter_combobox.set("All")
        self.safety_filter_combobox.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.safety_filter_combobox.bind("<<ComboboxSelected>>", lambda event: self._apply_filters())

        self.filter_category_label = ttk.Label(self.filter_frame, text="Filter Category:")
        self.filter_category_label.grid(row=0, column=2, padx=5, pady=5, sticky="w")
        # Categories will be populated after scan
        self.category_filter_options = ["All"]
        self.category_filter_combobox = ttk.Combobox(self.filter_frame, values=self.category_filter_options, state="readonly", width=15)
        self.category_filter_combobox.set("All")
        self.category_filter_combobox.grid(row=0, column=3, padx=5, pady=5, sticky="w")
        self.category_filter_combobox.bind("<<ComboboxSelected>>", lambda event: self._apply_filters())

        # Allow filter frame columns to expand slightly
        self.filter_frame.grid_columnconfigure(1, weight=1)
        self.filter_frame.grid_columnconfigure(3, weight=1)


        # --- App List (Treeview) ---
        self.tree = ttk.Treeview(self.list_frame, columns=("Package", "Safety", "Category", "Description"), show="headings")
        self.tree.grid(row=0, column=0, sticky="nsew")

        # Define columns and headings
        # We will simulate checkboxes using tags and click handling
        self.tree.heading("Package", text="Package Name", anchor=tk.W)
        self.tree.heading("Safety", text="Safety", anchor=tk.W)
        self.tree.heading("Category", text="Category", anchor=tk.W)
        self.tree.heading("Description", text="Description", anchor=tk.W)

        # Define column widths (adjust as needed)
        self.tree.column("Package", width=250, stretch=tk.YES)
        self.tree.column("Safety", width=80, stretch=tk.NO)
        self.tree.column("Category", width=100, stretch=tk.NO)
        self.tree.column("Description", width=300, stretch=tk.YES) # Description can take more space

        # Scrollbar
        self.treescroll = ttk.Scrollbar(self.list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.treescroll.set)
        self.treescroll.grid(row=0, column=1, sticky="ns")

        self.list_frame.grid_columnconfigure(0, weight=1)
        self.list_frame.grid_rowconfigure(0, weight=1)

        # Store package names mapped to Treeview item IDs
        self._item_packages = {} # Maps Treeview item ID to package name
        self.all_installed_bloatware = {} # Store the full list after scan

        # Bind click event to toggle selection state (visual feedback needed)
        self.tree.bind("<ButtonRelease-1>", self._on_item_click)
        self.tree.bind("<Double-1>", self._on_item_double_click) # Optional: view details

        # Configure initial tags for colors (must be done after treeview is created)
        self._configure_tree_tags()


        # --- Status Log ---
        self.status_log = scrolledtext.ScrolledText(self.status_frame, height=8, state=tk.DISABLED, wrap=tk.WORD, font=('Courier New', 9)) # Using Courier New for better alignment
        self.status_log.grid(row=0, column=0, sticky="ew")
        self.status_frame.grid_columnconfigure(0, weight=1)

        # Initial state
        self.print_status("Poco X6 Pro App Manager GUI ready.\nConnect your phone, enable USB debugging, authorize your computer, and click 'Connect & Scan Apps'.")
        self.print_status("Ensure ADB is installed and in your system PATH.")
        self.print_status("Click on a row to select/deselect it (highlighted in blue). Use filter options above.")
        # Add print to confirm __init__ finished
        print("--- PocoAppManagerGUI __init__ finished ---")


    def _configure_tree_tags(self):
        """Configures Treeview tags for colors and selection highlight."""
        if not self.tree_tags_configured:
            self.tree.tag_configure('risky_tag', foreground='red')
            self.tree.tag_configure('caution_tag', foreground='orange')
            self.tree.tag_configure('selected', background='lightblue') # Keep selection highlight
            self.tree_tags_configured = True


    # --- Status Logging Helper ---
    def print_status(self, message):
        self.status_log.config(state=tk.NORMAL)
        self.status_log.insert(tk.END, message + "\n")
        self.status_log.see(tk.END) # Auto-scroll to the bottom
        self.status_log.config(state=tk.DISABLED)
        self.master.update_idletasks() # Update GUI immediately # Ensure GUI updates


    # --- ADB Command Runner (Threaded) ---
    # This function now returns a dict indicating success or failure,
    # including stdout/stderr and returncode on success, or error details on failure.
    def run_adb_command(self, command, package_name="N/A", step_desc="execute command"):
        """Runs an ADB command and returns a dict indicating success or failure."""
        try:
            # print(f"  Executing: {' '.join(command)}") # Uncomment for verbose ADB commands
            # Use Popen to manage the process. CREATE_NO_WINDOW prevents a console window from flashing.
            # stderr is directed to stdout so we capture all command output in stdout.
            # Added creationflags for Windows
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0)

            # Use communicate with timeout to avoid deadlocks and handle timeout
            stdout, _ = process.communicate(timeout=60)
            returncode = process.returncode

            # Command completed without Python exception or timeout.
            return {"error": False, "returncode": returncode, "stdout": stdout, "stderr": ""} # Return stderr as empty string as it's captured in stdout

        except FileNotFoundError:
            # This error happens if the 'adb' executable itself is not found
            return {"error": True, "type": "ADB_NOT_FOUND", "message": f"\nError: ADB command 'adb' not found. Ensure ADB is in your system's PATH.\n"}
        except subprocess.TimeoutExpired:
            # This error happens if the command times out
            try: # Try to terminate gracefully first
                process.terminate()
                stdout, _ = process.communicate(timeout=5) # Read any remaining output
            except: # If terminate fails, kill
                process.kill()
                stdout, _ = process.communicate(timeout=5) # Read any remaining output

            return {"error": True, "type": "TIMEOUT", "message": f"  Error: ADB command timed out while trying to {step_desc} {package_name}.\n", "stdout_on_timeout": stdout} # Include partial output

        except Exception as e:
            # Catch any other unexpected Python-level errors during subprocess creation/communication
            return {"error": True, "type": "PYTHON_ERROR_SUBPROCESS", "message": f"\nAn unexpected Python error during subprocess for {step_desc} {package_name}: {e}\nTraceback:\n{traceback.format_exc()}\n"}


    # --- Scan Process ---
    def start_scan(self):
        # Add a print here to see if the method is entered
        print("--- Button 'Connect & Scan' Clicked ---") # Console print
        self.set_buttons_state(tk.DISABLED)
        self.process_button.config(state=tk.DISABLED) # Disable process button until scan is complete

        self.print_status("\n--- Starting Scan Process ---")
        self.print_status("Checking ADB connection...")
        # Clear previous results
        for item in self.tree.get_children():
            self.tree.delete(item)
        self._item_packages.clear()
        self.all_installed_bloatware.clear() # Clear previous scan data

        # Run scan in a separate thread to keep GUI responsive
        print("--- Starting scan thread ---") # Console print
        scan_thread = threading.Thread(target=self._perform_scan_task, daemon=True) # daemon=True allows thread to exit with GUI
        scan_thread.start()
        print("--- Scan thread started ---") # Console print


    def _perform_scan_task(self):
        """Task run in a separate thread for scanning."""
        print("--- Inside _perform_scan_task thread ---") # Console print
        try:
            # Check ADB connection first
            adb_check_command = ["adb", "devices"]
            check_result = self.run_adb_command(adb_check_command, step_desc="check connection")

            # Handle command execution errors (FileNotFoundError, Timeout, Python error)
            if check_result.get("error"):
                 self.master.after(0, self.print_status, check_result["message"])
                 if check_result.get("stdout_on_timeout"): # Print output if available (e.g., partial output on timeout)
                      self.master.after(0, self.print_status, "Partial Output:\n" + check_result["stdout_on_timeout"].strip())
                 self.master.after(0, self.set_buttons_state, tk.NORMAL) # Update GUI state back
                 print("--- Scan thread finished (execution error) ---") # Console print
                 return

            # Now check the result of the ADB command itself (returncode, stdout)
            # For 'adb devices', non-zero returncode is an error, but "unauthorized" or "no devices"
            # messages are in stdout/stderr even with returncode 0.
            # Check if stdout contains a device entry and not an error message
            if check_result["returncode"] != 0 or "List of devices attached" not in check_result["stdout"] or "device" not in check_result["stdout"] or "unauthorized" in check_result["stdout"] or "error" in check_result["stdout"].lower():
                 self.master.after(0, self.print_status, "Error: ADB device not found or unauthorized.")
                 self.master.after(0, self.print_status, "Please ensure your phone is connected, USB Debugging is ON, and authorized.")
                 self.master.after(0, self.print_status, "ADB Output (stdout):\n" + check_result["stdout"].strip())
                 self.master.after(0, self.set_buttons_state, tk.NORMAL) # Update GUI state back
                 print("--- Scan thread finished (device error) ---") # Console print
                 return

            self.master.after(0, self.print_status, "ADB connection successful.")

            # Get installed packages for user 0
            installed_packages = self.get_installed_packages()

            if installed_packages is None or (isinstance(installed_packages, dict) and installed_packages.get("error")):
                 self.master.after(0, self.print_status, "Failed to get package list.")
                 # Error message is printed by get_installed_packages
                 self.master.after(0, self.set_buttons_state, tk.NORMAL)
                 print("--- Scan thread finished (package list error) ---") # Console print
                 return
            # installed_packages is a set if successful


            # Compare installed packages against the known bloatware database
            installed_bloatware = {}
            all_categories = set()
            for package, info in known_bloatware_db.items():
                if package in installed_packages:
                    installed_bloatware[package] = info # Store info including safety and category
                    all_categories.add(info[2]) # Add category to the set

            self.all_installed_bloatware = installed_bloatware # Store the full list

            if not self.all_installed_bloatware:
                 self.master.after(0, self.print_status, "\nNo known bloatware apps from the database found installed on your device for user 0.")
            else:
                 self.master.after(0, self.print_status, f"\nFound {len(self.all_installed_bloatware)} known bloatware/removable apps installed (for User 0).")
                 # Update category filter options and set default
                 sorted_categories = sorted(list(all_categories))
                 self.master.after(0, self._update_filter_options, sorted_categories)
                 # Apply initial filter (which is 'All' by default)
                 # master.after is used because _apply_filters updates the Treeview
                 self.master.after(0, self._apply_filters)


            self.master.after(0, self.set_buttons_state, tk.NORMAL) # Update GUI state back
            # Process button state is managed within _apply_filters
            print("--- Scan thread finished successfully ---") # Console print

        except Exception as e:
            # Catch any unexpected errors within the thread task itself
            self.master.after(0, self.print_status, f"\nAn unexpected error occurred in the scan thread task: {e}")
            self.master.after(0, self.print_status, "Traceback:\n" + traceback.format_exc()) # Print traceback
            self.master.after(0, self.set_buttons_state, tk.NORMAL) # Ensure buttons are re-enabled
            self.master.after(0, self.process_button.config, {"state": tk.NORMAL}) # Re-enable process button
            print("--- Scan thread finished (UNCAUGHT EXCEPTION) ---") # Console print


    def get_installed_packages(self):
        """Fetches a list of all installed package names for user 0."""
        self.master.after(0, self.print_status, "Fetching list of installed packages from the device for user 0...")
        # Command to explicitly list packages for user 0
        command = ["adb", "shell", "pm", "list", "packages", "--user", "0"]
        result = self.run_adb_command(command, "N/A", "list packages")

        # Handle command execution errors (FileNotFoundError, Timeout, Python error)
        if result.get("error"):
             self.master.after(0, self.print_status, result["message"])
             if result.get("stdout_on_timeout"): # Print output if available (e.g., partial output on timeout)
                  self.master.after(0, self.print_status, "Partial Output:\n" + result["stdout_on_timeout"].strip())
             return {"error": True, "message": "Failed to run pm list packages command."} # Return a consistent error indicator


        # Now check the result of the ADB command itself (returncode, stdout)
        # pm list packages usually returns 0 on success, errors go to stdout
        if result["returncode"] != 0 or "Error:" in result["stdout"] or "Exception:" in result["stdout"] or "SecurityException" in result["stdout"] :
            self.master.after(0, self.print_status, "Failed to get package list from device (ADB Command Error).")
            self.master.after(0, self.print_status, "ADB Output (stdout):\n" + result["stdout"].strip())
            # No stderr with STDOUT redirected to STDOUT
            return {"error": True, "message": "pm list packages returned an error."} # Return a consistent error indicator

        # Parse the output: each line is "package:com.package.name"
        packages = [line.strip().replace("package:", "") for line in result["stdout"].splitlines() if line.strip() and line.startswith("package:")]
        # print(f"Found {len(packages)} packages for user 0 on the device.") # Too verbose for GUI log
        return set(packages) # Use a set for faster lookup

    def _update_filter_options(self, categories):
        """Updates filter combobox options (run in main GUI thread)."""
        self.category_filter_options = ["All"] + categories
        self.category_filter_combobox['values'] = self.category_filter_options
        self.category_filter_combobox.set("All") # Reset to default

        self.safety_filter_combobox['values'] = self.safety_filter_options
        self.safety_filter_combobox.set("All") # Reset to default


    def _apply_filters(self):
        """Applies filters and populates the Treeview with matching apps."""
        if not self.all_installed_bloatware:
            # Clear the tree if no data is loaded
            for item in self.tree.get_children():
                self.tree.delete(item)
            self._item_packages.clear()
            self.process_button.config(state=tk.DISABLED)
            return # No data to filter

        self.master.after(0, self.print_status, "Applying filters...")

        selected_safety = self.safety_filter_combobox.get()
        selected_category = self.category_filter_combobox.get()

        # Clear current list and selections
        for item in self.tree.get_children():
            self.tree.delete(item)
        self._item_packages.clear() # Clear mapping

        # Sort the bloatware list alphabetically by package name
        sorted_bloatware_items = sorted(self.all_installed_bloatware.items())

        if not self.tree_tags_configured:
             self._configure_tree_tags() # Ensure tags are configured if not already


        # Populate Treeview with filtered items
        items_displayed = 0
        for package, info in sorted_bloatware_items:
            description, safety, category = info
            # Check if item matches the filters
            safety_match = (selected_safety == "All" or safety == selected_safety)
            category_match = (selected_category == "All" or category == selected_category)

            if safety_match and category_match:
                # Insert item into the treeview
                item_id = self.tree.insert("", "end",
                                           values=(package, safety, category, description))

                # Store item ID mapped to package name
                self._item_packages[item_id] = package

                # Apply safety color tag and selectable tag
                tags = ['selectable_item'] # Add a generic tag for click handling
                if safety == "RISKY":
                     tags.append('risky_tag')
                elif safety == "CAUTION":
                     tags.append('caution_tag')
                self.tree.item(item_id, tags=tags) # Apply tags
                items_displayed += 1

        self.master.after(0, self.print_status, f"Filter applied. Displaying {items_displayed} items.")
        # Ensure process button is enabled if there are items displayed
        if items_displayed > 0:
             self.master.after(0, self.process_button.config, {"state": tk.NORMAL})
        else:
             self.master.after(0, self.process_button.config, {"state": tk.DISABLED})


    # --- Treeview Click and Selection Handling ---
    def _on_item_click(self, event):
        """Handles clicks on Treeview items to toggle selection."""
        # Get the item ID from the click coordinates
        item_id = self.tree.identify_row(event.y)
        if not item_id or 'selectable_item' not in self.tree.item(item_id, 'tags'): # Ensure it's a selectable item row
            return

        # Toggle the 'selected' tag
        tags = list(self.tree.item(item_id, 'tags'))

        if 'selected' in tags:
            tags.remove('selected')
        else:
            tags.append('selected')

        self.tree.item(item_id, tags=tags)

    def _on_item_double_click(self, event):
        """Optional: Show full description on double click."""
        item_id = self.tree.identify_row(event.y)
        if not item_id:
            return
        # Get values: ("Package", "Safety", "Category", "Description")
        item_values = self.tree.item(item_id, 'values')
        if item_values and len(item_values) > 3:
            package = item_values[0]
            description = item_values[3]
            messagebox.showinfo(f"Details: {package}", f"Package: {package}\n\nDescription:\n{description}")


    def get_selected_item_ids(self):
        """Gets the list of item IDs that are currently selected."""
        selected_ids = []
        # Iterate only through the currently visible items
        for item_id in self.tree.get_children():
            tags = self.tree.item(item_id, 'tags')
            if 'selected' in tags:
                 selected_ids.append(item_id)
        return selected_ids

    def select_all_apps(self):
        """Selects all currently filtered items in the Treeview."""
        for item_id in self.tree.get_children():
            tags = list(self.tree.item(item_id, 'tags'))
            if 'selected' not in tags:
                tags.append('selected')
                self.tree.item(item_id, tags=tags)

    def select_none_apps(self):
        """Deselects all currently filtered items in the Treeview."""
        for item_id in self.tree.get_children():
            tags = list(self.tree.item(item_id, 'tags'))
            if 'selected' in tags:
                tags.remove('selected')
                self.tree.item(item_id, tags=tags)

    def select_by_safety(self, safety_level):
        """Selects apps based on safety level among the currently filtered items."""
        # Clear current selection before selecting by category/level among filtered items
        self.select_none_apps() # Clear current selection
        for item_id in self.tree.get_children():
            # Get safety from item values, not from the main DB, as the item is what's displayed
            package, safety, category, description = self.tree.item(item_id, 'values')
            tags = list(self.tree.item(item_id, 'tags'))
            if safety.upper() == safety_level.upper():
                 if 'selected' not in tags:
                     tags.append('selected')
            self.tree.item(item_id, tags=tags) # Apply changes

    # Add methods like select_by_category_button if needed, similar to select_by_safety


    # --- Process Selected Apps ---
    def start_process(self):
        selected_item_ids = self.get_selected_item_ids()
        if not selected_item_ids:
            messagebox.showwarning("No Selection", "Please select at least one app to process.")
            return

        # Get package names and full details for selected items
        selected_packages_details = []
        for item_id in selected_item_ids:
             package = self._item_packages[item_id] # Get package name from stored mapping
             details = known_bloatware_db.get(package) # Get full details from the main DB
             if details: # Should always be found if it was in the list
                 selected_packages_details.append((package, details[0], details[1], details[2])) # package, description, safety, category

        # Display the confirmation/review window
        self._show_review_window(selected_packages_details)


    def _show_review_window(self, selected_apps_details):
        """Creates and displays a window to review selected apps before processing."""
        review_window = tk.Toplevel(self.master)
        review_window.title("Review Selected Apps")
        review_window.geometry("600x450") # Set a slightly larger default size
        review_window.transient(self.master) # Keep review window on top of main window
        review_window.grab_set() # Modal - block interaction with other windows

        # --- Review List ---
        review_list_frame = ttk.Frame(review_window, padding="10")
        review_list_frame.pack(expand=True, fill=tk.BOTH)

        review_tree = ttk.Treeview(review_list_frame, columns=("Package", "Safety", "Category"), show="headings")
        review_tree.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        review_tree.heading("Package", text="Package Name", anchor=tk.W)
        review_tree.heading("Safety", text="Safety", anchor=tk.W)
        review_tree.heading("Category", text="Category", anchor=tk.W)

        review_tree.column("Package", width=250, stretch=tk.YES)
        review_tree.column("Safety", width=80, stretch=tk.NO)
        review_tree.column("Category", width=100, stretch=tk.NO)

        review_scroll = ttk.Scrollbar(review_list_frame, orient="vertical", command=review_tree.yview)
        review_tree.configure(yscrollcommand=review_scroll.set)
        review_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Populate review tree
        for package, description, safety, category in selected_apps_details:
            item_id = review_tree.insert("", "end", values=(package, safety, category))
            # Apply safety color tag in review window too
            if safety == "RISKY":
                 review_tree.item(item_id, tags=('risky_tag',))
            elif safety == "CAUTION":
                 review_tree.item(item_id, tags=('caution_tag',))

        # Configure tags for colors in the review tree (needs to match main window tags)
        review_tree.tag_configure('risky_tag', foreground='red')
        review_tree.tag_configure('caution_tag', foreground='orange')


        # --- Warning/Summary Text ---
        warning_text = "Review the list below carefully. This action cannot be easily undone."
        risky_selected = any(safety == "RISKY" for _, _, safety, _ in selected_apps_details)
        caution_selected = any(safety == "CAUTION" for _, _, safety, _ in selected_apps_details)

        if risky_selected:
            warning_text += "\n\nWARNING: Apps marked RISKY are included. This may cause significant system issues or bootloops. PROCEED WITH EXTREME CAUTION."
        elif caution_selected:
            warning_text += "\n\nCAUTION: Apps marked CAUTION are included. This may affect features."

        warning_label = ttk.Label(review_window, text=warning_text, wraplength=580, justify=tk.CENTER, font=('TkDefaultFont', 9, 'bold'))
        if risky_selected:
             warning_label.config(foreground='red')
        elif caution_selected:
             warning_label.config(foreground='orange')

        warning_label.pack(pady=10)


        # --- Control Buttons ---
        button_frame = ttk.Frame(review_window, padding="0 0 10 10") # Padding bottom/right
        button_frame.pack(fill=tk.X, anchor=tk.S) # Align buttons to bottom right

        # Store the list of packages to process
        self._packages_to_process_in_thread = [pkg for pkg, _, _, _ in selected_apps_details]


        def on_confirm():
            review_window.destroy() # Close the review window
            # Now call the processing task
            # Use after(0, ...) to ensure review_window is destroyed before starting heavy task
            self.master.after(0, self._start_processing_thread)


        def on_cancel():
            review_window.destroy() # Close the review window
            self.master.after(0, self.print_status, "Processing cancelled by user.")


        confirm_button = ttk.Button(button_frame, text="Confirm and Process", command=on_confirm)
        confirm_button.pack(side=tk.RIGHT, padx=5)

        cancel_button = ttk.Button(button_frame, text="Cancel", command=on_cancel)
        cancel_button.pack(side=tk.RIGHT)


        # Block interaction with the main window until review window is closed
        review_window.transient(self.master)
        review_window.grab_set()
        self.master.wait_window(review_window)


    def _start_processing_thread(self):
         """Starts the processing thread with the pre-selected list."""
         if not self._packages_to_process_in_thread:
             self.print_status("No apps selected for processing.")
             return # Should not happen if review window was shown

         self.set_buttons_state(tk.DISABLED)
         self.process_button.config(state=tk.DISABLED) # Disable process button
         self.print_status("\n--- Starting Removal/Disabling Process ---")

         # Run process in a separate thread
         print("--- Starting process thread ---") # Console print
         # Use the list stored from the review window
         process_thread = threading.Thread(target=self._perform_process_task, args=(self._packages_to_process_in_thread,), daemon=True)
         process_thread.start()
         print("--- Process thread started ---") # Console print
         self._packages_to_process_in_thread = [] # Clear the list once thread is started


    def _perform_process_task(self, selected_packages):
        """Task run in a separate thread for processing apps."""
        print("--- Inside _perform_process_task thread ---") # Console print
        try:
            for package in selected_packages:
                self.master.after(0, self.print_status, f"\nProcessing package: {package}")

                # --- Attempt 1: Uninstall for User 0 ---
                uninstall_command = ["adb", "shell", "pm", "uninstall", "-k", "--user", "0", package]
                uninstall_result = self.run_adb_command(uninstall_command, package, "uninstall")

                # Handle command execution errors or ADB command failure
                if uninstall_result.get("error"):
                     self.master.after(0, self.print_status, uninstall_result["message"])
                     if uninstall_result.get("stdout_on_timeout"): # Print output if available (e.g., partial output on timeout)
                         self.master.after(0, self.print_status, "Partial Output:\n" + uninstall_result["stdout_on_timeout"].strip())
                     self.master.after(0, self.print_status, f"  Failed to process {package} due to execution error.")
                     continue # Move to next package


                # Now check the result of the ADB command itself
                # pm uninstall usually returns 0 on success, errors go to stdout
                if "Success" in uninstall_result["stdout"]:
                    self.master.after(0, self.print_status, f"  Status: Successfully UNINSTALLED {package} for user 0.")
                else:
                    # Uninstall failed, now try to disable
                    self.master.after(0, self.print_status, f"  Uninstall failed for {package}. Trying to disable instead.")
                    # Optional: Print failure output if needed for debugging
                    self.master.after(0, self.print_status, "  Uninstall ADB Output (stdout):\n" + uninstall_result["stdout"].strip())


                    # --- Attempt 2: Disable for User 0 ---
                    disable_command = ["adb", "shell", "pm", "disable-user", "--user", "0", package]
                    disable_result = self.run_adb_command(disable_command, package, "disable")

                    # Handle command execution errors or ADB command failure
                    if disable_result.get("error"):
                        self.master.after(0, self.print_status, disable_result["message"])
                        if disable_result.get("stdout_on_timeout"): # Print output if available (e.g., partial output on timeout)
                            self.master.after(0, self.print_status, "Partial Output:\n" + disable_result["stdout_on_timeout"].strip())
                        self.master.after(0, self.print_status, f"  Failed to process {package} due to execution error.")
                        continue # Move to next package

                    # Check the result of the ADB command itself
                    # pm disable-user usually returns 0 on success, output indicates new state
                    if "new state: disabled-user" in disable_result["stdout"] or "new state: disabled" in disable_result["stdout"]:
                        self.master.after(0, self.print_status, f"  Status: Successfully DISABLED {package} for user 0.")
                    else:
                        self.master.after(0, self.print_status, f"  Status: Failed to UNINSTALL AND DISABLE {package}.")
                        self.master.after(0, self.print_status, "  Disable ADB Output (stdout):\n" + disable_result["stdout"].strip())


                # Add a small visual delay between items if processing many
                # self.master.after(0, time.sleep, 0.1) # Cannot use blocking sleep in thread, needs timer or loop with breaks


            self.master.after(0, self.print_status, "\n--- Process finished ---")
            self.master.after(0, self.print_status, "Review the status messages above.")
            self.master.after(0, self.print_status, "Apps reported as 'UNINSTALLED' or 'DISABLED' should no longer appear in your app drawer.")
            self.master.after(0, self.print_status, "Consider restarting your phone.")
            self.master.after(0, self.set_buttons_state, tk.NORMAL) # Update GUI state back
            self.master.after(0, self.process_button.config, {"state": tk.NORMAL}) # Re-enable process button
            print("--- Process thread finished successfully ---") # Console print

        except Exception as e:
            # Catch any unexpected errors within the thread task itself
            self.master.after(0, self.print_status, f"\nAn unexpected error occurred in the process thread task: {e}")
            self.master.after(0, self.print_status, "Traceback:\n" + traceback.format_exc()) # Print traceback
            self.master.after(0, self.set_buttons_state, tk.NORMAL) # Ensure buttons are re-enabled
            self.master.after(0, self.process_button.config, {"state": tk.NORMAL})
            print("--- Process thread finished (UNCAUGHT EXCEPTION) ---") # Console print


    def set_buttons_state(self, state):
        """Helper to set state of main control buttons."""
        self.scan_button.config(state=state)
        # Process button state is managed separately after scan
        self.select_all_button.config(state=state)
        print(f"--- set_buttons_state: select_all_button state set to {state} ---") # Added print
        self.select_none_button.config(state=state)
        print(f"--- set_buttons_state: select_none_button state set to {state} ---") # Added print
        self.select_safe_button.config(state=state)
        print(f"--- set_buttons_state: select_safe_button state set to {state} ---") # Added print
        self.select_caution_button.config(state=state)
        print(f"--- set_buttons_state: select_caution_button state set to {state} ---") # Added print
        self.select_risky_button.config(state=state)
        print(f"--- set_buttons_state: select_risky_button state set to {state} ---") # Added print
        # Add other selection buttons here


# --- Run the GUI ---
# Add print to confirm we are about to enter the main guard
print("--- About to enter __main__ guard ---")
if __name__ == "__main__":
    # Add print to confirm we entered the main guard
    print("--- Entered __main__ guard ---")
    try:
        print("Creating Tkinter root window...")
        root = tk.Tk()
        print("Creating App instance...")
        app = PocoAppManagerGUI(root)
        print("Starting Tkinter main loop...")
        root.mainloop()
        print("Tkinter main loop exited.")
    except Exception as e:
        print(f"An unhandled exception occurred during GUI startup: {e}")
        traceback.print_exc()

# Add print at the very end of the script file
print("--- Script Finished Execution ---")