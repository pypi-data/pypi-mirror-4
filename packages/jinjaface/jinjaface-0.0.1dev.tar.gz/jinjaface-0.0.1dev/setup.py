from distutils.core import setup

setup(
    name='jinjaface',
    author='aldeka',
    version='0.0.1dev',
    packages=['jinjaface',],
    license='Apache License v2.0',
    long_description=open('README.txt').read(),
    install_requires=[
        "jinja2 >= 2.6",
    ],
)
