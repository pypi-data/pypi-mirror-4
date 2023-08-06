from __future__ import with_statement
from virtstrap import hooks
from virtstrap.log import logger
from virtstrap.utils import call_subprocess, in_directory


@hooks.create('install', ['after'])
def install_npm_packages(event, options, project=None, **kwargs):
    # ensure we're in the project's root directory
    with in_directory(project.path()):
        try:
            call_subprocess(['command', '-v', 'npm'], show_stdout=False)
        except OSError:
            logger.warning('Skipping node requirements. '
                    'npm must be installed on your system')
            return
        # Installs the bundle requirements and the bins for each
        # requirement in the project's bin path
        call_subprocess(['npm', 'install'])


@hooks.create('environment', ['after'])
def add_npm_bin_path(event, options, project=None, **kwargs):
    with in_directory(project.path()):
        npm_bin_path = project.path('node_modules/.bin')
        env_file_path = options.env_file
        env_file = open(env_file_path, 'a')
        env_file.write('\n# EXTEND PATH WITH NPM\n')
        env_file.write('export PATH="%s:$PATH"\n' % npm_bin_path)
        env_file.close()
