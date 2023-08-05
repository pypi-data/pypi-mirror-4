from setuptools import setup
from version import VERSION

setup(
    name="campari",
    version=VERSION,
    description="Simple command-line pomodoro timer.",
    author="Ilya Strukov",
    author_email="iley@iley.ru",
    url="https://github.com/iley/campari",
    py_modules=["campari", "version"],
    scripts=["campari"],
    install_requires=[
        "decorator>=3.4.0",
        "docopt>=0.5.0"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.2"])
