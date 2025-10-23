import os
import shutil
import subprocess
import requests
import time
import winreg
import wmi
import win32com.client
import re
import logging
from typing import Optional, Dict
import sys
import contextlib

CONSTANTS = {
    'DNS_SERVER': '8.8.8.8',
    'PING_COUNT': 1,
    'CHUNK_SIZE': 8192,
    'PROGRESS_BAR_LENGTH': 30,
    'WMIC_TIMEOUT': 10,
    'CYCLE_SLEEP_TIME': 0.3,
    'PRINTER_PATH': r"\\s000rdl01\FollowmeS000RDL01",
    'SYMANTEC_PATH': r"C:\Program Files\Symantec\Symantec Endpoint Protection\SepLiveUpdate.exe",
    'HIGH_PERFORMANCE_GUID': '8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c',
    'ULTIMATE_PERFORMANCE_GUID': 'e9a42b02-d5df-448d-aa00-03f14749eb61'
}

URLS = {
    'HP_SUPPORT': "https://ftp.hp.com/pub/softpaq/sp108501-109000/sp108770.exe",
    'GENERIC_SUPPORT': "https://ftp.hp.com/pub/softpaq/sp108501-109000/sp108770.exe",
    # Fallbacks for manufacturer checks below (mapped to the same generic package)
    'DELL_SUPPORT': "https://ftp.hp.com/pub/softpaq/sp108501-109000/sp108770.exe",
    'LENOVO_SUPPORT': "https://ftp.hp.com/pub/softpaq/sp108501-109000/sp108770.exe",
}

CYCLE_IDS = {
    "Application Deployment Evaluation Cycle": "{00000000-0000-0000-0000-000000000121}",
    "Discovery Data Collection Cycle": "{00000000-0000-0000-0000-000000000003}",
    "File Collection Cycle": "{00000000-0000-0000-0000-000000000010}",
    "Hardware Inventory Cycle": "{00000000-0000-0000-0000-000000000001}",
    "Machine Policy Retrieval & Evaluation Cycle": "{00000000-0000-0000-0000-000000000022}",
    "Software Inventory Cycle": "{00000000-0000-0000-0000-000000000002}",
    "Software Metering Usage Report Cycle": "{00000000-0000-0000-0000-000000000031}",
    "Software Updates Assignments Evaluation Cycle": "{00000000-0000-0000-0000-000000000108}",
    "Software Updates Deployment Evaluation Cycle": "{00000000-0000-0000-0000-000000000113}",
    "User Policy Retrieval & Evaluation Cycle": "{00000000-0000-0000-0000-000000000026}",
    "Windows Installer Source List Update Cycle": "{00000000-0000-0000-0000-000000000032}"
}

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('auto_setup.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ---------------------------
# Console helpers
# ---------------------------

def print_separator(title: Optional[str] = None, width: int = 70) -> None:
    """Print a visual separator to the console."""
    bar = "-" * width
    print("\n" + bar)
    if title:
        print(title.center(width))
        print(bar + "\n")
    else:
        print(bar + "\n")

def wait_for_enter() -> None:
    """Wait for user to press Enter."""
    input("\nPress Enter to continue...")

# ---------------------------
# Subprocess & networking
# ---------------------------

def safe_subprocess_run(command: str, timeout: int = 30, encoding: str = 'cp857', **kwargs) -> subprocess.CompletedProcess:
    """Run a subprocess command safely with timeout and consistent encoding."""
    try:
        return subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            encoding=encoding,
            timeout=timeout,
            **kwargs
        )
    except subprocess.TimeoutExpired:
        logger.warning(f"Command timed out: {command}")
        raise
    except Exception as e:
        logger.error(f"Command execution error: {command} - {e}")
        raise

def get_network_info() -> Dict[str, str]:
    """Retrieve basic network information safely."""
    network_info: Dict[str, str] = {}
    try:
        import socket
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        network_info['hostname'] = hostname
        network_info['local_ip'] = local_ip

        result = safe_subprocess_run('ipconfig', timeout=10)
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            for line in lines:
                if 'IPv4' in line and ('192.168' in line or '10.' in line):
                    network_info['adapter_ip'] = line.strip()
                    break
    except Exception as e:
        logger.warning(f"Could not retrieve network info: {e}")

    return network_info

