from distutils.core import setup

setup(
    name='PartitionSets',
    version='0.1.1',
    author='Stefan Drees',
    author_email='stefan@drees.name',
    packages=['partitionsets', 'partitionsets.test'],
    package_data = {
        'partitionsets': ['data/OEIS_A000110.json'],
    },
    scripts=['bin/partition_sets.py', 'bin/partition_showcase.py'],
    url='http://pypi.python.org/pypi/PartitionSets/',
    description='Consolidation of existing third party recipes for partitioning of sets and multisets/bags.',
    long_description=open('README.txt').read(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Environment :: MacOS X',
        'Environment :: Other Environment',
        'Environment :: Win32 (MS Windows)',
        'Intended Audience :: Education',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Education',
        'Topic :: Scientific/Engineering',
        'Topic :: Utilities',
    ],
)
