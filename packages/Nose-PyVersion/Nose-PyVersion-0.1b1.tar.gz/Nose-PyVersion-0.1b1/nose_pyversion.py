# vim: set fileencoding=utf-8 :

from nose.plugins import Plugin
import os


class PyVersion(Plugin):
    """Nose plugin that excludes files based on python version and file name

    If a filename has the format [NAME][SEPARATOR]py[VERSION].py and
    VERSION doesn't match [major][minor][micro], [major][minor] or [major]
    the file will be excluded from tests.

    Options for pyversion::

        pyversion-separator

            The separator between [name] and 'py' in the filename

    Example::

        file_py3.py
        file_py33.py
        file_py330.py
        file_py2.py
        file_py27.py
        file_py273.py

    """

    name = 'pyversion'
    """Name of this nose plugin"""

    score = 1

    enabled = False
    """By default this plugin is not enabled"""

    default_separator = '_'
    """The separator between filename and python version"""

    separator = None
    """Separator between filename and python version

    Will be set to :attr:`PyVersion.default_separator` or by the
    pyversion-separator option.
    """

    def options(self, parser, env=os.environ):
        """Define the command line options for the plugin."""
        parser.add_option(
            "--pyversion-separator",
            action="store",
            default=self.default_separator,
            dest="pyversion_separator",
            help="Separator for version-specific files")
        super(PyVersion, self).options(parser, env=env)

    def configure(self, options, conf):
        super(PyVersion, self).configure(options, conf)
        if not self.enabled:
            return
        self.separator = options.pyversion_separator or self.default_separator
        if self.separator is '.':
            raise Exception('Not a valid pyversion-separator: ' +
                            str(self.separator))

    def wantFile(self, file):
        import sys
        import re

        separator = re.escape(self.separator)

        # Use '%' instead of str.format because of older python versions
        is_versioned = r'^.+%spy\d+\.py$' % (separator,)
        wrong_version = (
            r'^.+%(sep)spy%(maj)d((%(min)s)|(%(min)s%(mic)s))?\.py$' % {
                'sep': separator,
                'maj': sys.version_info.major,
                'min': sys.version_info.minor,
                'mic': sys.version_info.micro})

        if re.match(is_versioned, file) and not re.match(wrong_version,
                                                         file):
            return False
        else:
            return None
