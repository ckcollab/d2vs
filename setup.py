from setuptools import setup, find_packages


setup(
    name="d2vs",
    version="0.0.1",
    packages=find_packages(),
    description="Save contacts from your terminal",
    long_description=open("README.md", "r").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/wangonya/contacts-cli",
    author="Eric Carmichael",
    author_email="eric@ckcollab.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
    ],
    install_requires=open("requirements.txt", "r").readlines(),
)
