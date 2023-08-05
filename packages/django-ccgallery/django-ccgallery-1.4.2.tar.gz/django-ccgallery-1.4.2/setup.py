import os
from distutils.core import setup
from ccgallery import get_version

root_dir = os.path.dirname(__file__)
if root_dir != '':
    os.chdir(root_dir)

setup(
    name='django-ccgallery',
    version=get_version(),
    license='BSD 3 Clause',
    description='A minimal Gallery application for Django',
    long_description=open('README.rst').read(),
    author='c&c Design Consultants LTD',
    author_email='studio@designcc.co.uk',
    url='https://github.com/designcc/django-ccgallery',
    package_data={
        'ccgallery' : [
            'templates/ccgallery/*.html',
            'static/ccgallery/*.jpg',
            'static/ccgallery/css/*.css',
            'static/ccgallery/fancybox/source/*.gif',
            'static/ccgallery/fancybox/source/*.png',
            'static/ccgallery/fancybox/source/*.css',
            'static/ccgallery/fancybox/source/*.js',
            'static/ccgallery/fancybox/source/*.png',
            'static/ccgallery/fancybox/source/helpers/*.png',
            'static/ccgallery/fancybox/source/helpers/*.css',
            'static/ccgallery/fancybox/source/helpers/*.js',
        ],
    },
    packages=[
        'ccgallery',
        'ccgallery.templatetags',
        'ccgallery.tests'
    ],
    install_requires=[
            'django-ccthumbs',
            'markdown2'])
