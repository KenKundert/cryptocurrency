from setuptools import setup

setup(
    name='cryptocurrency',
    version='0.0.14',
    author='Ken Kundert',
    license='GPLv3+',
    install_requires='''
        appdirs
        arrow
        avendesora  # not required if you only want prices
        docopt
        inform
        matplotlib  # required only for show-cryptocurrency-history
        quantiphy
        requests
        shlib
    '''.split(),
    py_modules='cryptocurrency networth'.split(),
    scripts='cryptocurrency show-cryptocurrency-history'.split()
)

# vim: set sw=4 sts=4 et:
