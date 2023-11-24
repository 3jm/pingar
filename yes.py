import platform
import subprocess
import time
import sys 
import configparser
import os
import ctypes 
from ping3 import ping


CONFIG_FILE = "ping_config.cfg"
REQUIRED_PACKAGES = ["ping3", "colorama", "scapy"]

def check_packages():
    missing_packages = [package for package in REQUIRED_PACKAGES if not is_package_installed(package)]
    return missing_packages

def is_package_installed(package):
    try:
        subprocess.check_output([sys.executable, "-m", "pip", "show", package])
        return True
    except subprocess.CalledProcessError:
        return False

def install_packages(packages):
    for package in packages:
        subprocess.call([sys.executable, "-m", "pip", "install", package])

def load_config():
    config = configparser.ConfigParser()
    if os.path.exists(CONFIG_FILE):
        config.read(CONFIG_FILE)
        return config
    else:
        return None

def save_config(timeout):
    try:
        from colorama import Fore, Style, init
        init(autoreset=True)
    except ImportError:
        pass
    config = configparser.ConfigParser()
    config["Settings"] = {"Timeout": str(timeout)}
    with open(CONFIG_FILE, "w") as configfile:
        config.write(configfile)
    print(f"{Fore.LIGHTRED_EX}({platform.node()}){Style.RESET_ALL} >> Saved settings to config.")

def get_timeout_from_user():
    try:
        from colorama import Fore, Style, init
        init(autoreset=True)
    except ImportError:
        pass
    while True:
        try:
            timeout = float(input(f"{Fore.LIGHTRED_EX}({platform.node()}){Style.RESET_ALL} >> Enter the timeout value in seconds (e.g., 0.1): "))
            return timeout
        except ValueError:
            print(f"{Fore.LIGHTRED_EX}({platform.node()}){Style.RESET_ALL} >> Invalid input. Please enter a valid number.")

def check_ping(host):
    try:
        delay = ping(host, timeout=2)
        if delay is not None:
            success = True
        else:
            success = False
        return success, delay
    except Exception as e:
        print(f"Error during ping: {e}")
        return False, None

from scapy.all import ARP, Ether, srp
import ipaddress

def discover_devices(ip_range):
    devices = []
    try:
        # Create ARP request packet
        arp = ARP(pdst=ip_range)
        ether = Ether(dst="ff:ff:ff:ff:ff:ff")
        packet = ether/arp

        # Send ARP request and receive response
        result = srp(packet, timeout=3, verbose=0)[0]

        # Extract devices from the response
        for sent, received in result:
            devices.append({'ip': received.psrc, 'mac': received.hwsrc})

        return devices

    except Exception as e:
        print(f"Error during device discovery: {e}")
        return devices

def get_network_devices():
    network_ip = "192.168.0.1/24"  # Adjust the network IP range as per your network configuration
    devices = discover_devices(network_ip)
    return devices

from colorama import Fore, Style

def colorize_ping(delay):
    ms = int(delay * 1000)
    
    if ms < 65:
        color = Fore.GREEN
    elif 65 <= ms <= 110:
        color = Fore.YELLOW
    else:
        color = Fore.RED

    return f"{color}{ms}ms{Style.RESET_ALL}"

def set_window_title(title):
    ctypes.windll.kernel32.SetConsoleTitleW(title)

def print_device_count():
    devices = get_network_devices()
    device_count = len(devices)
    
    if device_count > 0:
        return f" | {device_count} devices connected"
    else:
        return " | No devices found"


def main():
    missing_packages = check_packages()

    if missing_packages:
        print(f"({platform.node()}) >> You are missing the following packages to run this program: {', '.join(missing_packages)}")
        install_choice = input(f"({platform.node()}) >> Install them? (Y/N): ").lower()

        if install_choice == "y":
            install_packages(missing_packages)
            print("Packages installed. Restarting the program.")
            time.sleep(2)
            os.execv(sys.executable, [sys.executable] + sys.argv)
        else:
            print("Goodbye!")
            return

    try:
        from colorama import Fore, Style, init
        init(autoreset=True)
    except ImportError:
        pass

    config = load_config()

    if config is not None and "Settings" in config and "Timeout" in config["Settings"]:
        print(f"{Fore.LIGHTRED_EX}({platform.node()}){Style.RESET_ALL} >> Loaded settings.")
        timeout = float(config["Settings"]["Timeout"])
    else:
        timeout = get_timeout_from_user()
        save_config(timeout)

    host = "1.1.1.1" 
    ping_history = []

    set_window_title(f"{platform.node()}!")

    print(f"{Fore.LIGHTRED_EX}({platform.node()}){Style.RESET_ALL} >> Pinging {host}... (Timeout: {timeout}s)")

    while True:
        success, delay = check_ping(host)
        if success:
            ping_history.append(delay)
            if len(ping_history) > 10:
                ping_history.pop(0)

            average_ping = sum(filter(None, ping_history)) / len(list(filter(None, ping_history)))
            colored_ping = colorize_ping(delay)
            device_count_info = print_device_count()
            print(f"{Fore.LIGHTRED_EX}({platform.node()}){Style.RESET_ALL} >> Ping ({colored_ping}) | Average ({int(average_ping * 1000)}ms){device_count_info}")

        else:
            print(f"{Fore.LIGHTRED_EX}({platform.node()}){Style.RESET_ALL} >> Packet loss detected.")

        time.sleep(timeout)

if __name__ == "__main__":
    main()
