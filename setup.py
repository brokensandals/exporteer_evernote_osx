import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="exporteer_evernote_osx",
    version="0.0.2",
    author="Jacob Williams",
    author_email="jacobaw@gmail.com",
    description="Exports data from the Mac Evernote app.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/brokensandals/exporteer_evernote_osx",
    packages=setuptools.find_packages('src'),
    package_dir={'':'src'},
    entry_points={
        'console_scripts': [
            'exporteer_evernote_osx = exporteer_evernote_osx.cli:main'
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS :: MacOS X",
    ],
    install_requires=[
    ],
    python_requires='>=3.7',
)
