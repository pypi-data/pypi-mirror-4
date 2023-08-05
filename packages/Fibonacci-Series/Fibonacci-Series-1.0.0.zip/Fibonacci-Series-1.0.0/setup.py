from distutils.core import setup

setup(
    name='Fibonacci-Series',
    version='1.0.0',
    author='Saad Bin Akhlaq',
    author_email='saad.18@gmail.com',
    packages=['fib1_fib2'],
    scripts=['bin/fib1_fib2.py'],
    url='http://pypi.python.org/pypi/fib1_fib2/',
    license='LICENSE.txt',
    description='Useful Fibonacci Series',
    long_description=open('README.txt').read(),
    install_requires=[]
)