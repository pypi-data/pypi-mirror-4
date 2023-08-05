import os
import sys
import re
import shutil

class Command(object):
    name = 'default_name'
    def run(self, option):
        pass
    
class CommandManager(object):
    commands = []
    
    def get_command(self, command_name):
        command = [f for f in self.commands if f.name == command_name]
        try:
            command = command[0]
        except IndexError:
            raise Exception('Command %(command_name)s does not exist!'%locals())
        return command
        
    def add_command(self):
        def wrapper(command):
            self.commands.append(command())
        return wrapper
    
    def execute(self, argv):
        command_name, option = argv[:]
        command = self.get_command(command_name)
        command.run(option)
        
command_manager = CommandManager()

@command_manager.add_command()
class StartProject(Command):
    name = 'startproject'
    def run(self, option):
        if not re.search(r'^[_a-zA-Z]+$', option):
            raise Exception('Bad option!')
        project_path = os.path.join(os.getcwd(), option)
        if not os.path.exists(project_path):
            os.mkdir(project_path)
        shutil.copy(os.path.join(os.path.dirname(__file__), 'wsgi.py'), project_path)
                    