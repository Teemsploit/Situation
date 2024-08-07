import os
import ctypes
import platform
import socket
import psutil
import json
import uuid
import re
import logging
import subprocess
import colorama
import sys
import requests
from difflib import get_close_matches

colorama.init()

if os.name == 'nt':  # Windows
    APPDATA = os.getenv('APPDATA', 'C:\\Users\\Default\\AppData\\Roaming')
else:  # macOS/Linux
    directory = os.path.expanduser("~/Library/Application Support/Situation/")
    if not os.path.exists(directory):
        try:
            os.makedirs(directory)
        except Exception as e:
            print(f"{colorama.Fore.RED + colorama.Style.BRIGHT}Error: {colorama.Style.DIM}{e}{colorama.Style.RESET_ALL}")
    APPDATA = directory

LOG_FILE_PATH = os.path.join(APPDATA, 'situation.log')
logging.basicConfig(filename=LOG_FILE_PATH, level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

if os.name == 'nt':
    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32

commands = {}

def split(input_str, sep=" "):
    if not input_str:
        return []
    return input_str.split(sep)

def help_command(args):
    print(colorama.Style.BRIGHT + "Available commands:")
    for command, (func, desc, usage) in commands.items():
        print(f" - {colorama.Fore.GREEN + colorama.Style.BRIGHT}{command}:{colorama.Style.RESET_ALL} {colorama.Fore.MAGENTA}{desc}{colorama.Style.RESET_ALL}")
        print(f"   {colorama.Fore.CYAN}Usage: {colorama.Style.RESET_ALL + colorama.Style.DIM}{usage}{colorama.Style.RESET_ALL}")

def clear_command(args):
    os.system('cls' if os.name == 'nt' else 'clear')

def list_files(args):
    path = args[0] if args else "."
    try:
        files = os.listdir(path)
        for file in files:
            print(file)
    except Exception as e:
        print(f"{colorama.Fore.RED + colorama.Style.BRIGHT}Error: {colorama.Style.DIM}{e}{colorama.Style.RESET_ALL}")
        logging.error(f"Error listing files in {path}: {e}")

def read_file(args):
    if len(args) < 1:
        print(colorama.Fore.RED + colorama.Style.BRIGHT + "Usage: " + colorama.Style.RESET_ALL + "read <file_path>")
        return
    path = args[0]
    try:
        with open(path, 'r') as file:
            content = file.read()
            print(content)
    except Exception as e:
        print(f"{colorama.Fore.RED + colorama.Style.BRIGHT}Error: {colorama.Style.DIM}{e}{colorama.Style.RESET_ALL}")
        logging.error(f"Error reading file {path}: {e}")

def write_file(args):
    if len(args) < 2:
        print(colorama.Fore.RED + colorama.Style.BRIGHT + "Usage: " + colorama.Style.RESET_ALL + "write <file_path> <content>")
        return
    path = args[0]
    content = ' '.join(args[1:])
    try:
        with open(path, 'w') as file:
            file.write(content)
        print(f"Content written to {path}")
    except Exception as e:
        print(f"{colorama.Fore.RED + colorama.Style.BRIGHT}Error: {colorama.Style.DIM}{e}{colorama.Style.RESET_ALL}")
        logging.error(f"Error writing to file {path}: {e}")

def create_file(args):
    if len(args) < 1:
        print(colorama.Fore.RED + colorama.Style.BRIGHT + "Usage: " + colorama.Style.RESET_ALL + "create <file_path>")
        return
    path = args[0]
    try:
        with open(path, 'w') as file:
            pass
        print(f"File \"{path}\" created.")
    except Exception as e:
        print(f"{colorama.Fore.RED + colorama.Style.BRIGHT}Error: {colorama.Style.DIM}{e}{colorama.Style.RESET_ALL}")
        logging.error(f"Error creating file {path}: {e}")

def delete_file(args):
    if len(args) < 1:
        print(colorama.Fore.RED + colorama.Style.BRIGHT + "Usage: " + colorama.Style.RESET_ALL + "delete <file_path>")
        return
    path = args[0]
    try:
        os.remove(path)
        print(f"File {path} deleted.")
    except Exception as e:
        print(f"{colorama.Fore.RED + colorama.Style.BRIGHT}Error: {colorama.Style.DIM}{e}{colorama.Style.RESET_ALL}")
        logging.error(f"Error deleting file {path}: {e}")

def create_folder(args):
    if len(args) < 1:
        print(colorama.Fore.RED + colorama.Style.BRIGHT + "Usage: " + colorama.Style.RESET_ALL + "mkdir <folder_path>")
        return
    path = args[0]
    if os.path.exists(path):
        print(f"{colorama.Fore.RED + colorama.Style.BRIGHT}Error:{colorama.Style.RESET_ALL} Folder \"{path}\" already exists.")
        confirmation = input(f"Do you want to overwrite it? (y/[N]): {colorama.Style.RESET_ALL}")
        if confirmation.lower() != 'y':
            return
    try:
        os.makedirs(path)
        print(f"Folder \"{path}\" created.")
    except Exception as e:
        print(f"{colorama.Fore.RED + colorama.Style.BRIGHT}Error: {colorama.Style.DIM}{e}{colorama.Style.RESET_ALL}")
        logging.error(f"Error creating folder {path}: {e}")

def delete_folder(args):
    if len(args) < 1:
        print(colorama.Fore.RED + colorama.Style.BRIGHT + "Usage: " + colorama.Style.RESET_ALL + "rmdir <folder_path>")
        return
    path = args[0]
    try:
        os.rmdir(path)
        print(f"Folder {path} deleted.")
    except Exception as e:
        print(f"{colorama.Fore.RED + colorama.Style.BRIGHT}Error: {colorama.Style.DIM}{e}{colorama.Style.RESET_ALL}")
        logging.error(f"Error deleting folder {path}: {e}")

def run_batch_script(args):
    if len(args) < 1:
        print(colorama.Fore.RED + colorama.Style.BRIGHT + "Usage: " + colorama.Style.RESET_ALL + "run <script_path>")
        return
    script_path = args[0]
    try:
        if os.name == 'nt':
            subprocess.run(script_path, shell=True, check=True)
        else:
            subprocess.run(['chmod', '+x', script_path])
            subprocess.run(["./" + script_path], shell=True, check=True)
        print(f"{colorama.Fore.GREEN}Script {script_path} executed successfully.{colorama.Style.RESET_ALL}")
    except subprocess.CalledProcessError as e:
        print(f"{colorama.Fore.RED + colorama.Style.BRIGHT}Error running script: {colorama.Style.DIM}{e}{colorama.Style.RESET_ALL}")
        logging.error(f"Error running script {script_path}: {e}")
    except Exception as e:
        print(f"{colorama.Fore.RED + colorama.Style.BRIGHT}Error: {colorama.Style.DIM}{e}{colorama.Style.RESET_ALL}")
        logging.error(f"Error running script {script_path}: {e}")

def download_command(args):
    if len(args) < 1:
        print(colorama.Fore.RED + colorama.Style.BRIGHT + "Usage: " + colorama.Style.RESET_ALL + "download <url>")
        return
    url = args[0]
    try:
        response = requests.get(url)
        if response.status_code == 200:
            filename = os.path.basename(url)
            with open(filename, 'wb') as file:
                file.write(response.content)
            print(f"{colorama.Fore.GREEN}File {filename} downloaded successfully.{colorama.Style.RESET_ALL}")
        else:
            print(f"{colorama.Fore.RED + colorama.Style.BRIGHT}Error downloading file: {colorama.Style.DIM}{response.status_code}{colorama.Style.RESET_ALL}")
            logging.error(f"Error downloading file from {url}: {response.status_code}")
    except Exception as e:
        print(f"{colorama.Fore.RED + colorama.Style.BRIGHT}Error: {colorama.Style.DIM}{e}{colorama.Style.RESET_ALL}")
        logging.error(f"Error downloading file from {url}: {e}")

def ip_command(args):
    try:
        response = requests.get('https://api.ipify.org?format=json')
        data = response.json()
        ip = data['ip']
    except Exception as e:
        print(f"{colorama.Fore.RED + colorama.Style.BRIGHT}Error fetching public IP: {colorama.Style.DIM}{e}{colorama.Style.RESET_ALL}")
        logging.error(f"Error fetching public IP: {e}")
        ip = "Unavailable"

    try:
        local_ip = socket.gethostbyname(socket.gethostname())
    except Exception as e:
        print(f"{colorama.Fore.RED + colorama.Style.BRIGHT}Error fetching local IP: {colorama.Style.DIM}{e}{colorama.Style.RESET_ALL}")
        logging.error(f"Error fetching local IP: {e}")
        local_ip = "Unavailable"
    
    print(f"{colorama.Fore.GREEN}Your public IP is: {colorama.Style.RESET_ALL}{ip}")
    print(f"{colorama.Fore.GREEN}Your local IP is: {colorama.Style.RESET_ALL}{local_ip}")

def exit_command(args):
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')
    print(colorama.Fore.RED + "Exiting Situation..." + colorama.Style.RESET_ALL)
    sys.exit()

def suggest_command(input_cmd, commands):
    close_matches = get_close_matches(input_cmd, commands.keys(), n=1, cutoff=0.6)
    return close_matches[0] if close_matches else None

# function, description, usage
# Register a new command: commands['EXAMPLE'] = (COMMAND_FUNCTION, "Brief description of what the command does", "example [optional arguments]")
commands['help'] = (help_command, "Shows available commands and usage", "help")
commands['clear'] = (clear_command, "Clears the terminal screen", "clear")
commands['list'] = (list_files, "Lists files in the specified directory", "list [directory]")
commands['read'] = (read_file, "Reads and prints the content of a file", "read <file_path>")
commands['write'] = (write_file, "Writes content to a file", "write <file_path> <content>")
commands['create'] = (create_file, "Creates an empty file", "create <file_path>")
commands['delete'] = (delete_file, "Deletes a file", "delete <file_path>")
commands['mkdir'] = (create_folder, "Creates a folder", "mkdir <folder_path>")
commands['rmdir'] = (delete_folder, "Deletes a folder", "rmdir <folder_path>")
commands['run'] = (run_batch_script, "Runs a batch script", "run <script_path>")
commands['download'] = (download_command, "Downloads a file from a URL", "download <url>")
commands['ip'] = (ip_command, "Get your IP", "ip")
commands['exit'] = (exit_command, "Exits Situation", "exit")

def main():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')
    print(colorama.Fore.GREEN + colorama.Style.BRIGHT + "Welcome to Situation. Type 'help' for a list of commands." + colorama.Style.RESET_ALL)
    while True:
        try:
            user_input = input(colorama.Fore.CYAN + "> " + colorama.Style.RESET_ALL)
            tokens = split(user_input)
            if len(tokens) > 0:
                command = tokens[0].lower()
                args = tokens[1:]
                if command in commands:
                    func, _, _ = commands[command]
                    func(args)
                else:
                    suggestion = suggest_command(command, commands)
                    if suggestion:
                        print(f"{colorama.Fore.RED}Unknown command:{colorama.Style.RESET_ALL} {command}")
                        print(f"{colorama.Fore.RED}Did you mean:{colorama.Style.RESET_ALL} {suggestion}")
                    else:
                        print(f"{colorama.Fore.RED}Unknown command:{colorama.Style.RESET_ALL} {command}")
                        print(f"{colorama.Fore.RED}For a list of commands run:{colorama.Style.RESET_ALL} help")
        except KeyboardInterrupt:
            if os.name == 'nt':
                os.system('cls')
            else:
                os.system('clear')
            print(colorama.Fore.RED + "Exiting Situation..." + colorama.Style.RESET_ALL)
            sys.exit()

if __name__ == "__main__":
    main()
