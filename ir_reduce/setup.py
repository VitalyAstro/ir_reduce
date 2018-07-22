import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ir_reduce",
    version="0.0.1",
    author="Sebastian Meßlinger",
    author_email="sebastian.messlinger@poste.de",
    description="A reduction toolchain for infrared astronomical images",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://krachyon.de/git/reduce/",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Astronomy",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research"
    ),
    keywords='astronomy infrared ccd reduction photometry',
    python_requires='>=3.6',
    install_requires=['astropy>=3', 'numpy>1.14', 'ccdproc>=1.3.0', 'pytest', 'tox']

)
