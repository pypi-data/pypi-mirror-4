import shutil
import subprocess
import sys
import os

def generator(options):
    args = options['args']
    configs = options['configs']
    commands = options.get('commands', sys.argv[1:])
    remove_dirs = options.get('remove_dirs', [])
    create_dirs = options.get('create_dirs', [])
    clean_dirs = options.get('clean_dirs', [])

    # Remove dirs
    for path in remove_dirs + clean_dirs:
        try:
            print("rm " + path)

            if os.path.isdir(path):
                shutil.rmtree(path)
            elif os.path.isfile(path):
                os.remove(path)
        except OSError as e:
            print(e)

    # Create dirs
    for path in create_dirs + clean_dirs:
        if not os.path.isdir(path):
            print("mkdir " + path)
            os.makedirs(path)

    try:
        # Process all configs
        for config in configs:
            dir = os.path.dirname(config)
            config_arg = ['--config=' + config]

            if commands:
                # Call every command in the list
                for command in commands:
                    subprocess.check_call(args + config_arg + [command], cwd=dir)
            else:
                # Default generator command, specified in config
                subprocess.check_call(args + config_arg, cwd=dir)

        # Success
        return 0
    except subprocess.CalledProcessError as e:
        # Print error and exit
        print("Command {0} failed with return code {1}".format(e.cmd, e.returncode))
        return e.returncode
