#!/usr/bin/env python
from setuptools import setup, find_packages
from os.path import dirname, join
import sys, os

# When creating the sdist, make sure the django.mo file also exists:
if 'sdist' in sys.argv:
    try:
        os.chdir('fluent_contents')
        from django.core.management.commands.compilemessages import compile_messages
        compile_messages(sys.stderr)
    finally:
        os.chdir('..')


setup(
    name='django-fluent-contents',
    version='0.8.5',
    license='Apache License, Version 2.0',

    install_requires=[
        'django-polymorphic>=0.2',
        'django-tag-parser>=1.0.0',
        'django-template-analyzer>=1.1.0',
    ],
    requires=[
        'Django (>=1.3)',   # Using staticfiles
    ],
    extras_require = {
        'code': ['Pygments'],
        'disquscommentsarea': ['django-disqus'],
        'formdesignerlink': ['django-form-designer'],
        'markup': ['docutils', 'textile', 'Markdown>=1.7'],
        'oembeditem': ['micawber>=0.2.6'],
        'text': ['django-wysiwyg>=0.5.1'],
        'twitterfeed': ['twitter-text-py>=1.0.3'],
    },
    dependency_links = [
        'git+https://github.com/philomat/django-form-designer.git#egg=django-form-designer-dev',
    ],

    description='A widget engine to display various content on Django pages',
    long_description=open(join(dirname(__file__), 'README.rst')).read(),

    author='Diederik van der Boor',
    author_email='opensource@edoburu.nl',

    url='https://github.com/edoburu/django-fluent-contents',
    download_url='https://github.com/edoburu/django-fluent-contents/zipball/master',

    packages=find_packages(exclude=('example*',)),
    include_package_data=True,

    test_suite = 'runtests',

    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
