from distutils.core import setup

setup(
    name='TwitterCounter',
    version='1.1.0',
    author='Jonas Geduldig',
    author_email='boxnumber03@gmail.com',
    packages=['twittercounter'],
    package_data={'': ['credentials.txt']},
    url='https://github.com/geduldig/twittercounter',
    download_url = 'https://github.com/gedldig/twittercounter/tarball/master',
    license='MIT',
    keywords='twitter',
    description='Command line scripts for counting old and new tweets from twitter.com.',
    install_requires = ['puttytat']
)