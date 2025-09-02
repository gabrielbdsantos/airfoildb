# airfoildb

A simple script for creating a consistent airfoil database.

## Installation

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

The code is licensed under the MIT terms. For further information, refer to
[LICENSE](./LICENSE).
