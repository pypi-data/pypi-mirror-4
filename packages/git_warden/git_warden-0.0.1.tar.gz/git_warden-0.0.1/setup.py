from distutils.core import setup

import git_warden as module

setup(
    name="git_warden",
    version=module.__version__,
    description=module.__doc__,
    author="Ceasar Bautista",
    author_email="cbautista2010@gmail.com",
    url="http://www.github.com/Ceasar/git_warden",
    py_modules=[module.__name__],
)
