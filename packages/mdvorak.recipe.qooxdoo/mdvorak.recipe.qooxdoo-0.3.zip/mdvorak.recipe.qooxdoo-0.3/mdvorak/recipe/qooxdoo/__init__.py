import os, sys, re
from zc.buildout import easy_install
from zc.recipe.egg import Egg

def split(s):
    """
    Splits the string by white-space. Ignores empty results.
    """
    for entry in re.split(r'\s*', s):
        # Ignore empty entries - they're just empty lines
        if entry:
            yield entry


class GeneratorRecipe(object):
    """
    Buildout recipe, that runs Qooxdoo generator script. It requires Qooxdoo SDK to run.

    Supported options:
    script, commands, config, qooxdoo-sdk, cache, let, remove-dirs, create-dirs, clean-dirs

    See README for details.
    """

    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options

        # Helper object
        self.egg = Egg(buildout, options['recipe'], options)

        # Read configuration
        self.root = os.path.abspath(buildout['buildout']['directory'])

        self.qooxdoo_sdk = self._abspath(options.get('qooxdoo-sdk', buildout['buildout']['qooxdoo-sdk']))
        self.generator = self._abspath(os.path.join(self.qooxdoo_sdk, 'tool', 'bin', 'generator.py'))
        self.script = options.get('script', name)
        self.cache_path = options.get('cache', buildout['buildout'].get('cache-directory'))

        self.remove_dirs = [self._abspath(path) for path in split(options.get('remove-dirs', ''))]
        self.create_dirs = [self._abspath(path) for path in split(options.get('create-dirs', ''))]
        self.clean_dirs = [self._abspath(path) for path in split(options.get('clean-dirs', ''))]

        self.commands = list(split(options.get('commands', '')))

        self.configs = []
        for config in split(options['config']):
            path = self._abspath(config)

            # If it points to a directory instead of a file, let's assume it contains config.json
            if os.path.isdir(path):
                path = os.path.join(path, 'config.json')

            # Add to the list
            self.configs.append(path)

        # We must have at least one config specified
        if not len(self.configs):
            raise ValueError("No qooxdoo config specified")

        # Macros
        self.macros = ['QOOXDOO_PATH:' + self.qooxdoo_sdk]

        if self.cache_path:
            self.cache_path = self._abspath(os.path.join(self.cache_path, 'qx'))
            self.macros += ['CACHE:' + self.cache_path]

        self.macros += split(options.get('let', ''))

    def _abspath(self, path):
        return os.path.normpath(path if os.path.isabs(path) else os.path.join(self.root, path))

    def install(self):
        # Validate qooxdoo path
        if not os.path.exists(self.generator):
            raise ValueError("Qooxdoo SDK path '{0}' is not valid".format(self.qooxdoo_sdk))

        for config in self.configs:
            if not os.path.exists(config):
                raise ValueError("Qooxdoo config file '{0}' does not exist".format(config))

        # Cache dir
        if self.cache_path and not os.path.isdir(self.cache_path):
            os.makedirs(self.cache_path)

        # Prepare values needed for script generation
        requirements, ws = self.egg.working_set()
        executable = sys.executable
        bin = self.options['bin-directory']

        # Options for the script
        options = {
            'args': [executable, self.generator] + ['--macro=' + macro for macro in self.macros],
            'configs': [config for config in self.configs],
        }

        if self.commands:
            options['commands'] = self.commands
        if self.remove_dirs:
            options['remove_dirs'] = self.remove_dirs
        if self.create_dirs:
            options['create_dirs'] = self.create_dirs
        if self.clean_dirs:
            options['clean_dirs'] = self.clean_dirs

        # Generate script
        output = easy_install.scripts(
            [(self.script, 'mdvorak.recipe.qooxdoo.script', 'generator')],
            ws, executable, bin,
            arguments=options
        )

        # Return name of the script so Buildout will know about it
        return output

    update = install
