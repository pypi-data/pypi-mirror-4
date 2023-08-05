from setuptools import setup

setup(
    name="campari",
    version="0.1",
    description="Simple command-line pomodoro timer.",
    author="Ilya Strukov",
    author_email="iley@iley.ru",
    url="https://github.com/iley/campari",
    py_modules=["campari"],
    scripts=["campari"],
    install_requires=[
        "decorator>=3.4.0",
        "docopt>=0.5.0"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "License :: OSI Approved :: MIT License"])
