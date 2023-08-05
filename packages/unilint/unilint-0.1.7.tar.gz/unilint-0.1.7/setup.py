from setuptools import setup

import imp


def get_version():
    ver_file = None
    try:
        ver_file, pathname, description = imp.find_module('__version__', ['src/unilint'])
        vermod = imp.load_module('__version__', ver_file, pathname, description)
        version = vermod.VERSION
        return version
    finally:
        if ver_file is not None:
            ver_file.close()


setup(name='unilint',
      version=get_version(),
      packages=['unilint', 'roslint'],
      package_dir={'': 'src'},
      scripts=["scripts/roslint", "scripts/unilint"],
      install_requires=[],
      author="Thibault Kruse",
      author_email="thibault.kruse@gmx.de",
      url="https://github.com/tkruse/unilint",
      download_url="https://github.com/tkruse/unilint",
      keywords=["lint", "python", "pylint",
                "pychecker", "pyflakes", "pep8",
                "cppcheck", "linux"],
      classifiers=["Programming Language :: Python",
                   "License :: OSI Approved :: BSD License"],
      description="script wrapping static code analyzers producing unified output",
      long_description="""Unilint runs over files or folders and makes calls to static code analysis tools, which are not installed with unilint. Depends on shell tools like gnu find and grep.""",
      license="BSD")
