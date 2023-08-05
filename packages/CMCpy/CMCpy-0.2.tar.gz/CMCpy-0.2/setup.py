import distribute_setup
distribute_setup.use_setuptools()

from setuptools import setup, find_packages
setup(
    name = "CMCpy",
    version = "0.2",
    packages = find_packages(),
    scripts = ['bin/cmc'],

    # Project uses reStructuredText, so ensure that the docutils get
    # installed or upgraded on the target machine
    install_requires = ['docutils>=0.3','numpy'],

    package_data = {
        # If any package contains *.txt or *.rst files, include them:
        '': ['*.txt', '*.rst'],
        # And include any *.msg files found in the 'hello' package, too:
        'hello': ['*.msg'],
    },

    entry_points = {
        'console_scripts': [
            'cmc = cmcpy.__main__:main',
        ]
    },
    
    extras_require = {
        'CUDA':  ["pycuda"],
    },

    # metadata for upload to PyPI
    author = "David H. Ardell",
    author_email = "dardell@ucmerced.edu",
    description = 'Genetic Code-Message Coevolution in Python',
    license = "Apache 2.0",
    keywords = "",
    url = "http://pypi.python.org/pypi/CMCpy/",
    long_description=open('README.txt').read(),
)
