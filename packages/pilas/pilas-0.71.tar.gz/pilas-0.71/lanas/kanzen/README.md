About
=====

This is the Code Completion module of **NINJA-IDE**


Contact
-------

[Homepage] (http://ninja-ide.org)

Mail list: http://groups.google.com/group/ninja-ide/topics

Twitter: @ninja\_ide

IRC: #ninja-ide (at Freenode)


Using Kanzen for Code Completion
--------------------------------

```python
    from kanzen import code_completion
    cc = code_completion.CodeCompletion()
    
    # Get the source code to be analyzed
    source_code = your_editor.get_source_code()  # str or unicode
    # The path is used to identify each module after analysis inside Kanzen
    path = '/path/to/the/file.py'
    # If you provide a path, but an empty string for source_code, Kanzen will
    # try to read the file from disk and get the source code.
    # Execute "analyze_file" to collect metadata and resolve types
    cc.analyze_file(path, source_code)
    
    # To get the list of possible completions, you need to call: "get_completion"
    # providing the source code of the file, and the position of where the cursor is.
    result = cc.get_completion(source_code, offset)
```

**get_completion** will return a structure like this:

(Not always will contain all of the following, sometimes the "modules" key could be missing if that object doesn't have modules, etc)
```python
    {
        'modules': ["list of strings", ...],
        'classes': ["list of strings", ...],
        'functions': ["list of strings", ...],
        'attributes': ["list of strings", ...],
    }
```

Important
---------

You can improve Completion Results adding project folders to Kanzen, for example you can do something like this:

```python
    from kanzen import completion_daemon
    completion_daemon.add_project_folder('/path/to/project/')
    
    # This will create a map of the project structure and will allow Kanzen to understand
    # the imports that are related to your project and look for those modules.
    # Also if your project is related to another project which code is in your computer,
    # the same principle apply.
```
**DON'T FORGET:**
When using Kanzen, Kanzen will activate a daemon to resolve in background special cases of completion and have that information available when it's needed.
Being said that, don't forget to shutdown the daemon before closing your program.
```python
    from kanzen import completion_daemon
    completion_daemon.shutdown_daemon()
```

License
-------

GPL v3

