#!/usr/bin/env python
# coding=utf-8
"""Fetch airfoild data from the UIUC airfoil database.

optional arguments:
  -h, --help    show this help message and exit
  --output DIR  the output directory
  --force       force an update of all data
"""

import argparse
import multiprocessing
import os
import re
import urllib.parse
from functools import partial

import numpy as np
import requests
from bs4 import BeautifulSoup
from numpy.typing import NDArray

BASE_URL = "https://m-selig.ae.illinois.edu"
SEARCH_PATTERN = re.compile("^\\s*([0-9\\.]+)\\s+([0-9\\.\\-]+)\\s*$")


def get_url_content(url: str) -> bytes:
    """Access a given url and return its content."""
    page = requests.get(url)

    if page.status_code != requests.codes.ok:
        raise requests.HTTPError(f"Unable to access {url}")

    return page.content


def list_airfoil_urls(url: str = f"{BASE_URL}/ads/coord_seligFmt/") -> tuple:
    """Get the link for each airfoil found in the base url."""
    page = get_url_content(url)
    soup = BeautifulSoup(page, "html.parser")

    return tuple(
        [
            urllib.parse.urljoin(url, link.attrs["href"])
            for link in soup.select("a")
            if link.text.endswith(".dat")
        ]
    )


def read_airfoil_data(
    url: str, pattern: re.Pattern = SEARCH_PATTERN
) -> NDArray:
    """Read airfoil data from a urls."""
    page = get_url_content(url)
    page_content = page.decode().splitlines()

    return np.asfarray(
        [
            match.groups()
            for line in page_content
            if (match := pattern.match(line))
        ]
    )


def export_airfoil_data(
    url: str, output_dir: str, force: bool = False
) -> None:
    """Export airfoil data to file."""
    filename = url.split("/")[-1]
    output = os.path.join(output_dir, filename)

    # Check whether the file already exists in the output directory. If yes,
    # there is no need to download the data again. To force an update, use the
    # `force` flag.
    if not os.path.isfile(output) or force:
        print(f"Saving {url} data to {output}.")
        np.savetxt(output, read_airfoil_data(url), fmt="%.6e")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Fetch airfoild data from an online database."
    )
    parser.add_argument(
        "--output",
        metavar="DIR",
        type=str,
        default=r"./data/database",
        help="the output directory",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="force an update of all data",
    )
    args = parser.parse_args()

    # Check whether the output directory exists.
    if not os.path.exists(args.output):
        os.makedirs(args.output, mode=0o755)

    # We are doing just web scraping. It should not do any harm to use 4 times
    # more processes than the maximum number of CPUS.
    with multiprocessing.Pool(
        processes=multiprocessing.cpu_count() * 4
    ) as pool:
        func = partial(
            export_airfoil_data, output_dir=args.output, force=args.force
        )
        pool.map(func, list_airfoil_urls())
