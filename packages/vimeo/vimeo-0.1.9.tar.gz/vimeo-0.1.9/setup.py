import re
from setuptools import setup

version = None
for line in open('./vimeo/__init__.py'):
    m = re.search('__version__\s*=\s*(.*)', line)
    if m:
        version = m.group(1).strip()[1:-1]  # quotes
        break
assert version

setup(
    name='vimeo',
    version=version,
    description='Python module for using Vimeo API.',
    author='Nirmal Kumar',
    author_email='rkumarnirmal@gmail.com',
    url='https://github.com/rkumarnirmal/python-vimeo',
    packages=['vimeo'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet',
        'Topic :: Multimedia :: Video',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='vimeo internet api',
    scripts=['vimeo/client.py'],
    license='MIT',
    install_requires=[
        "requests == 0.13.1",
        "simplejson >= 2.1.6",
        "oauth2 >= 1.5.170",
    ]
)
