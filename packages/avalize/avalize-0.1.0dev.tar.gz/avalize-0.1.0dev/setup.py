from distutils.core import setup

setup(
    name='avalize',
    version='0.1.0dev',
    author='Dylan Taylor',
    author_email='dylanjt3@gmail.com',
    packages=['avalize'],
    url='http://github.com/wasdylan/avalize',
    license='LICENSE.txt',
    description='share files over a network.',
    long_description=open('README.txt').read(),
    entry_points = {
        'console_script': [
            'avalize = avalize.__init__.py:go'
        ]
    },
)
