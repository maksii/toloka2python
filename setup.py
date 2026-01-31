import re
from pathlib import Path

from setuptools import setup

readme = (Path(__file__).resolve().parent / "README.md").read_text(encoding="utf-8")
long_description = readme.split("## Installation", 1)[0].strip()

def read_version():
    init_path = Path(__file__).parent / "toloka2python" / "__init__.py"
    content = init_path.read_text(encoding="utf-8")
    match = re.search(r'^__version__\s*=\s*["\\\']([^"\\\']+)["\\\']', content, re.M)
    if not match:
        raise RuntimeError("Unable to find __version__ in toloka2python/__init__.py")
    return match.group(1)

setup(
    name="toloka2python",
    install_requires=["requests", "beautifulsoup4"],
    packages=["toloka2python", "toloka2python/models"],
    version=read_version(),
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
