from distutils.core import setup

setup(
    name='django-fbrealtime',
    version='0.1.0',
    author='Nathan Jhaveri',
    author_email='jhaveri@umich.edu',
    url='https://github.com/n8j/django-fbrealtime',
    packages=['fbrealtime',],
    license='MIT',
    description='Django app for receiving realtime facebook updates',
    long_description=open('README.txt').read(),
    install_requires=['Django>=1.4.0',],
)

