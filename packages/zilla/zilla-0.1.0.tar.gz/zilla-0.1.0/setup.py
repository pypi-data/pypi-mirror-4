from setuptools import setup

setup(
    name="zilla",
    version="0.1.0",
    desctiption="Command line suite of tools for hacking on mozilla source code",
    author="Nick Fitzgerald",
    author_email="fitzgen@mozilla.com",
    utl="https://github.com/fitzgen/zilla",
    scripts=["scripts/zilla"],
    packages=["zilla"]
)
