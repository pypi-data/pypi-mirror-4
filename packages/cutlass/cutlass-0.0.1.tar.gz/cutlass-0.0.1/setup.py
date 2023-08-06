from distutils.core import setup


def get_version():
    "Extract version string from cutlass/__init__.py"
    import os
    import re
    base = os.path.abspath(os.path.dirname(__file__))
    version_regex = re.compile(r'^__version__ = "(.*?)"\n\Z')
    init_py_path = os.path.join(base,  "cutlass", "__init__.py")
    with open(init_py_path, 'r') as init_py:
        version_string = None
        for line in init_py:
            match = version_regex.match(line)
            if match:
                version_string = match.group(1)
    return version_string


setup(
    name="cutlass",
    version=get_version(),
    author="Sasha Hart",
    author_email="s@sashahart.net",
    url="https://github.com/sashahart/cutlass",
    license="LICENSE",
    packages=["cutlass"],
    description="Modular library for writing WSGI apps",
    long_description=open('README').read(),
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX",
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
