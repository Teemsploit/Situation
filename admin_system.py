import os
import ctypes
import platform
import socket
import psutil
import json
import uuid
import re
import logging
import importlib.util

APPDATA = os.getenv('APPDATA')
LOG_FILE_PATH = os.path.join(APPDATA, 'situation.log')
logging.basicConfig(filename=LOG_FILE_PATH, level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

SW_SHOW = 5
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

commands = {}

plugins_directory = os.path.join(APPDATA, "situation_plugins")

def split(input_str, sep=" "):
    if not input_str:
        return []
    return input_str.split(sep)

def load_plugins():
    if not os.path.exists(plugins_directory):
        os.makedirs(plugins_directory)
    
    for filename in os.listdir(plugins_directory):
        if filename.endswith('.py'):
            plugin_path = os.path.join(plugins_directory, filename)
            spec = importlib.util.spec_from_file_location(filename[:-3], plugin_path)
            plugin_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(plugin_module)
            plugin_name = filename[:-3]
            commands[plugin_name] = plugin_module.main

def help_command(args):
    print("Available commands:")
    for command in commands.keys():
        print(f" - {command}")

commands['help'] = help_command

def show_console():
    kernel32.AllocConsole()
    console_handle = kernel32.GetConsoleWindow()
    user32.ShowWindow(console_handle, SW_SHOW)
    print("Console shown.")

def main():
    show_console()
    load_plugins()
    print("Welcome to Situation. Type 'help' for a list of commands.")
    while True:
        try:
            user_input = input("Input: ")
            tokens = split(user_input)
            if len(tokens) > 0:
                command = tokens[0].lower()
                args = tokens[1:]
                if command in commands:
                    commands[command](args)
                else:
                    print(f"Unknown command: {command}")
        except KeyboardInterrupt:
            print("\nExiting Situation.")
            sys.exit()

if __name__ == "__main__":
    main()
