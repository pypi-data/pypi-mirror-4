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
    Buildout recipe, that runs Qooxdoo generator. It requires Qooxdoo SDK to run.
    """

    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options

        # Helper object
        self.egg = Egg(buildout, options['recipe'], options)

        # Read configuration
        self.root = os.path.abspath(buildout['buildout']['directory'])

        self.qooxdoo_sdk = self._abspath(options.get('qooxdoo-sdk', buildout['buildout']['qooxdoo-sdk']))
        self.generator = self._abspath(os.path.join(self.qooxdoo_sdk, 'tool', 'bin', 'generator.py'))
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

        # Options for the script
        options = {
            'args': [sys.executable, self.generator] + ['--macro=' + macro for macro in self.macros],
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

        # Perform the action
        return self._install(options)

    def _install(self, options):
        raise NotImplementedError()

    update = install


class ScriptRecipe(GeneratorRecipe):
    """
    Buildout recipe, that generate script that runs Qooxdoo generator. It requires Qooxdoo SDK to run.

    Supported options:
    script, commands, config, qooxdoo-sdk, cache, let, remove-dirs, create-dirs, clean-dirs

    See README for details.
    """

    def __init__(self, buildout, name, options):
        super(ScriptRecipe, self).__init__(buildout, name, options)

        self.script = options.get('script', name)


    def _install(self, options):
        # Prepare values needed for script generation
        requirements, ws = self.egg.working_set()
        bin = self.options['bin-directory']

        # Generate script
        output = easy_install.scripts(
            [(self.script, 'mdvorak.recipe.qooxdoo.script', 'generator')],
            ws, sys.executable, bin,
            arguments=options
        )

        # Return name of the script so Buildout will know about it
        return output


class RunRecipe(GeneratorRecipe):
    def _install(self, options):
        # Lazy import - we don't need this for ScriptRecipe
        from mdvorak.recipe.qooxdoo.script import generator

        # Call generator
        result = generator(options)

        # Fail on error
        if result != 0:
            raise AssertionError("Qooxdoo generator finished with errors")

        # No script generated
        return ()
