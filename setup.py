from setuptools import setup

setup(
    name='cryptocurrency',
    version='0.0.14',
    author='Ken Kundert',
    license='GPLv3+',
    install_requires='''
        appdirs
        arrow
        avendesora
        docopt
        inform
        matplotlib
        quantiphy
        requests
        shlib
    '''.split(),
        # avendesora is not required, without it there is no transaction support
        # matplotlib is not required, without it you cannot use
        # show-cryptocurrency-history
    py_modules='cryptocurrency networth'.split(),
    scripts='cryptocurrency show-cryptocurrency-history'.split()
)

# vim: set sw=4 sts=4 et:
