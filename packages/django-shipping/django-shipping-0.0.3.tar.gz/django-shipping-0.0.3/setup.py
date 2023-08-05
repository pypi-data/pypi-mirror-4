from setuptools import setup
import os


def get_packages():
    # setuptools can't do the job :(
    packages = []
    for root, dirnames, filenames in os.walk('shipping'):
        if '__init__.py' in filenames:
            packages.append(".".join(os.path.split(root)).strip("."))

    return packages


setup(
    name='django-shipping',
    version='0.0.3',
    description='Django shipping tool',
    long_description=open("README.md").read(),
    author=u'Marcel Nicolay',
    author_email='marcelnicolay@gmail.com',
    url='http://github.com/quatix/django-shipping',
    install_requires=open("requirements.txt").read().split("\n"),
    packages=get_packages(),
    package_data={'shipping': ['templates/**/*.html', 'static/**/*/*', 'migrations/*.sql']}
)
