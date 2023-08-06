import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

long_desc = read('README.md')

setup(
    install_requires=['RPi.GPIO'],
    name="RPIO",
    packages=['RPIO'],
    version="0.1.3",
    description="An extension of RPi.GPIO to easily use interrupts on the Raspberry Pi",
    long_description=long_desc,
    url="https://github.com/metachris/raspberrypi-utils",

    author="Chris Hager",
    author_email="chris@linuxuser.at",

    license="MIT",
    keywords=["raspberry", "raspberry pi", "interrupts", "gpio", "gpio2"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Operating System :: POSIX :: Linux",
        "Topic :: Utilities",
        "Topic :: Software Development",
        "Topic :: Home Automation",
        "Topic :: System :: Hardware",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
    ],
)
