from setuptools import setup

__version_info__ = ('0', '0', '6')
__version__ = '.'.join(__version_info__)


setup(
    name="git_warden",
    version=__version__,
    description="Batch Git repository manager",
    author="Ceasar Bautista",
    author_email="cbautista2010@gmail.com",
    url="http://www.github.com/Ceasar/git_warden",
    py_modules=["git_warden"],
    install_requires=["fabric"]
)
