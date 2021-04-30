import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name="panda3d-livecode",
    version="0.0.001",
    author="janEntikan",
    author_email="bandaibandai@rocketship.com",
    description="Live-coding environment for panda3d",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/janentikan/panda3d-livecode",
    packages=["livecode"],
    install_requires=[
        "panda3d>=1.10",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication",
        "Operating System :: OS Independent",
    ],
)
