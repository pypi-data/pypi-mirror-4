from distutils.core import setup

setup(
    name='Renuntius',
    version='0.1',
    author='Philipp Rautenberg',
    author_email='rautenberg@mpisoc.mpg.de',
    packages=['renuntius',],
    url='https://github.com/MUCAM/Renuntius',
    license='LICENSE.txt',
    description='Renuntius is a RESTful webservice for sending messages.',
    long_description=open('README.rst').read(),
    install_requires=[
        "flask >= 0.9",
        "flask-restless >= 0.9.3",
        "flask-sqlalchemy >= 0.16",
        ],
)
