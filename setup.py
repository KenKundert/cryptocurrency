from setuptools import setup

setup(
    name = 'cryptocurrency',
    version = '0.1.0',
    author = 'Ken Kundert',
    license = 'GPLv3+',
    install_requires = '''
        appdirs
        arrow
        avendesora
        docopt
        inform>=1.14
        matplotlib
        quantiphy
        requests
        shlib
    '''.split(),
        # avendesora is not required, without it there is no transaction or networth support
        # matplotlib is not required, without it you cannot use show-cryptocurrency-history
    py_modules = 'cryptocurrency'.split(),
    scripts = 'cryptocurrency show-cryptocurrency-history'.split()
    zip_safe = True,
)

# vim: set sw=4 sts=4 et:
