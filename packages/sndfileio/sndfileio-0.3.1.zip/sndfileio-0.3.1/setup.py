from setuptools import setup

version = open("VERSION.txt").readline()

setup(
    name = "sndfileio",
    version = version,
    author = "Eduardo Moguillansky",
    author_email = "eduardo moguillansky dot gmail dot com",
    url = "https://github.com/gesellkammer/sndfileio",
    packages = [ "sndfileio"],
    package_data={'': ['README.md']},
    include_package_data=True
)