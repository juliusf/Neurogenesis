import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="neurogenesis",
    version="0.0.1",
    author="Julius Flohr",
    author_email="julius.flohr@uni-due.de",
    description="Distributed inet simulation framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/juliusf/Neurogenesis",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
