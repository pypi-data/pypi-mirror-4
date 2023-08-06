from distutils.core import setup

setup(
    name='FinPy',
    version='0.1.0',
    author='Tsung-Han Yang',
    author_email='blacksburg98@yahoo.com',
    packages=['finpy'],
    package_data={'finpy': ['stock_data/Yahoo/*.csv', '*.txt',
        'stock_data/Yahoo/*.txt', 'stock_data/Yahoo/Lists/*']},
    scripts=['scripts/marketsim.py'],
    url='http://pypi.python.org/pypi/FinPy/',
    license='LICENSE.txt',
    description='Financial Python',
    long_description=open('README.txt').read(),
    install_requires=[
        "NumPy >= 1.6.1",
        "pandas >= 0.7.3",
        "matplotlib >= 1.2.1",
    ],
)

