from setuptools import setup, find_packages
import os, re

here = os.path.abspath(os.path.dirname(__file__))

v = open(os.path.join(here, 'src', 'nfd2nfc', '__init__.py'))
version = re.compile(r".*__version__ = '(.*?)'", re.S).match(v.read()).group(1)
v.close()

install_requires = [
    'docopt'
]

setup(
    name='nfd2nfc',
    version=version,
    description="Convert Mac OSX NFD unicode filename to NFC unicode",
    classifiers=[
    ],
    keywords='MacOSX unicode NFD NFC',
    author='Stephane Klein',
    author_email='contact@stephane-klein.info',
    url='',
    license='',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    entry_points={
        'console_scripts': [
            'nfd2nfc=nfd2nfc:main'
        ]
    }
)
