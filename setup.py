from setuptools import setup


setup(
    name="d2vs",
    version="0.0.5",
    packages=["d2vs"],
    description="diablo 2 vision system is a library to assist with the automation of d2, using only pixels, keyboard and mouse",
    long_description=open("README.md", "r").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/ckcollab/d2vs",
    author="Eric Carmichael",
    author_email="eric@ckcollab.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
    ],
    install_requires=open("requirements.txt", "r").readlines(),

    # Including things from MANIFEST.in
    include_package_data=True,
)
