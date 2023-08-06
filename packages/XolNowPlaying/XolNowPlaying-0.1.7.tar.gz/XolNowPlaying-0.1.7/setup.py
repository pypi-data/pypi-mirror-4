from distutils.core import setup

setup(
    name='XolNowPlaying',
    version='0.1.7',
    author='Jonas Svarvaa',
    author_email='jonassvarvaa@gmail.com',
    packages=['xolnowplaying'],
    scripts=['bin/np.py'],
    url='http://pypi.python.org/pypi/XolNowPlaying',
    license='LICENSE.txt',
    description='Read from AudioScrobbler and write to file.',
    long_description=open('README.rst').read(),
    install_requires=[
        "docopt == 0.6.1",
    ],
)
