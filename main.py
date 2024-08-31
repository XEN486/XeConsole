import importlib, os, json, pickle, pathlib
from datetime import datetime

internal_commands = ['help', 'load', 'unload', 'reset', 'exit', 'prompt', 'cd', 'chdir']
internal_fixes = ['cd', 'chdir']

default_plugins = ['default_commands']
default_prompt = '> '

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
        plugin_cmd_dict[plugin] = [command for command in dir(module) if command.startswith('command_')]
        all_cmds.extend([str(i).removeprefix('command_') for i in plugin_cmd_dict[plugin]])

def execute_command(command, argc, argv):
    done = False
    for key in plugin_cmd_dict.keys():
        if done: break
        
        for cmd in plugin_cmd_dict[key]:
            if cmd == 'command_'+command:
                exec(f'module_dict["{key}"].{cmd}(argc, argv)')
                done = True
                break
            
        if done: break

def init_help():
    help_dict = {}
    jsons = ['internal'] + plugins
    for file in jsons:
            with open(file+'.json') as f:
                help_dict.update(json.load(f))

    for key in help_dict.keys():
        short_desc_dict[key] = help_dict[key][0]
        long_desc_dict[key] = help_dict[key][1]

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
        prompt = default_prompt

def read_plugins():
    global plugins

    try:
        with open('plugins', 'rb') as f:
            plugins = pickle.load(f)

    except FileNotFoundError:
        plugins = default_plugins

def update_prompt(prompt):
    return prompt.replace('$n', pathlib.Path.home().drive.removesuffix(':')).replace('$p', os.getcwd()).replace('$t', datetime.now().strftime("%H:%M:%S"))

def reinit():
    global all_cmds, plugin_cmd_dict, module_dict, long_desc_dict, short_desc_dict
    
    all_cmds = []
    plugin_cmd_dict = {}
    module_dict = {}
    long_desc_dict = {}
    short_desc_dict = {}
    
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
        if type(e) == FileNotFoundError:
            print(f' Recommended action: Run \'fix {e.filename.removesuffix(".json")}\'.')
        else:
            print()

    running = True
    while running:
        prompt = update_prompt(old_prompt)
        inp = str(input(prompt))
        argv = inp.split(' ')
        argc = len(argv)

        if argv[0] in all_cmds:
            execute_command(argv[0], argc, argv)

        elif argv[0] == 'load':
            plugins.append(argv[1])
            write_plugins()
            reinit()

        elif argv[0] == 'unload':
            plugins.remove(argv[1])
            write_plugins()
            reinit()

        elif argv[0] == 'reset':
            try:
                os.remove('plugins')
            except:
                pass
            
            plugins = ['default_commands']
            
            reinit()

        elif argv[0] == 'fix' and enable_fix:
            plugins = old_plugins
            plugins.remove(argv[1])
            write_plugins()
            
            print('Done! Other plugins enabled.')
            reinit()

        # fix for cmd
        elif argv[0] == 'cd' or argv[0] == 'chdir':
            os.chdir(' '.join(argv[1:]))

        elif argv[0] == 'prompt':
            prompt = ' '.join(argv[1:])
            old_prompt = prompt
            write_prompt()
        
        elif argv[0] == 'exit':
            exit()

        elif argv[0] == 'help':
            if argc > 1:
                try:
                    print(long_desc_dict[argv[1]])
                except KeyError:
                    print('Command not found!')
            else:
                [print(f'{int}: {short_desc_dict[int]}') for int in internal_commands if int not in internal_fixes]

                for cmd in all_cmds:
                    try:
                        print(f'{cmd}: {short_desc_dict[cmd]}')
                    except:
                        pass
                
        else:
            os.system(inp)

if __name__ == '__main__':
    main()