def measure_ping_time() -> Optional[str]:
    """Measure ping time to the configured DNS server."""
    try:
        ping_result = safe_subprocess_run(f'ping -n 1 {CONSTANTS["DNS_SERVER"]}', timeout=10)
        if ping_result.returncode == 0:
            for line in ping_result.stdout.split('\n'):
                if 'Zaman=' in line or 'time=' in line:
                    time_part = line.split('Zaman=')[-1].split('ms')[0] if 'Zaman=' in line else line.split('time=')[-1].split('ms')[0]
                    return f"{time_part}ms"
    except Exception as e:
        logger.warning(f"Ping time could not be measured: {e}")
    return None

def check_internet_connection(verbose: bool = False) -> bool:
    """Check internet connectivity by pinging a DNS server."""
    if verbose:
        print_separator("INTERNET CONNECTIVITY CHECK")

        network_info = get_network_info()
        if network_info.get('hostname'):
            print(f"Host Name: {network_info['hostname']}")
        if network_info.get('local_ip'):
            print(f"Local IP: {network_info['local_ip']}")
        if network_info.get('adapter_ip'):
            print(f"Adapter: {network_info['adapter_ip']}")

    try:
        response = os.system(f"ping -n {CONSTANTS['PING_COUNT']} {CONSTANTS['DNS_SERVER']} > nul")
        connection_ok = (response == 0)

        if verbose:
            if connection_ok:
                print("✓ Internet connection is available")
                print(f"✓ DNS server ({CONSTANTS['DNS_SERVER']}) is reachable")
                print("✓ Network link appears active")

                ping_time = measure_ping_time()
                if ping_time:
                    print(f"Ping: {ping_time}")
            else:
                print("✗ No internet connection detected")
                print(f"✗ DNS server ({CONSTANTS['DNS_SERVER']}) is not reachable")
                print("✗ Network connectivity issue detected")
                print("  Please check your internet connection.")

        return connection_ok

    except Exception as e:
        logger.error(f"Internet connectivity check failed: {e}")
        if verbose:
            print("✗ Unable to verify internet connectivity")
            print("  Please check your network settings.")
        return False
    finally:
        if verbose:
            print_separator()

# ---------------------------
# Filesystem utilities
# ---------------------------

def copy_file(src: str, dst: str) -> bool:
    """Copy a file from src to dst."""
    try:
        if not os.path.exists(src):
            print(f"Source file not found: {src}")
            return False

        dst_dir = os.path.dirname(dst)
        if dst_dir and not os.path.exists(dst_dir):
            os.makedirs(dst_dir)

        shutil.copy2(src, dst)
        print(f"File copied successfully: {src} -> {dst}")
        return True
    except Exception as e:
        logger.error(f"File copy error: {e}")
        print(f"Error: {e}")
        return False

# ---------------------------
# OEM / Manufacturer
# ---------------------------

def get_manufacturer() -> str:
    """Get the system manufacturer safely."""
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\SystemInformation") as key:
            manufacturer = winreg.QueryValueEx(key, "SystemManufacturer")[0].lower()
            return manufacturer
    except Exception as e:
        logger.warning(f"Could not read manufacturer: {e}")
        return ""

# ---------------------------
# Download helper
# ---------------------------

