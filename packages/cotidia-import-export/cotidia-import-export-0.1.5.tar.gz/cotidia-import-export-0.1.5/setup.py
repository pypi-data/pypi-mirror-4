from distutils.core import setup
from setuptools import find_packages


VERSION = __import__("import_export").__version__

CLASSIFIERS = [
    'Framework :: Django',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Topic :: Software Development',
]

install_requires = [
    'tablib',
    'Django>=1.4.2',
    'diff-match-patch',
]

setup(
    name="cotidia-import-export",
    description="Django application and library for importing and exporting"
            "data with included admin integration.",
    version=VERSION,
    author="Guillaume Piot",
    author_email="guillaume@cotidia.com",
    url="https://github.com/Cotidia/cotidia-import-export",
    packages=find_packages(),
    include_package_data=True,
    install_requires=install_requires,
    classifiers=CLASSIFIERS,
)