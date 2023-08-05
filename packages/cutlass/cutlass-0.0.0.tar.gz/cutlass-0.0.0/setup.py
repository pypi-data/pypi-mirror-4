from distutils.core import setup

tests_require = []

setup(
    name="cutlass",
    version="0.0.0",
    author="Sasha Hart",
    author_email="s@sashahart.net",
    url="https://github.com/sashahart/cutlass",
    license="LICENSE",
    packages=["cutlass"],
    #tests_require=tests_require,
    description="Modular library for writing WSGI apps",
    long_description=open('README').read(),
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.1",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
