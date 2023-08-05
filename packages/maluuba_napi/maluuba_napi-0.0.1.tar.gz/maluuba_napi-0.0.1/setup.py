from distutils.core import setup

setup(
    name='maluuba_napi',
    version='0.0.1',
    author='Maluuba',
    author_email='napi@maluuba.com',
    packages=['maluuba_napi'],
    url='http://developer.maluuba.com',
    license='LICENSE',
    description='A simple wrapper for consuming the Maluuba NLP API',
    long_description=open('README.md').read(),
    install_requires=[
        'requests >= 0.14.1'
    ]
)
