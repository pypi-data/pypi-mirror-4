from distutils.core import setup

setup(
    name="shelve2",
    version="1.0",
    url="https://bitbucket.org/fk/shelve2",
    author="Felix Krull",
    author_email="f_krull@gmx.de",
    description="Persistent dictionary with modular serialiser support",
    long_description="""\
An expanded drop-in replacement for the ``shelve`` module with modular support
for additional serialisers. JSON support is provided as a more secure
alternative to pickle.
""",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Python Software Foundation License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    license="Python Software Foundation License",
    download_url="https://pypi.python.org/pypi/shelve2",
    py_modules=["shelve2"])
