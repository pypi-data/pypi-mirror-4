from setuptools import setup

setup(
    name='rpitwit',
    version='0.1.0',
    author='Mario Gomez',
    author_email='mxgxw.alpha@gmail.com',
    packages=['rpitwit'],
    url='http://pypi.python.org/pypi/RPiTwit/',
    license='LICENSE.txt',
    description='Remote control your RaspberryPI from Twitter.',
    long_description=open('README.txt').read(),
    install_requires=[
        "twitter >= 1.9.0",
    ],
    entry_points="""
    # -*- Entry points: -*-
    [console_scripts]
    rpitwit=rpitwit.cmdline:main
    """,
)
