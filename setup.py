import setuptools

with open("README.md") as file:
    read_me_description = file.read()

setuptools.setup(
    name="Detector license plates wrapper",
    version="0.1",
    author="egor.bakharev",
    author_email="progr18@pancir.it",
    description="This is a wrapper for DTKLPR neural network api",
    long_description=read_me_description,
    long_description_content_type="text/markdown",
    url="https://git.pancir.it/egor.bakharev/DTKLP-wrapper",
    packages=['dtklp_wrapper'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.5',
)