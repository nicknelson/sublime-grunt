import sublime
import sublime_plugin
import os
import subprocess
import json
from hashlib import sha1 

package_name = "sublime-grunt"
package_url = "https://github.com/nicknelson/sublime-grunt"
cache_file_name = ".sublime-grunt.cache"


class GruntRunner(object):
    def __init__(self, window):
        self.window = window
        self.list_gruntfiles()

    def list_tasks(self):
        try:
            self.callcount = 0
            json_result = self.fetch_json()
        except TypeError as e:
            self.window.new_file().run_command("grunt_error", {"message": "SublimeGrunt: JSON is malformed\n\n%s\n\n" % e})
            sublime.error_message("Could not read available tasks\n")
        else:
            settings = sublime.load_settings('SublimeGrunt.sublime-settings')
            available_tasks = json_result["available_tasks"]
            if settings:
                available_tasks += settings.get('available_tasks')
            if available_tasks:
                filtered_tasks = [obj for obj in json_result["tasks"].items() if obj[1]['name'] in available_tasks]
                if not filtered_tasks:
                    filtered_tasks = json_result["tasks"].items()
            else: 
                filtered_tasks = json_result["tasks"].items()

            tasks = [[name, task['info'], task['meta']['info'], task['grunt_args']] for name, task in filtered_tasks]
            # self.window.new_file().run_command("grunt_error", {"message": str(tasks)})
            return sorted(tasks, key=lambda task: task)

    def run_expose(self):
        package_path = os.path.join(sublime.packages_path(), package_name)

        args = r'grunt --no-color --tasks "%s" expose:%s' % (package_path, os.path.basename(self.chosen_gruntfile))

        expose = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=get_env_with_exec_args_path(), cwd=self.wd, shell=True)
        (stdout, stderr) = expose.communicate()

        if 127 == expose.returncode:
            sublime.error_message("\"grunt\" command not found.\nPlease add Grunt's location to your PATH.")
            return

        return self.fetch_json()

    def fetch_json(self):
        jsonfilename = os.path.join(self.wd, cache_file_name)
        data = None

        if os.path.exists(jsonfilename):
           filesha1 = hashfile(self.chosen_gruntfile)

           json_data=open(jsonfilename)

           try:
                data = json.load(json_data)
                if data[self.chosen_gruntfile]["sha1"] == filesha1:
                    return data[self.chosen_gruntfile]
           finally:
               json_data.close()
        self.callcount += 1

        if self.callcount == 1: 
            return self.run_expose()

        if data is None:
            raise TypeError("Could not expose gruntfile")

        raise TypeError("Sha1 from grunt expose ({0}) is not equal to calculated ({1})".format(data[self.chosen_gruntfile]["sha1"], filesha1))

    def list_gruntfiles(self):
        # Load gruntfile paths from config
        self.folders = get_grunt_file_paths()
        self.grunt_files = []
        for f in self.window.folders():
            self.folders.append(f)

        for f in self.folders:
            if os.path.exists(os.path.join(f, "Gruntfile.js")):
                self.grunt_files.append(os.path.join(f, "Gruntfile.js"))
            elif os.path.exists(os.path.join(f, "Gruntfile.coffee")):
                self.grunt_files.append(os.path.join(f, "Gruntfile.coffee"))

        if len(self.grunt_files) > 0:
            if len(self.grunt_files) == 1:
                self.choose_file(0)
            else:
                self.window.show_quick_panel(self.grunt_files, self.choose_file)
        else:
            sublime.error_message("Gruntfile.js or Gruntfile.coffee not found!")

    def choose_file(self, file):
        self.wd = os.path.dirname(self.grunt_files[file])
        self.chosen_gruntfile = self.grunt_files[file]

        self.tasks = self.list_tasks()
        self.task_args = [obj.pop(3) for obj in self.tasks]
        if self.tasks is not None:
            self.arg_values = []
            #fix quick panel unavailable
            sublime.set_timeout(lambda:  self.window.show_quick_panel(self.tasks, self.pass_argument), 1)

    def pass_argument(self, task):
        if task:
            self.this_task = task

        if self.task_args[self.this_task]:
            arg_i = len(self.arg_values)
            if self.task_args[task][arg_i]["type"] == "text":
                if self.task_args[task][arg_i]["default_value"]:
                    if self.task_args[task][arg_i]["default_value"] == "path":
                        this_value = self.window.active_view().file_name()
                    elif self.task_args[task][arg_i]["default_value"]:
                        this_value = self.task_args[task][arg_i]["default_value"]
                else:
                    this_value = ""
                if self.task_args[task][arg_i]["key"]:
                    arg_name = self.task_args[task][arg_i]["key"]
                else:
                    arg_name = "Argument"
                self.window.show_input_panel("Enter " + arg_name, this_value, self.save_argument, None, None)
            elif self.task_args[task][arg_i]["type"] == "prompt":
                self.on_done(None)
        else:
            self.on_done(None)

    def save_argument(self, arg):
        self.arg_values.append(arg)
        self.on_done(arg)
        # if len(self.arg_values) == len(self.task_args[self.this_task]):
        #     self.on_done(self.arg_values)
        # else:
        #     self.pass_argument

    def display_prompt(self, task):
        if task_prompt:
            prompt_options = [{}]
            next_step = self.on_done
            self.window.show_quick_panel(prompt_optioms, next_step)
        else:
            self.on_done

    def on_done(self, arg):
        if self.this_task > -1:
            path = get_env_path()
            passedArgument = ':'+arg[0]
            exec_args = {'cmd': "grunt --no-color " + self.tasks[self.this_task][0] + passedArgument, 'shell': True, 'working_dir': self.wd, 'path': path}
            self.window.run_command("exec", exec_args)


def hashfile(filename):
    with open(filename, mode='rb') as f:
        filehash = sha1()
        content = f.read();
        filehash.update(str("blob " + str(len(content)) + "\0").encode('UTF-8'))
        filehash.update(content)
        return filehash.hexdigest()


def get_env_path():
    path = os.environ['PATH']
    settings = sublime.load_settings('SublimeGrunt.sublime-settings')
    if settings:
        exec_args = settings.get('exec_args')
        if exec_args:
            path = exec_args.get('path', os.environ['PATH'])
    return str(path)


def get_grunt_file_paths():
    # Get the user settings
    global_settings = sublime.load_settings('SublimeGrunt.sublime-settings')
    # Check the settings for the current project
    # If there is a setting for the paths in the project, it takes precidence
    # No setting in the project, then use the global one
    # If there is no global one, then use a default
    return sublime.active_window().active_view().settings().get('SublimeGrunt', {}).get('gruntfile_paths', global_settings.get('gruntfile_paths', []))


def get_env_with_exec_args_path():
    env = os.environ.copy()
    settings = sublime.load_settings('SublimeGrunt.sublime-settings')
    if settings:
        exec_args = settings.get('exec_args')        
        if exec_args:
            path = str(exec_args.get('path', ''))
            if path:
                env['PATH'] = path
    return env


class GruntCommand(sublime_plugin.WindowCommand):
    def run(self):
        GruntRunner(self.window)


class GruntKillCommand(sublime_plugin.WindowCommand):
    def run(self):
        self.window.run_command("exec", {"kill": True})

class GruntErrorCommand(sublime_plugin.TextCommand):
    def run(self, edit, **args):
        view = self.view
        view.insert(edit, 0, args["message"])
