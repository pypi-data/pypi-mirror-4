from setuptools import setup

setup(
    name = 'django-flatqueries',
    version = '0.1',
    author = 'John Samuel Anderson',
    author_email = 'john@andersoninnovative.com',
    description = 'Flatpage-like SQL queries for Django.',
    long_description=open('README.txt').read(),
    install_requires = [ 'Django' ],
    license = 'MIT',
    packages = ['flatqueries'],
    package_dir = {'flatqueries': 'sample_project/flatqueries'},
    package_data = {'flatqueries': ['templates/flatqueries/*.html']},
    url = 'http://code.google.com/p/django-flatqueries/',
    zip_safe = True,
)
