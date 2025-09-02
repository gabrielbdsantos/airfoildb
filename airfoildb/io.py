# coding: utf-8
"""Define I/O functionalities."""

import glob
import pathlib
from typing import Callable

import numpy as np
from numpy.typing import NDArray

from .bspline import curvature_based_bspline
from .webscrap import read_airfoil_data


def list_files_in_directory(
    directory: pathlib.Path, extension: str = ".dat"
) -> list:
    """List files in directory.

    Parameters
    ----------
    directory
        The relative or absolute path to the directory.
    extension
        Only list files with a specific extension. An empty string will
        consider all extensions as valid ones.

    Return
    ------
        A list of path-like strings.
    """
    if not directory.is_dir():
        raise TypeError(f"It seems that {directory} is not a directory.")

    return sorted(glob.glob(f"{directory}/*{extension}"))


def export_airfoil_data(
    url: str, output_dir: pathlib.Path, force: bool = False
) -> None:
    """Export airfoil data to file."""
    filename = url.split("/")[-1]
    output = output_dir / filename

    # Check whether the file already exists in the output directory. If yes,
    # there is no need to download the data again. To force an update, use the
    # `force` flag.
    if not output.is_file() or force:
        print(f"+ {url} -> {output}")
        np.savetxt(output, read_airfoil_data(url), fmt="%.6e")


def export_as_bspline(
    file: str,
    output_dir: pathlib.Path,
    func: Callable[[NDArray], NDArray] = curvature_based_bspline,
    rename_fn: Callable[[pathlib.Path, str], pathlib.Path] = lambda out,
    file: out / f"uniform_{file.split('/')[-1]}",
    force: bool = False,
) -> None:
    """Convert the airfoil to a curvature-based B-spline representation.

    Parameters
    ----------
    file
        Path to a file containing a list of sample vector arrays representing
        the curve.
    output_dir
        The output directory.
    func
        A function that converts the list of sample vectors to a B-spline
        representation.
    rename_fn
        A function that renames the exported file based on the output directory
        and the read filename.
    force
        Whether to force the convertion if the output file already exists.
    """
    output = rename_fn(output_dir, file)

    # Check whether the file already exists in the output directory. If yes,
    # there is no need to convert the data again. To force an update, use the
    # `force` flag.
    if not output.is_file() or force:
        np.savetxt(output, func(np.genfromtxt(file).T))
