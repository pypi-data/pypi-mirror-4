from distutils.core import setup

setup(
    name='bw-stats-toolkit',
    version='0.7',
    author='Chris Mutel',
    author_email='cmutel@gmail.com',
    url='https://bitbucket.org/cmutel/bw-stats-toolkit',
    packages=['stats_toolkit', 'stats_toolkit.distributions',
        'stats_toolkit.tests'],
    license='BSD 2-clause; LICENSE.txt',
    long_description=open('README.txt').read(),
)
