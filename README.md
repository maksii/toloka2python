<p align="center">
	<img src="https://raw.githubusercontent.com/maksii/toloka2python/main/assets/icon.png" alt="toloka2python logo" /><br>
</p>

# toloka2python

[![CI](https://github.com/maksii/toloka2python/actions/workflows/ci.yml/badge.svg)](https://github.com/maksii/toloka2python/actions/workflows/ci.yml)
[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-yellow.svg)](https://opensource.org/licenses/GPL-3.0)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3670A0?logo=python&logoColor=ffdd54)](https://github.com/maksii/toloka2python)
[![Code size](https://img.shields.io/github/languages/code-size/maksii/toloka2python)](https://github.com/maksii/toloka2python)

Python library for getting information from the Ukrainian torrent tracker Toloka.

> Note: The library is still under development and may not work in all environments.

## Features

- Authenticate and fetch profile information.
- Search torrents via HTML or API search.
- Fetch torrent metadata and file lists.

## Installation

Install directly from this fork:

```bash
pip install git+https://github.com/maksii/toloka2python
```

## Usage

1. Authorization and getting information about yourself
	```python
	from toloka2python import Toloka

	toloka = Toloka("Username", "Password")
	print(toloka.me)
	```
2. Search torrents by title
	```python
	for torrent in toloka.search("Магія"):
	  print(torrent.url)
	```
3. Getting information about another user
	```python
	print(toloka.get_account("https://toloka.to/u123456"))
	```
4. Getting information about a torrent
	```python
	print(toloka.get_torrent("https://toloka.to/t71117"))
	```

## Development

Run the test suite and linting locally:

```bash
python -m unittest discover -s tests -v
ruff check .
```

## Maintainer

- [@maksii](https://github.com/maksii)

## Original Author

- [@CakesTwix](https://github.com/CakesTwix)

## License

- [GPL-3.0](https://choosealicense.com/licenses/gpl-3.0/)
