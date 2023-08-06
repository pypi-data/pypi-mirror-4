from distutils.core import setup

setup(
    name='wise',
    version='0.9',
    author='Henrik Brink',
    author_email='henrik@wise.io',
    packages=['wise','wise.client'],
    url='https://wise.io',
    license='LICENSE.txt',
    description='Client library for the wise.io machine-learning service.',
    install_requires=["requests"],
)
