from distribute_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages
setup(
    include_package_data = True,
    name = "Works-4x-to-Word-Python-Converter",
    version = "2.0.1",
    packages = find_packages(),
    scripts = ['works_to_word.py',
               'distribute_setup.py'],

    # Project has some significant requirements so grab em ALL!
    install_requires = ['lxml',
                        'PIL',
                        'python-dateutil',
                        'docx',
                        'Send2Trash'],

    # metadata for upload to PyPI
    author = "Nick Wilde",
    author_email = "nick.wilde.90@gmail.com",
    description = "Works 4.x to Word Python Converter bulk converts those ancient archaic Microsoft Works Word Processor 4.x (.wps) files to Microsoft Word 2007 format (.docx).",
    license = "New BSD",
    keywords = "Microsoft Works 4x Word Converter",
    url = "https://code.google.com/p/works-4x-to-word-python-converter/",   # project home page, if any

    # could also include long_description, download_url, classifiers, etc.
)
