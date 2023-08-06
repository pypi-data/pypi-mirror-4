import os
from setuptools import setup, find_packages
import cmsplugin_filer_image_translated


def read(fname):
    try:
        return open(os.path.join(os.path.dirname(__file__), fname)).read()
    except IOError:
        return ''


setup(
    name="cmsplugin-filer-image-translated",
    version=cmsplugin_filer_image_translated.__version__,
    description=read('DESCRIPTION'),
    long_description=read('README.rst'),
    license='The MIT License',
    platforms=['OS Independent'],
    keywords='django, image, multilingual, i18n, filer, django-cms, plugin',
    author='Martin Brochhaus',
    author_email='mbrochh@gmail.com',
    url="https://github.com/bitmazk/cmsplugin-filer-image-translated",
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
    test_suite='cmsplugin_filer_image_translated.tests.runtests.runtests',
)
