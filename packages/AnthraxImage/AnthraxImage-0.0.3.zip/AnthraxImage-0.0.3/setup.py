# vim set fileencoding=utf-8
from setuptools import setup

with open('README.rst') as f:
    long_description = f.read()

setup(
    name = 'AnthraxImage',
    version = '0.0.3',
    author = 'Szymon Pyżalski',
    author_email = 'zefciu <szymon@pythonista.net>',
    description = 'Anthrax - tools for HTML input',
    keywords = 'form web html',
    long_description = long_description,

    install_requires = ['Anthrax', 'pystacia'],
    tests_require = ['nose>=1.0', 'nose-cov>=1.0'],
    test_suite = 'nose.collector',
    package_dir = {'': 'src'},
    namespace_packages = ['anthrax'],
    packages = [
        'anthrax', 'anthrax.image'
    ],
    classifiers = [
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Multimedia :: Graphics',
    ],
    entry_points = """
[anthrax.field]
image = anthrax.image.field:Image
""",

)

