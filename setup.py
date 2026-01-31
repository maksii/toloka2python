from pathlib import Path

from setuptools import setup

readme = Path("README.md").read_text(encoding="utf-8")
long_description = readme.split("## Installation", 1)[0].strip()

setup(
    name="toloka2python",
    install_requires=["requests", "beautifulsoup4"],
    packages=["toloka2python", "toloka2python/models"],
    version="0.2.3",
    description="Бібліотека на пітоні для взаємодії з українським торрент-трекером Toloka",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="CakesTwix",
    maintainer="maksii",
    url="https://github.com/maksii/toloka2python",
    project_urls={
        "Source": "https://github.com/maksii/toloka2python",
        "Issues": "https://github.com/maksii/toloka2python/issues",
    },
    license="GPL-3.0-only",
    license_files=["LICENSE"],
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.10",
)
