# airfoildb

A simple script for creating a consistent airfoil database.

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![black](https://github.com/gabrielbdsantos/airfoildb/actions/workflows/black.yml/badge.svg?branch=master)](https://github.com/gabrielbdsantos/airfoildb/actions/workflows/black.yml)

## Installation

### Rye

1. Clone the repository

       git clone https://github.com/gabrielbdsantos/airfoildb
       cd airfoildb

2. Sync the requirements and install it.

       rye sync

### Pip

1. Clone the repository.

       git clone https://github.com/gabrielbdsantos/airfoildb
       cd airfoildb

2. Create a dedicated virtual environment (optional).

       python3 -m venv .venv --clear
       source .venv/bin/activate

3. Install it.

       pip install -r requirements.lock


## Quick start

  1. Download the airfoils from the UIUC website.

         airfoildb download --output airfoildb/raw

  2. Uniformize the airfoils across the entire database.

         airfoildb uniformize --database airfoildb/raw --output airfoildb/uniform

## License

The code is licensed under the MIT terms. For further information, refer to [LICENSE](./LICENSE).
