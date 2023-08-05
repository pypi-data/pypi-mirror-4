from distutils.core import setup

setup(
    name='mtFileUtil',
    version='0.6.2',
    author='Travis Bear',
    author_email='travis_bear@yahoo.com',
    packages=['mtfileutil'],
    scripts=['bin/mtfu_read_sequential_multithread_example.py',
             'bin/mtfu_tail_example.py',
             'bin/mtfu_read_random_example.py',
             'bin/mtfu_read_sequential_singlethread_example.py',
             'bin/mtfu_reverse_seek_example.py'],
    url='http://pypi.python.org/pypi/mtFileUtil/',
    license='LICENSE.txt',
    description='High-performance tools for reading data from text files.',
    long_description=open('README.txt').read(),
    install_requires=[]
)
