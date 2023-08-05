from setuptools import setup, find_packages

setup(
    name="syncstomp",
    version = '0.5.1',
    maintainer='Luminoso, LLC',
    maintainer_email='dev@lumino.so',
    license = "MIT",
    url = 'http://github.com/LuminosoInsight/syncstomp',
    platforms = ["any"],
    description = "Synchronous STOMP library with automatic provider discovery",
    packages=find_packages(),
    install_requires=['plumb-util >= 0.1', 'stomp.py'],
    entry_points={
        'console_scripts':
            ['stomp = syncstomp.cli:main'
             ]}
)
