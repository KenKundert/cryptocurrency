from setuptools import setup

setup(
    name='cryptocurrency',
    version='0.0.6',
    author='Ken Kundert',
    license='GPLv3+',
    install_requires='''
        appdirs avendesora docopt inform quantiphy requests shlib
    '''.split(),
    py_modules='cryptocurrency'.split(),
    scripts='cryptocurrency'.split()
)

# vim: set sw=4 sts=4 et:
