import os
from setuptools import setup, find_packages
import object_attachments as app


def read(fname):
    try:
        return open(os.path.join(os.path.dirname(__file__), fname)).read()
    except IOError:
        return ''


setup(
    name="django-object-attachments",
    version=app.__version__,
    description=read('DESCRIPTION'),
    long_description=read('README.rst'),
    license='The MIT License',
    platforms=['OS Independent'],
    keywords='django, extension, admin, attachment, document',
    author='Martin Brochhaus',
    author_email='mbrochh@gmail.com',
    url="https://github.com/bitmazk/django-object-attachments",
    packages=find_packages(),
    include_package_data=True,
    tests_require=[
        'fabric',
        'factory_boy',
        'django-nose',
        'coverage',
        'django-coverage',
        'mock',
    ],
    test_suite='object_attachments.tests.runtests.runtests',
)
