import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="lexit",
    version="0.0.1",
    author="Sergey Tikhonov",
    author_email="srg.tikhonov@gmail.com",
    long_description=long_description,
    long_description_content_type="text/markdown",
    description="An open source lexer generation written in Python 3.6",
    url="https://github.com/pypa/example-project",
    packages=['lexit'],
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
