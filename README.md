# OwnCloud Version Checker

This Python script is designed to automate the process of checking and comparing different versions of OwnCloud, including server packages, desktop clients, and mobile apps. It fetches version information from various web pages and compares it against available changelogs and download pages.

## Features

- Checks for the latest versions of OwnCloud server, desktop, and mobile apps.
- Compares version information from different sources for consistency.
- Reports discrepancies between the declared versions and those found in changelogs.
- Outputs the results in a clear, concise format.

## Usage

Run the script directly in a Python 3 environment:

```bash
python checkVersion.py
```

## Prerequisites

Before running the script, ensure you have Python 3 installed along with the following packages:

```bash
pip install requests beautifulsoup4
```
