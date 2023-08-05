from distutils.core import setup

setup(
    name='bam2fpkc',
    version='0.1.0',
    author='Michael Imelfort',
    author_email='mike@mikeimelfort.com',
    packages=['bam2fpkc', 'bam2fpkc.test'],
    scripts=['bin/bam2fpkc'],
    url='http://pypi.python.org/pypi/bam2fpkc/',
    license='LICENSE.txt',
    description='bam2fpkc',
    long_description=open('README.txt').read(),
    install_requires=[
        "pysam >= 0.6",
        "numpy >= 1.6.1",
    ],
)
