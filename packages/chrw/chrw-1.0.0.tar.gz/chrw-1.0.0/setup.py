from setuptools import setup

if __name__ != "__main__":
    import sys
    sys.exit(1)

def long_desc():
    with open('README.rst', 'rb') as f:
        return f.read()

execfile('chrw/version.py')

kw = {
    "name": "chrw",
    "version": __version__,
    "description": "Python wrapper for the chr url shortener API",
    "long_description": long_desc(),
    "url": "https://github.com/plausibility/chrw",
    "author": "plausibility",
    "author_email": "chris@gibsonsec.org",
    "license": "MIT",
    "packages": ["chrw"],
    "install_requires": ["requests"],
    "zip_safe": False,
    "keywords": "chr url wrapper shorten",
    "classifiers": [
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2"
    ]
}

if __name__ == "__main__":
    setup(**kw)
