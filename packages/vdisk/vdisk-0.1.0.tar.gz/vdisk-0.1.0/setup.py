from distutils.core import setup

VERSION = '0.1.0'

setup(
    name='vdisk',
    version=VERSION,
    description="Helper tool to build debian based virtual disks.",
    author='John-John Tedro',
    author_email='udoprog@spotify.com',
    url="http://github.com/spotify/vdisk",
    license='GPLv3',
    packages=[
        'vdisk',
        'vdisk.actions',
    ],
    scripts=[
        "bin/vdisk"
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
    ],
)
