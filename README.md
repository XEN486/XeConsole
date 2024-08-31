# XeConsole

A simple command interpreter that easily integrates into your python program.

## Guide on creating commands
Creating commands is very easy! It should only take you 5 minutes to set up.

### Create the plugin files
Create a python file named anything. For example, you could name it `console_commands.py`.\
Alongside it, you should create a json file of the same name (e.g. `console_commands.json`).

### Write your code!
This step is the most important one. This is where you will write your code.\
All functions starting with `command_` will be recognized as a command in your plugin.\
Open up your `console_commands.py` file and start writing! For this example, we will make a simple hello command.
```python
def command_hello(argc, argv):
  print(f'Hello, world! argc: {argc}, argv: {argv}')
```

### Add the help text
This step is optional but highly recommended. Add your command's descriptions to this file.\
It should be an array with the short and long descriptions.\
For example:
```json
{
  "hello": [
    "A simple hello command.",
    "A hello command written for a tutorial. It prints out the argc and argv values."
  ]
}
```

### That's it?
Yes! You have just added your command!\
Run the console and load your plugin with `load console_commands`.
Run `help` and voilà! Your hello command should be there. Try run it!
