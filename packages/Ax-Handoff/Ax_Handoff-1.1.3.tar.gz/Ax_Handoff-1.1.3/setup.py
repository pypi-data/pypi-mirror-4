from distutils.core import setup

VERSION = '1.1.3'

def read_readme():
    with open('README.rst') as file:
        return file.read()

classifiers = [
    "Programming Language :: Python",
    "Development Status :: 5 - Production/Stable",
    "Environment :: Web Environment",
    "Environment :: Other Environment",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Topic :: Security :: Cryptography",
    "Topic :: Internet :: WWW/HTTP :: Session",
    ]

setup(
    version = VERSION,
    name = 'Ax_Handoff',
    packages = ['axonchisel', 'axonchisel.handoff', 'axonchisel.handoff.protocol'],
    url = "https://bitbucket.org/dkamins/ax_handoff/",
    description = "Easy secure protocol for passing encrypted structured data over unencrypted channels (such as URLs) while maintaining tamper-proof integrity.",
    author = "Dan Kamins",
    author_email = "dos@axonchisel.net",
    keywords = ["encryption", "cryptography", "single-sign-on", "SSO", "distributed", "handoff", "url"],
    requires = ["pycrypto (>=2.3)"],
    license = "MIT",
    classifiers = classifiers,
    long_description = read_readme(),
)


