import os
from distutils.core import setup
from cccontact import get_version

root_dir = os.path.dirname(__file__)
if root_dir != '':
    os.chdir(root_dir)

setup(
    name='django-cccontact',
    version=get_version(),
    license='BSD 3 Clause',
    description='A minimal contact form application for django',
    long_description=open('README.rst').read(),
    author='c&c Design Consultants',
    author_email='studio@designc.co.uk',
    url='https://github.com/designcc/django-cccontact',
    package_data={
        'cccontact' : [
            'templates/cccontact/*.html',
            'templates/cccontact/*.txt',
            'static/cccontact/js/*.js',
        ],
    },
    packages=[
        'cccontact',
        'cccontact.templatetags',
        'cccontact.tests'
    ],
    install_requires=[
        'django-mailer==0.2a1'],
    dependency_links = ['https://github.com/designcc/django-mailer/zipball/master#egg=django-mailer-0.2a1'])
