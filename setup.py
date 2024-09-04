from setuptools import setup, find_packages

setup(
    name="set_crafter",
    version="0.1.0",
    author="Pim Meerdink",
    author_email="pimmeerdink@hotmail.com",
    description="A short description of your package",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        # List your project dependencies here
        # "requests>=2.25.1",
        # "numpy>=1.20.0",
    ],
)
