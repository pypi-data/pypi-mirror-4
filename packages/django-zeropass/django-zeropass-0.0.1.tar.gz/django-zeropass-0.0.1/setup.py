import os
from distutils.core import setup
from zeropass import get_version

root_dir = os.path.dirname(__file__)
if root_dir != '':
    os.chdir(root_dir)

setup(
    name='django-zeropass',
    version=get_version(),
    license='BSD 3 Clause',
    description='An app to allow password free logins',
    long_description=open('README.md').read(),
    author='Jamie Curle',
    author_email='jamie@obscuremetaphor.co.uk',
    url='https://django-zeropass.obscuremetaphor.co.uk',
    package_data={
        'zeropass' : [
            'templates/zeropass/*.html',
        ],
    },
    packages=[
        'zeropass',
        'zeropass.templatetags',
        'zeropass.management.commands',
        'zeropass.tests'
    ],
    classifiers = [
        'Development Status :: 4 - Beta',
        'Framework :: Django',],
    install_requires=[
        'django >= 1.4'
    ])
