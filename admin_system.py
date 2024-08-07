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

APPDATA = os.getenv('APPDATA')
LOG_FILE_PATH = os.path.join(APPDATA, 'situation.log')
logging.basicConfig(filename=LOG_FILE_PATH, level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

SW_SHOW = 5
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

commands = {}

def split(input_str, sep=" "):
    if not input_str:
        return []
    return input_str.split(sep)

def help_command(args):
    print("Available commands:")
    for command, (func, desc, usage) in commands.items():
        print(f" - {command}: {desc}")
        print(f"   Usage: {usage}")

def clear_command(args):
    os.system('cls' if os.name == 'nt' else 'clear')

def list_files(args):
    path = args[0] if args else "."
    try:
        files = os.listdir(path)
        for file in files:
            print(file)
    except Exception as e:
        print(f"Error: {e}")
        logging.error(f"Error listing files in {path}: {e}")

def read_file(args):
    if len(args) < 1:
        print("Usage: read <file_path>")
        return
    path = args[0]
    try:
        with open(path, 'r') as file:
            content = file.read()
            print(content)
    except Exception as e:
        print(f"Error: {e}")
        logging.error(f"Error reading file {path}: {e}")

def write_file(args):
    if len(args) < 2:
        print("Usage: write <file_path> <content>")
        return
    path = args[0]
    content = ' '.join(args[1:])
    try:
        with open(path, 'w') as file:
            file.write(content)
        print(f"Content written to {path}")
    except Exception as e:
        print(f"Error: {e}")
        logging.error(f"Error writing to file {path}: {e}")

def create_file(args):
    if len(args) < 1:
        print("Usage: create <file_path>")
        return
    path = args[0]
    try:
        with open(path, 'w') as file:
            pass
        print(f"File {path} created.")
    except Exception as e:
        print(f"Error: {e}")
        logging.error(f"Error creating file {path}: {e}")

def delete_file(args):
    if len(args) < 1:
        print("Usage: delete <file_path>")
        return
    path = args[0]
    try:
        os.remove(path)
        print(f"File {path} deleted.")
    except Exception as e:
        print(f"Error: {e}")
        logging.error(f"Error deleting file {path}: {e}")

def create_folder(args):
    if len(args) < 1:
        print("Usage: mkdir <folder_path>")
        return
    path = args[0]
    try:
        os.makedirs(path)
        print(f"Folder {path} created.")
    except Exception as e:
        print(f"Error: {e}")
        logging.error(f"Error creating folder {path}: {e}")

def delete_folder(args):
    if len(args) < 1:
        print("Usage: rmdir <folder_path>")
        return
    path = args[0]
    try:
        os.rmdir(path)
        print(f"Folder {path} deleted.")
    except Exception as e:
        print(f"Error: {e}")
        logging.error(f"Error deleting folder {path}: {e}")

def run_batch_script(args):
    if len(args) < 1:
        print("Usage: run <script_path>")
        return
    script_path = args[0]
    try:
        subprocess.run(script_path, shell=True, check=True)
        print(f"Script {script_path} executed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error running script: {e}")
        logging.error(f"Error running script {script_path}: {e}")
    except Exception as e:
        print(f"Error: {e}")
        logging.error(f"Error running script {script_path}: {e}")

# function, description, usage
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

def main():
    print("Welcome to Situation. Type 'help' for a list of commands.")
    while True:
        try:
            user_input = input("> ")
            tokens = split(user_input)
            if len(tokens) > 0:
                command = tokens[0].lower()
                args = tokens[1:]
                if command in commands:
                    func, _, _ = commands[command]
                    func(args)
                else:
                    print(f"Unknown command: {command}")
        except KeyboardInterrupt:
            print("\nExiting Situation.")
            sys.exit()

if __name__ == "__main__":
    main()
