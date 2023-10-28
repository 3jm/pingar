import platform
import subprocess
import time
import sys 
import configparser
import os
import ctypes 

CONFIG_FILE = "ping_config.cfg"
REQUIRED_PACKAGES = ["ping3", "colorama"]

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
        from ping3 import ping
        delay = ping(host)
        if delay is not None:
            return delay
        else:
            return None
    except ImportError:
        return None

def colorize_ping(delay):
    from colorama import Fore, Style

    ms = int(delay * 1000)
    if delay < 50:
        return f"{Fore.GREEN}{ms}ms{Style.RESET_ALL}"
    elif 50 <= delay <= 80:
        return f"{Fore.YELLOW}{ms}ms{Style.RESET_ALL}"
    else:
        return f"{Fore.RED}{ms}ms{Style.RESET_ALL}"

def set_window_title(title):
    ctypes.windll.kernel32.SetConsoleTitleW(title)

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
        delay = check_ping(host)
        if delay is not None:
            ping_history.append(delay)
            if len(ping_history) > 10:
                ping_history.pop(0)

            average_ping = sum(ping_history) / len(ping_history)
            colored_ping = colorize_ping(delay)
            print(f"{Fore.LIGHTRED_EX}({platform.node()}){Style.RESET_ALL} >> Ping ({colored_ping}) | Average ({int(average_ping * 1000)}ms)")

        else:
            print(f"{Fore.LIGHTRED_EX}({platform.node()}){Style.RESET_ALL} >> Failed to get response.")

        time.sleep(timeout)

if __name__ == "__main__":
    main()
