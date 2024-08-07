import os
import ctypes
import platform
import socket
import psutil
import json
import uuid
import re
import logging

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
    for command in commands.keys():
        print(f" - {command}")

commands['help'] = help_command

def main():
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
