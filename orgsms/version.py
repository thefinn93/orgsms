import subprocess

__version__ = "dev"

try:
    __version__ = str(subprocess.check_output(['git', 'describe', '--tags', '--always'])).strip()
except subprocess.CalledProcessError:
    pass
