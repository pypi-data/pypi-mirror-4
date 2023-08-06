import os
from setuptools import setup, find_packages
import cmsplugin_blog_images as app


def read(fname):
    try:
        return open(os.path.join(os.path.dirname(__file__), fname)).read()
    except IOError:
        return ''


setup(
    name="cmsplugin-blog-images",
    version=app.__version__,
    description=read('DESCRIPTION'),
    long_description=read('README.rst'),
    license='The MIT License',
    platforms=['OS Independent'],
    keywords='django, blog, django-cms, app, plugin, apphook, images, gallery',
    author='Martin Brochhaus',
    author_email='mbrochh@gmail.com',
    url='https://github.com/bitmazk/cmsplugin-blog-images',
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
    test_suite='cmsplugin_blog_images.tests.runtests.runtests',
)