def download_with_progress(url: str, file_path: str) -> bool:
    """Download a file with a simple progress bar."""
    try:
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

        if 'drive.google.com' in url:
            print("Downloading from Google Drive...")
            session = requests.Session()
            session.headers.update(headers)

            response = session.get(url, stream=True, verify=False, timeout=30)

            for key, value in response.cookies.items():
                if key.startswith('download_warning'):
                    url = url + '&confirm=' + value
                    break

            response = session.get(url, stream=True, verify=False, timeout=30)
        else:
            response = requests.get(url, stream=True, verify=False, timeout=30, headers=headers)

        response.raise_for_status()

        total_size = int(response.headers.get('content-length', 0))
        if total_size == 0:
            print("Unable to determine file size; downloading...")

        downloaded = 0
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=CONSTANTS['CHUNK_SIZE']):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)

                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        mb_downloaded = downloaded / (1024 * 1024)
                        mb_total = total_size / (1024 * 1024)
                        filled_length = int(CONSTANTS['PROGRESS_BAR_LENGTH'] * downloaded // total_size)
                        bar = '█' * filled_length + '-' * (CONSTANTS['PROGRESS_BAR_LENGTH'] - filled_length)
                        print(f'\rDownloading: [{bar}] {percent:.1f}% ({mb_downloaded:.1f}MB/{mb_total:.1f}MB)', end='', flush=True)
                    else:
                        mb_downloaded = downloaded / (1024 * 1024)
                        print(f'\rDownloading: {mb_downloaded:.1f}MB', end='', flush=True)

        print()
        return True

    except requests.RequestException as e:
        logger.error(f"Download error: {e}")
        print(f"Download error: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected download error: {e}")
        print(f"Unexpected error: {e}")
        return False

# ---------------------------
# Support Assistant installer
# ---------------------------

def install_support_assistant() -> None:
    """Download and open the Support Assistant installer (OEM-dependent)."""
    print_separator("SUPPORT ASSISTANT INSTALLER")

    if not check_internet_connection():
        print("No internet connection. Please check your network and try again.")
        print_separator()
        return

    print("Downloading and preparing Support Assistant...")

    try:
        manufacturer = get_manufacturer()
        if "dell" in manufacturer:
            print("Dell system detected. Downloading Dell Support Assistant package...")
            url = URLS['DELL_SUPPORT']
        elif "lenovo" in manufacturer:
            print("Lenovo system detected. Downloading Lenovo Support Assistant package...")
            url = URLS['LENOVO_SUPPORT']
        else:
            print("HP/Generic system detected. Downloading HP Support Assistant package...")
            url = URLS['HP_SUPPORT']

        current_dir = os.path.dirname(os.path.abspath(__file__))
        auto_setup_dir = os.path.join(current_dir, "autoSetup")
        os.makedirs(auto_setup_dir, exist_ok=True)
        download_path = os.path.join(auto_setup_dir, "Support_Assistant.exe")

        print("Starting download...")
        if download_with_progress(url, download_path):
            print("\nDownload completed. Opening download folder...")
            try:
                folder_path = os.path.dirname(download_path)
                subprocess.run(['explorer', folder_path], check=True)
            except Exception as e:
                logger.warning(f"Could not open Explorer: {e}")
                print(f"Could not open Explorer: {e}")
                print(f"File path: {download_path}")
                print("Please navigate to the folder and run the installer manually.")
        else:
            print("Download failed.")

    except Exception as e:
        logger.error(f"Support Assistant install error: {e}")
        print(f"Support Assistant install error: {e}")

    print_separator()

# ---------------------------
# SCCM client cycles
# ---------------------------

def check_sccm_service() -> bool:
    """Check if the SCCM (ccmexec) service exists/runs."""
    try:
        result = safe_subprocess_run('sc query ccmexec', timeout=10)
        return "RUNNING" in result.stdout or "STOPPED" in result.stdout
    except Exception as e:
        logger.warning(f"SCCM service check error: {e}")
        return False

def trigger_single_cycle(cycle_name: str, cycle_id: str) -> bool:
    """Trigger a single SCCM client schedule cycle."""
    try:
        wmic_command = f'wmic /namespace:\\\\root\\ccm path sms_client CALL TriggerSchedule "{cycle_id}"'
        result = safe_subprocess_run(wmic_command, timeout=CONSTANTS['WMIC_TIMEOUT'])

        if result.returncode == 0 and "ReturnValue = 0" in result.stdout:
            return True

        ps_command = f'powershell -Command "Invoke-WmiMethod -Namespace root\\ccm -Class SMS_CLIENT -Name TriggerSchedule -ArgumentList \\"{cycle_id}\\""'
        alt_result = safe_subprocess_run(ps_command, timeout=CONSTANTS['WMIC_TIMEOUT'])
        return alt_result.returncode == 0

    except subprocess.TimeoutExpired:
        logger.warning(f"SCCM cycle timeout: {cycle_name}")
        return False
    except Exception as e:
        logger.error(f"SCCM cycle trigger error - {cycle_name}: {e}")
        return False

def trigger_sccm_client_cycles() -> None:
    """Trigger all common SCCM client action cycles."""
    print_separator("TRIGGER SCCM CLIENT CYCLES")
    print("Starting Microsoft Configuration Manager (SCCM) client cycles...")
    print(f"Total cycles to trigger: {len(CYCLE_IDS)}\n")

    if not check_sccm_service():
        print("❌ SCCM client not found on this system.")
        print_separator()
        return

    success_count = 0
    failure_count = 0

    for cycle_name, cycle_id in CYCLE_IDS.items():
        if trigger_single_cycle(cycle_name, cycle_id):
            success_count += 1
        else:
            failure_count += 1
        time.sleep(CONSTANTS['CYCLE_SLEEP_TIME'])

    print("\nSummary:")
    print(f"  ✓ Success:   {success_count}")
    print(f"  ✗ Failed:    {failure_count}")
    print(f"  ■ Total:     {len(CYCLE_IDS)}")

    if success_count > 0:
        print("\nClient cycles have been triggered in the background.")
    else:
        print("\nNo cycles could be triggered.")

    print_separator()

# ---------------------------
# Power configuration
# ---------------------------

def create_ultimate_performance_plan() -> Optional[str]:
    """Create the 'Ultimate Performance' power plan and return its GUID."""
    try:
        result = subprocess.run(
            ['powercfg', '/DUPLICATESCHEME', CONSTANTS['ULTIMATE_PERFORMANCE_GUID']],
            capture_output=True,
            text=True,
            check=True
        )
        match = re.search(r'Power Scheme GUID:\s+([a-fA-F0-9\-]+)', result.stdout)
        if match:
            return match.group(1)
    except subprocess.CalledProcessError as e:
        logger.warning(f"Could not create Ultimate Performance plan: {e}")
    except Exception as e:
        logger.error(f"Power plan creation error: {e}")

    return None

def set_power_scheme(guid: str) -> bool:
    """Activate the given power scheme GUID."""
    try:
        subprocess.run(['powercfg', '/S', guid], check=True)
        return True
    except Exception as e:
        logger.error(f"Power scheme activation error: {e}")
        return False

def configure_power_settings() -> None:
    """Apply no-sleep / high-availability power settings."""
    power_commands = [
        'powercfg /change monitor-timeout-ac 0',
        'powercfg /change monitor-timeout-dc 0',
        'powercfg /change disk-timeout-ac 0',
        'powercfg /change disk-timeout-dc 0',
        'powercfg /change standby-timeout-ac 0',
        'powercfg /change standby-timeout-dc 0'
    ]
    for command in power_commands:
        try:
            subprocess.run(command, shell=True, check=True)
        except Exception as e:
            logger.warning(f"Power setting command failed - {command}: {e}")

def optimize_power_settings_and_sleep() -> None:
    """Create/enable Ultimate Performance (or High Performance) and disable sleep."""
    print_separator("POWER PROFILE & SLEEP SETTINGS")
    print("Optimizing power configuration and disabling sleep...")

    try:
        ultimate_guid = create_ultimate_performance_plan()

        if ultimate_guid:
            print(f"[+] New plan GUID: {ultimate_guid}")
            if set_power_scheme(ultimate_guid):
                print("[✓] Ultimate Performance plan activated.")
            else:
                print("[!] Could not activate Ultimate Performance. Falling back to High Performance.")
                set_power_scheme(CONSTANTS['HIGH_PERFORMANCE_GUID'])
        else:
            print("[!] Could not create Ultimate Performance. Using High Performance.")
            set_power_scheme(CONSTANTS['HIGH_PERFORMANCE_GUID'])

        configure_power_settings()
        print("Power settings applied. Sleep disabled (Ultimate/High Performance active).")

    except Exception as e:
        logger.error(f"Power settings error: {e}")
        print(f"Power settings error: {e}")

    print_separator()

# ---------------------------
# Printer connection
# ---------------------------

def connect_printer() -> None:
    """Connect the shared printer."""
    print_separator("PRINTER CONNECTION - s000rdl01")
    print("Connecting to printer...")

    try:
        subprocess.run(
            [
                "rundll32",
                "printui.dll,PrintUIEntry",
                "/in",
                f"/n{CONSTANTS['PRINTER_PATH']}"
            ],
            check=True,
            shell=True
        )
        print(f"✅ Printer connected: {CONSTANTS['PRINTER_PATH']}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Printer connection error: {e}")
        print(f"❌ Printer connection failed. Error: {e}")
    except Exception as e:
        logger.error(f"Unexpected printer error: {e}")
        print(f"❌ Unexpected error: {e}")

    print_separator()

# ---------------------------
# Symantec update
# ---------------------------

def update_symantec() -> None:
    """Run Symantec LiveUpdate if installed."""
    print_separator("SYMANTEC DEFINITION UPDATE")
    print("Starting Symantec update...")

    try:
        if not os.path.exists(CONSTANTS['SYMANTEC_PATH']):
            print("Symantec not found.")
            print_separator()
            return

        cmd_command = f'"{CONSTANTS["SYMANTEC_PATH"]}" /u'
        result = safe_subprocess_run(cmd_command, timeout=60)

        if result.returncode == 0:
            print("Symantec update completed.")
        else:
            print("Symantec update failed.")
            if result.stderr:
                print(result.stderr)

    except Exception as e:
        logger.error(f"Symantec update error: {e}")
        print(f"Symantec update error: {e}")

    print_separator()

# ---------------------------
# Group policy update
# ---------------------------

def update_group_policy() -> None:
    """Force a Group Policy update."""
    print_separator("GROUP POLICY UPDATE")
    print("Updating Group Policy...")

    try:
        result = safe_subprocess_run('gpupdate /force', timeout=120)

        if result.returncode == 0:
            print("Group Policy updated successfully.")
            if result.stdout:
                print(result.stdout)
        else:
            print("Group Policy update failed.")
            if result.stderr:
                print(result.stderr)

    except Exception as e:
        logger.error(f"Group Policy error: {e}")
        print(f"Group Policy error: {e}")

    print_separator()

# ---------------------------
# Full automation
# ---------------------------

def run_full_automatic_setup() -> None:
    """Run all automated setup operations in sequence."""
    print("=== STARTING AUTOMATIC SETUP ===\n")

    operations = [
        ("Installing Support Assistant...", install_support_assistant),
        ("Triggering SCCM client actions...", trigger_sccm_client_cycles),
        ("Optimizing power settings...", optimize_power_settings_and_sleep),
        ("Connecting printer...", connect_printer),
        ("Updating Symantec...", update_symantec),
        ("Updating Group Policy...", update_group_policy),
    ]

    for i, (description, operation) in enumerate(operations, 1):
        print(f"{i} -> {description}")
        try:
            operation()
        except Exception as e:
            logger.error(f"Automatic setup error - {description}: {e}")
            print(f"❌ Error during: {description} -> {e}")
        print()

    print_separator("AUTOMATIC SETUP COMPLETED")

# ---------------------------
# Main menu
# ---------------------------

def main_menu() -> None:
    """Interactive main menu loop."""
    print_separator("USAGE MENU")

    menu_options = {
        "1": ("Automatic Setup (All Steps)", run_full_automatic_setup),
        "2": ("Install Support (Driver Update)", install_support_assistant),
        "3": ("Trigger SCCM Client Actions", trigger_sccm_client_cycles),
        "4": ("Optimize Power & Sleep Settings", optimize_power_settings_and_sleep),
        "5": ("Connect Printer", connect_printer),
        "6": ("Update Symantec", update_symantec),
        "7": ("Update Group Policy", update_group_policy),
        "8": ("Manual File Copy", None),  # calls copy_file with prompts
        "9": ("Internet Connectivity Test", lambda: check_internet_connection(True)),
        "10": ("Clear Console", lambda: os.system('cls'))
    }

    while True:
        for key, (description, _) in menu_options.items():
            print(f"{key}. {description}")
        print("0. Exit")

        choice = input("Your choice: ").strip()

        if choice in menu_options:
            description, operation = menu_options[choice]

            if choice == "8":
                src = input("Enter source file path: ").strip()
                dst = input("Enter destination folder path: ").strip()
                if src and dst:
                    copy_file(src, dst)
            elif operation:
                try:
                    operation()
                    if choice != "10":
                        wait_for_enter()
                except Exception as e:
                    logger.error(f"Menu operation error - {description}: {e}")
                    print(f"❌ Error during operation: {e}")
                    wait_for_enter()

        elif choice == "01":  # Hidden developer exit
            print("Exiting (Developer Mode)...")
            break
        elif choice == "0":
            print("Exiting...")
            try:
                os.system('taskkill /f /im cmd.exe')
            except Exception:
                pass
            break
        else:
            print("Invalid selection!")

# ---------------------------
# Entrypoint
# ---------------------------

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n\nProgram terminated by user.")
        sys.exit(0)
    except Exception as e:
        logger.critical(f"Critical error: {e}")
        print(f"Critical error: {e}")
        sys.exit(1)
