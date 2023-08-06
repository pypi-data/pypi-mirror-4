from setuptools import setup

if __name__ != "__main__":
    import sys
    sys.exit(1)

def long_desc():
    with open('README.rst', 'rb') as f:
        return f.read()

kw = {
    "name": "spiffing",
    "version": "1.1.0",
    "description": "The gentleman's CSS pre-processor, to convert correct English CSS to American English CSS (and the reverse).",
    "long_description": long_desc(),
    "url": "https://github.com/plausibility/spiffing.py",
    "author": "plausibility",
    "author_email": "chris@gibsonsec.org",
    "license": "MIT",
    "packages": ["spiffing"],
    "zip_safe": False,
    "keywords": "css preprocessor markup english jam",
    "classifiers": [
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2",
        "Topic :: Text Processing"
    ]
}

if __name__ == "__main__":
    setup(**kw)
