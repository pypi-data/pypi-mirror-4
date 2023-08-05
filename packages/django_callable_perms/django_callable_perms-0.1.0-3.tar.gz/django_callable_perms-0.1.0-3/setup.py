from setuptools import setup, find_packages

setup(
    name = "django_callable_perms",
    version = "0.1.0-3",
    description = 'Modular registry of permission handlers for Django',
    author = 'David Danier',
    author_email = 'david.danier@team23.de',
    url = 'https://github.com/ddanier/django_callable_perms',
    long_description = open('README.rst', 'r').read(),
    packages = [
        'django_callable_perms',
        'django_callable_perms.management',
        'django_callable_perms.management.commands',
        'django_callable_perms.templatetags',
    ],
    install_requires = [
        'Django >=1.4',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities'
    ],
)

