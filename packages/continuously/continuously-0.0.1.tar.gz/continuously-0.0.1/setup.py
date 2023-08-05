from setuptools import setup

setup(
    name = "continuously",
    version = "0.0.1",
    author = "Francesco Bruschi",
    py_modules = ["continuous"],
    entry_points = {
        "console_scripts" :["continuous = continuous:entry"]},
    description = "Allows to call a command continuously, whenever an argument file changes",
    long_description = open("README.md").read(),
    author_email = "Bruschi@elet.polimi.it",
    install_requires = open("requirements.txt").read().splitlines()
)
