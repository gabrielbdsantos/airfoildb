# airfoildb

A simple script for creating a consistent airfoil database.


## Instalation

It is recommended to use [Poetry](https://python-poetry.org).

  ```bash
  poetry install git+https://github.com/gabrielbdsantos/airfoildb
  ```

or

  ```bash
  git clone https://github.com/gabrielbdsantos/airfoildb
  cd airfoildb
  poetry install
  ```

## Quick start

  1. Download the airfoils from the UIUC website.

     ```bash
     airfoildb download --output airfoildb/raw
     ```

  2. Uniformize the airfoils across the entire database.

     ```bash
     airfoildb uniformize --database airfoildb/raw --output airfoildb/uniform
     ```

## License

The code is licensed under the MIT terms. For further information, refer to [LICENSE](./LICENSE).
