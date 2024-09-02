import importlib
import os
import json
import pickle
import pathlib
import shutil

from datetime import datetime

INTERNAL_COMMANDS = ['help', 'load', 'reload', 'unload', 'reset', 'exit', 'prompt', 'cd', 'chdir']
INTERNAL_FIXES = ['cd', 'chdir']
DEFAULT_PROMPT = '[xe] $p>'
INTERNAL_HELP = {'help': ['Shows this message.', 'Displays the description of a specific command, or a list of all possible commands.'], 'reload': ['Reloads a plugin.', 'Reloads a plugin.'], 'load': ['Loads a plugin.', 'Loads extra commands from a file containing them.\nNOTE: External commands may contain malicious software. It is your risk to use them.'], 'unload': ['Unloads a plugin.', 'Unloads a plugin.'], 'reset': ['Resets the command interpreter.', 'Resets all plugins and the prompt variable.'], 'prompt': ['Sets the prompt.', 'Sets the prompt of the command interpreter.'], 'exit': ['Exits the command interpreter.', 'Exits the command interpreter.']}

plugins = []
all_cmds = []
plugin_cmd_dict = {}
module_dict = {}
long_desc_dict = {}
short_desc_dict = {}
prompt = ''

def init_commands():
    for plugin in plugins:
        try:
            module = importlib.import_module(plugin)
        except ModuleNotFoundError:
            print(f'Plugin \'{plugin}\' missing!')
            plugins.remove(plugin)
            write_plugins()
            continue
        
        module_dict[plugin] = module
        
        plugin_commands = [command for command in dir(module) if command.startswith('command_')]
        plugin_cmd_dict[plugin] = plugin_commands
        all_cmds.extend([cmd.removeprefix('command_') for cmd in plugin_commands])

def execute_command(command, argc, argv):
    for plugin, cmds in plugin_cmd_dict.items():
        if f'command_{command}' in cmds:
            getattr(module_dict[plugin], f'command_{command}')(argc, argv)
            return

def init_help():
    help_dict = INTERNAL_HELP
    for plugin in ['internal'] + plugins:
        try:
            with open(f'{plugin}.json') as f:
                help_dict.update(json.load(f))
        except:
            pass

    for command, descriptions in help_dict.items():
        short_desc_dict[command] = descriptions[0]
        long_desc_dict[command] = descriptions[1]

def write_plugins():
    if not os.path.exists('.xeconsole'): os.mkdir('.xeconsole')
    
    with open('.xeconsole/plugins', 'wb') as f:
        pickle.dump(plugins, f)

def write_prompt():
    if not os.path.exists('.xeconsole'): os.mkdir('.xeconsole')
    
    with open('.xeconsole/prompt', 'w') as f:
        f.write(prompt)

def read_prompt():
    global prompt
    try:
        with open('.xeconsole/prompt', 'r') as f:
            prompt = f.read()
            
    except FileNotFoundError:
        prompt = DEFAULT_PROMPT

def read_plugins():
    global plugins
    try:
        with open('.xeconsole/plugins', 'rb') as f:
            plugins = pickle.load(f)
            
    except FileNotFoundError:
        pass

def update_prompt(prompt_template):
    return prompt_template.replace('$n', pathlib.Path.home().drive.rstrip(':')) \
                          .replace('$p', os.getcwd()) \
                          .replace('$t', datetime.now().strftime("%H:%M:%S"))

def reinit():
    global all_cmds, plugin_cmd_dict, module_dict, long_desc_dict, short_desc_dict
    
    all_cmds.clear()
    plugin_cmd_dict.clear()
    module_dict.clear()
    long_desc_dict.clear()
    short_desc_dict.clear()
    
    init_commands()
    init_help()

def main():
    global plugins, prompt
    
    read_plugins()
    read_prompt()
    
    old_prompt = prompt
    
    init_help()
    init_commands()

    running = True
    while running:
        prompt = update_prompt(old_prompt)
        inp = input(prompt)
        argv = inp.split()
        argc = len(argv)

        if not argv:
            continue

        command = argv[0]
        
        if command in all_cmds:
            execute_command(command, argc, argv)
            
        elif command == 'load':
            plugins.append(argv[1])
            write_plugins()
            reinit()

        elif command == 'reload':
            plugins.remove(argv[1])
            reinit()

            plugins.append(argv[1])
            reinit()
            
        elif command == 'unload':
            plugins.remove(argv[1])
            write_plugins()
            reinit()
            
        elif command == 'reset':
            if os.path.exists('.xeconsole'):
                shutil.rmtree('.xeconsole')
            plugins.clear()
            old_prompt = DEFAULT_PROMPT
            reinit()
            
        elif command in {'cd', 'chdir'}:
            os.chdir(' '.join(argv[1:]))
            
        elif command == 'prompt':
            prompt = ' '.join(argv[1:])
            old_prompt = prompt
            write_prompt()
            
        elif command == 'exit':
            running = False
            
        elif command == 'help':
            if argc > 1:
                print(long_desc_dict.get(argv[1], 'No description'))
            else:
                for cmd in INTERNAL_COMMANDS:
                    if cmd not in INTERNAL_FIXES:
                        print(f'{cmd}: {short_desc_dict.get(cmd, "No description")}')

                for cmd in all_cmds:
                    print(f'{cmd}: {short_desc_dict.get(cmd, "No description")}')
        else:
            os.system(inp)

if __name__ == '__main__':
    main()
