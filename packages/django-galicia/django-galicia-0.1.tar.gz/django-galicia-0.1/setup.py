import os
from setuptools import setup

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

setup(
    name = 'django-galicia',
    version = '0.1',
    description = 'Django helpers for Galicia (Spain).',
    long_description = README,
    author = 'Afonso Fernandez Nogueira',
    author_email = 'fonzzo+django-galicia@gmail.com',
    license='BSD',
    url = 'https://bitbucket.org/fonso/django-galicia',
    packages = ['django_galicia'],
    include_package_data = True,
    classifiers = [
        'Development Status :: 1 - Planning',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    install_requires=[
        'Django>=1.4',
    ]
)
