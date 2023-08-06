from distutils.core import setup


setup(
    name='django-ip2language',
    version='0.1',
    author='Marco Westerhof',
    author_email='westerhof.marco@gmail.com',
    packages=['ip2language'],
    # url='http://pypi.python.org/pypi/TowelStuff/',
    license='LICENSE.txt',
    description='A django module to derive a language code based on visitor IP',
    long_description=open('README.txt').read(),
    install_requires=[
        "pygeoip >= 0.2.6",
    ],
)
