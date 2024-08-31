import importlib
import os
import json
import pickle
import pathlib
from datetime import datetime

INTERNAL_COMMANDS = ['help', 'load', 'unload', 'reset', 'exit', 'prompt', 'cd', 'chdir']
INTERNAL_FIXES = ['cd', 'chdir']
DEFAULT_PROMPT = '$n>'

plugins = []
all_cmds = []
plugin_cmd_dict = {}
module_dict = {}
long_desc_dict = {}
short_desc_dict = {}
prompt = ''

def init_commands():
    for plugin in plugins:
        module = importlib.import_module(plugin)
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
    help_dict = {}
    json_files = ['internal'] + plugins
    for file in json_files:
        with open(f'{file}.json') as f:
            help_dict.update(json.load(f))

    for command, descriptions in help_dict.items():
        short_desc_dict[command] = descriptions[0]
        long_desc_dict[command] = descriptions[1]

def write_plugins():
    with open('plugins', 'wb') as f:
        pickle.dump(plugins, f)

def write_prompt():
    with open('prompt', 'w') as f:
        f.write(prompt)

def read_prompt():
    global prompt
    try:
        with open('prompt', 'r') as f:
            prompt = f.read()
            
    except FileNotFoundError:
        prompt = DEFAULT_PROMPT

def read_plugins():
    global plugins
    try:
        with open('plugins', 'rb') as f:
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
    enable_fix = False

    try:
        init_help()
        init_commands()
        
    except Exception as e:
        old_plugins = plugins
        enable_fix = True
        plugins = []
        reinit()
        print(f'{e}\nAll plugins disabled.', end='')
        
        if isinstance(e, FileNotFoundError):
            print(f' Recommended action: Run \'fix {e.filename.rstrip(".json")}\'.')
        else:
            print()

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
            
        elif command == 'unload':
            plugins.remove(argv[1])
            write_plugins()
            reinit()
            
        elif command == 'reset':
            if os.path.exists('plugins'):
                os.remove('plugins')
            plugins = ['default_commands']
            reinit()
            
        elif command == 'fix' and enable_fix:
            plugins = old_plugins
            plugins.remove(argv[1])
            write_plugins()
            print('Done! Other plugins enabled.')
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
                print(long_desc_dict.get(argv[1], 'Command not found!'))
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
