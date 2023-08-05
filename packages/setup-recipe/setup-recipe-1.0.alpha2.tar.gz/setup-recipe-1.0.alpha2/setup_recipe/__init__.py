import os, re

class Recipe(object):
    """
    Buildout recipe that writes out script into bin directory. Script then runs `setup.py`
    in all configured directories using specified python interpreter.

    Supported options:
    * develop - List of directories, where `setup.py` file reside. Typically `${buildout:develop}` to list all developed apps.
    * use-interpreter - Name of python interpreter to use. Optional, when not specified, system interpreter is used.
    * command - Command line argument for the `setup.py`. Optional.
    """

    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options

        self.develop = []
        for dir in re.split(r'\s+', self.options['develop']):
            if len(dir):
                self.develop.append(os.path.abspath(dir))

    def install(self):
        # Read settings
        bin = self.buildout['python']['bin-directory']
        python = self.buildout['python']['executable']
        script = os.path.join(bin, self.name)
        interpreter = os.path.join(bin, self.options.get('use-interpreter', python))
        command = self.options.get('command')

        # Write out the script. Ugly but functional.
        f = open(script, 'w')
        f.write('#!' + python + '\n')

        f.write('import os, sys\n')
        f.write('from subprocess import call\n\n')

        # Write settings
        f.write('INTERPRETER = "' + interpreter + '"\n')
        f.write('DEVELOP = ' + str(self.develop) + '\n')

        if command:
            f.write('CMD = ["' + command + '"]\n')
        else:
            f.write('CMD = []\n')

        f.write('ARGS = sys.argv[1:]\n\n')

        # Loop that runs setup.py
        f.write('for dir in DEVELOP:\n')
        f.write('  print "Processing " + dir\n')
        f.write('  r = call([INTERPRETER, os.path.join(dir, "setup.py")] + CMD + ARGS, cwd=dir)\n')
        f.write('  if r != 0:\n')
        f.write('    sys.exit(r)\n\n')

        # Finished
        f.write('print "All OK"\n')
        f.write('sys.exit(0)\n')

        f.close()

        # Make it executable
        os.chmod(script, 0755)

        return script

    update = install
