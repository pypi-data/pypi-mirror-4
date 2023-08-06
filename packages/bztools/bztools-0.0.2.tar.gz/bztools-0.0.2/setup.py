import os

from setuptools import setup, find_packages

root = os.path.abspath(os.path.dirname(__file__))
path = lambda *p: os.path.join(root, *p)


setup(
    name='bztools',
    version='0.0.2',
    description='Models and scripts to access the Bugzilla REST API.',
    long_description=open(path('README.rst')).read(),
    author='Jeff Balogh',
    author_email='me@jeffbalogh.org',
    url='http://github.com/mozilla/bztools',
    license='BSD',
    zip_safe=False,
    # install_requires=['remoteobjects>=1.1'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    entry_points={
        'console_scripts': [
            'bzattach = scripts.attach:main',
        ],
    },
    dependency_links = [
        'https://github.com/mozilla/check/tarball/master#egg=check',
        'https://github.com/mozilla/remoteobjects/tarball/master#egg=remoteobjects'
    ],
    install_requires=[
        'Jinja2 == 2.6',
        'argparse == 1.2.1',
        'certifi == 0.0.8',
        'chardet == 1.0.1',
        'check',
        'httplib2 == 0.7.4',
        'keyring == 1.2.2',
        'path.py == 2.2.2',
        'pep8 == 0.6.1',
        'pyflakes == 0.5.0',
        'python-dateutil == 1.5',
        'remoteobjects',
        'requests == 0.10.6',
        'simplejson == 2.3.3',
        'wsgiref == 0.1.2',
    ],
    setup_requires=["hgtools"],
    packages=find_packages(),
    include_package_data=True,
)
