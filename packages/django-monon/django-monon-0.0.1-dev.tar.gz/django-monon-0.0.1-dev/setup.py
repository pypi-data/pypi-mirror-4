# encoding=UTF-8
import os
from setuptools import setup, find_packages


def read_file(filename):
    """Read a file into a string"""
    path = os.path.abspath(os.path.dirname(__file__))
    filepath = os.path.join(path, filename)
    try:
        return open(filepath).read()
    except IOError:
        return ''


setup(
    name='django-monon',
    version=__import__('monon').__version__,
    author=u'Pedro Burón',
    author_email='pedro@witoi.com',
    packages=find_packages(),
    include_package_data=True,
    url='https://github.com/pedroburon/django-monon',
    description=u' '.join(__import__('monon').__doc__.splitlines()).strip(),
    classifiers=[
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Intended Audience :: Developers',
        'Programming Language :: Python',      
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Framework :: Django',
        'Development Status :: 1 - Planning',
        'Operating System :: OS Independent',
    ],
    install_requires = [
        'Django>=1.3',
        'pymonon',
    ],
    long_description=read_file('README.rst'),
    test_suite="runtests.runtests",
    zip_safe=False,
)
