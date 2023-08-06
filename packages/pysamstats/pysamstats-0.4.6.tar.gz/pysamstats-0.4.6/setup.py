from distutils.core import setup
from distutils.extension import Extension
from ast import literal_eval


def get_version(source='pysamstats.pyx'):
    with open(source) as f:
        for line in f:
            if line.startswith('VERSION'):
                return literal_eval(line.partition('=')[2].lstrip())
    raise ValueError("VERSION not found")


def get_include():
    try:
        import pysam
    except ImportError:
        pass
    else:
        return pysam.get_include()


def get_defines():
    try:
        import pysam
    except ImportError:
        pass
    else:
        return pysam.get_defines()


setup(
    name='pysamstats',
    version=get_version(),
    author='Alistair Miles',
    author_email='alimanfoo@googlemail.com',
    url='https://github.com/alimanfoo/pysamstats',
    license='MIT Licenses',
    description='A Python utility for calculating statistics per genome position based on pileups from a SAM or BAM file.',
    scripts=['pysamstats'],
    ext_modules = [Extension('pysamstats', 
                             ['pysamstats.c'], 
                             include_dirs=get_include(),
                             define_macros=get_defines()),
                   ],
    classifiers=['Intended Audience :: Developers',
                 'License :: OSI Approved :: MIT License',
                 'Programming Language :: Python',
                 'Topic :: Software Development :: Libraries :: Python Modules'
                 ],
    install_requires=['pysam>=0.7.4', 'numpy>=1.6'],
)


