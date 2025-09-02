# coding: utf-8
"""Define functions to scrap airfoil coordinates from the UIUC website."""

import re
import urllib.parse

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

    return np.asarray(
        [
            match.groups()
            for line in page_content
            if (match := pattern.match(line))
        ],
        dtype=np.float32,
    )
