import setuptools


setuptools.setup(
    author='Paul Hummer',
    author_email='paul@eventuallyanyway.com',
    description='A thin wrapper for accessing the Last.fm API with Twisted',
    install_requires=[
        'twisted',
        'lastfmapi',
    ],
    keywords='last.fm api twisted asynchronous',
    license='http://www.opensource.org/licenses/mit-license.php',
    name='txlastfmapi',
    py_modules=['txlastfmapi'],
    url='https://github.com/rockstar/txlastfmapi',
    version='0.1',
)
