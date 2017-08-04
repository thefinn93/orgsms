import subprocess

__version__ = "dev"

gitprocess = subprocess.run(['git', 'describe', '--tags', '--always'], stdout=subprocess.PIPE)
if gitprocess.returncode == 0:
    __version__ = gitprocess.stdout.strip()
