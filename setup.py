import adhoc
from setuptools import setup, find_packages
from setuptools.command.test import test

setup(
    name='django-adhoc',
    version=adhoc.__version__,
    description='Flexible Django CMS with edit-in-place capability',
    long_description=open('readme.markdown').read(),
    author='Greg Brown',
    author_email='greg@gregbrown.co.nz',
    url='https://github.com/gregplaysguitar/djangocms2000',
    packages=['adhoc'],
    platforms='any',
    zip_safe=False,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Framework :: Django',
    ],
)
