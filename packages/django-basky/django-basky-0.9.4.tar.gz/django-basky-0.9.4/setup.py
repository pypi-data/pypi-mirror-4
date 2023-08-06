import os
from distutils.core import setup
from basky import get_version

root_dir = os.path.dirname(__file__)
if root_dir != '':
    os.chdir(root_dir)

setup(
    name='django-basky',
    version=get_version(),
    license='BSD 3 Clause',
    description='A extensible basket for your django project',
    long_description=open('README.md').read(),
    author='Jamie Curle',
    author_email='me@jamiecurle.co.uk',
    url='http://django-basky.readthedocs.org',
    package_data={
        'basky' : [
            'templates/basky/*.html',
        ],
    },
    packages=[
        'basky',
        'basky.templatetags',
    ],
    install_requires=[
        'django >= 1.5'
    ],
)
