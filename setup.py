import re
from pathlib import Path

from setuptools import setup


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
    author="CakesTwix",
    license="GPL3",
)
