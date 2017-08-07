import subprocess

__version__ = "dev"

try:
    __version__ = subprocess.check_output(['git', 'describe', '--tags', '--always']).strip()
except subprocess.CalledProcessError:
    pass
