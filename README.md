sublime-grunt
=============

Formed from [tvooo/sublime-grunt](https://github.com/tvooo/sublime-grunt).

Added ability to filter the list of tasks shown in the list by adding an array of tasks in your grunt config:

```
sublime_grunt_tasks: [
  'some-task',
  'another-task'
]
```

OR in your User settings for `SublimeGrunt.sublime-settings`:

```
    "available_tasks": ['some-task','another-task']
```

You can also now pass arguments as either a text field or a prompt, by adding an `args` node to your task settinsg in your grunt config:

```
    `some-task`: {
      args: [
        {
          'key':'foo',
          'type':'text',
          'default_value': 'Bar'
        },
        {
          'key':'someOptions',
          'type':'prompt',
          'choices':['hello','world']
        }
      ]
    }
```

`type: text` will display an input panel to enter any text arguments. You can enter a `default_value` to pre-fill the argument with some text, you can also set a default value of `path` to pre-fill it will the path to the current file.

`type: prompt` will display a quick panel list of options to select from. Enter the options as an array in `choices`

The arguments will be passed to the grunt command in the order they appear in the task list, like `grunt some-task:arg1:arg2`

## Usage

Open the command palette using Ctrl+Shift+P (or Cmd+Shift+P on Mac, respectively)
and choose the "Grunt Custom Deploy" command.

The plugin expects to find a Gruntfile (`Gruntfile.js` or `Gruntfile.coffee`) in an open folder.
It displays a sorted list of available Grunt tasks out of this Grunt file.
If it finds more than one Gruntfile, it first provides a list for selection.

There is also a command to kill running tasks, for example
`watch` tasks.

## Settings

The file `SublimeGrunt.sublime-settings` is used for configuration.

You may override your `PATH` environment variable as follows:

```
{
    "exec_args": {
        "path": "/bin:/usr/bin:/usr/local/bin"
    }
}
```
If your GruntFile is not in the base path of the project, then you can add the path(s) to check as follows:

```
{
    "gruntfile_paths": ["/path", "/another/path", "/one/final/path"]
}
```
Alternatively this could be set per-project in your .sublime-project settings object

## Releases

* 1.0 Jumping to 1.0 to support ST versioning with tags
* 0.3 Grunt tasks are cached
* 0.2 Rewrite; supports Grunt >= 0.4, tasks can be killed (for example the `watch` task)
* 0.1 Initial release

## Thanks

Thanks for some contributions go to

* [VirtueMe](https://github.com/VirtueMe)
* [antonellopasella](https://github.com/antonellopasella)
* [structAnkit](https://github.com/structAnkit)
* [lavrton](https://github.com/lavrton)
* [adamcbrewer](https://github.com/adamcbrewer)
* [thebjorn](https://github.com/thebjorn)
* [maliayas](https://github.com/maliayas)
