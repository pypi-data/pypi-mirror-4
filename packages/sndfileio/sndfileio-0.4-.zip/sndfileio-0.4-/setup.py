from setuptools import setup

version = open("VERSION.txt").readline()

setup(
    name = "sndfileio",
    version = version,
    description = "common api for reading and writing soundfiles. uses installed packages if found (scikits.audiolab), implements reading uncompressed formats correctly in any format.",
    author = "Eduardo Moguillansky",
    author_email = "eduardo moguillansky dot gmail dot com",
    url = "https://github.com/gesellkammer/sndfileio",
    packages = [ "sndfileio"],
    package_data={'': ['README.md']},
    include_package_data=True
)