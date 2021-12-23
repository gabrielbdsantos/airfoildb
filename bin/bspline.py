#!/usr/bin/env python
# coding=utf-8
"""Uniformize shape representation accross the database using B-spline.

optional arguments:
  -h, --help      show this help message and exit
  -n N            number of points for the B-spline
  -k K            degree of the B-spline
  -s S            smooth the distribution based on curvature
  --database DIR  the database path
  --output DIR    the output directory
  --force         force an update of all data
"""

import argparse
import os
from functools import partial
from typing import Callable

import numpy as np
import scipy.integrate
import scipy.interpolate
from numpy.typing import NDArray


def curvature_based_bspline(
    original: NDArray,
    npoints: int = 200,
    k: int = 3,
    s: float = 1e-6,
    smoother: float = 10,
) -> NDArray:
    """Curvature-based B-spline approximation of N points.

    Parameters
    ----------
    original
        A list of sample vector arrays representing the curve. It must be
        passed as a two-dimensional array in the form of (x, y).
    k
        Degree of the spline. Cubic splines are recommended. Even values of k
        should be avoided especially with a small s-value. 1 <= k <= 5, default
        is 3.
    s
        A smoothing condition. The amount of smoothness is determined by
        satisfying the conditions: sum((w * (y - g))**2,axis=0) <= s, where
        g(x) is the smoothed interpolation of (x,y). The user can use s to
        control the trade-off between closeness and smoothness of fit. Larger s
        means more smoothing while smaller values of s indicate less smoothing.
        Recommended values of s depend on the weights, w. If the weights
        represent the inverse of the standard-deviation of y, then a good s
        value should be found in the range (m-sqrt(2*m),m+sqrt(2*m)), where m
        is the number of data points in x, y, and w.
    smoother
        A quantity to smooth out the curvature cummulative integral; i.e., the
        greater this value, the more homogeneous the spacing between points.

    Return
    ------
        A B-spline approximation via a curvature-based evaluation.
    """
    # Find the B-spline representation of the curve.
    tck, u = scipy.interpolate.splprep(original, k=k, s=s)

    # Create a fine discrete space.
    uu = np.linspace(u.min(), u.max(), 1000)

    # Calculate the B-spline curvature.
    dx, dy = scipy.interpolate.splev(uu, tck, der=1)
    ddx, ddy = scipy.interpolate.splev(uu, tck, der=2)
    curv = np.abs(ddx * dy - dx * ddy) / (dx * dx + dy * dy) ** 1.5 + smoother

    # Calculate the curvature cumulative integral.
    curv_int = scipy.integrate.cumtrapz(curv, uu, initial=0.0)

    # Sample the curvature cumulative integral with N points.
    curv_int_sample = np.linspace(0, curv_int.max(), npoints)

    # Interpolate the values to the new (coarser) discrete space.
    u_new = scipy.interpolate.interp1d(curv_int, uu)(curv_int_sample)

    # Evaluate the B-spline at the new discrete space.
    return np.array(scipy.interpolate.splev(u_new, tck, der=0)).T


def list_files_in_directory(directory: str, extension: str = ".dat") -> list:
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
    return [file for file in os.listdir(directory) if file.endswith(extension)]


def export_as_bspline(
    file: str,
    output_dir: str,
    func: Callable[[NDArray], NDArray] = curvature_based_bspline,
    renaming: Callable[[str, str], str] = lambda out, file: os.path.join(
        out, "uniform_" + file.split("/")[-1]
    ),
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
    renaming
        A function that renames the exported file based on the output directory
        and the read filename.
    force
        Whether to force the convertion if the output file already exists.
    """
    output = renaming(output_dir, file)

    # Check whether the file already exists in the output directory. If yes,
    # there is no need to convert the data again. To force an update, use the
    # `force` flag.
    if not os.path.isfile(output) or force:
        np.savetxt(
            output,
            func(np.genfromtxt(file).T),
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
            "Uniformize shape representation accross the database using"
            " B-splines."
        )
    )
    parser.add_argument(
        "-n",
        metavar="N",
        type=int,
        default=200,
        help="number of points for the B-spline",
    )
    parser.add_argument(
        "-k",
        metavar="K",
        type=int,
        default=3,
        help="degree of the B-spline",
    )
    parser.add_argument(
        "-s",
        metavar="S",
        type=int,
        default=30,
        help="smooth the distribution based on curvature",
    )
    parser.add_argument(
        "--database",
        metavar="DIR",
        type=str,
        default="./data/database",
        help="the database path",
    )
    parser.add_argument(
        "--output",
        metavar="DIR",
        type=str,
        default="./data/uniform",
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
        os.makedirs(args.output, mode=0o775)

    for file in list_files_in_directory(args.database):
        # For some reason, scipy.interpolate.splprep cannot approximate some
        # airfoil coordinates to a B-spline, which causes the routine to throw
        # a ValueError.
        # So far, I could not find what causes such behavior. As the error only
        # affects 3 airfoils, a try-except is completely acceptable as a
        # workaround.
        try:
            export_as_bspline(
                file=os.path.join(args.database, file),
                output_dir=args.output,
                func=partial(
                    curvature_based_bspline,
                    npoints=args.n,
                    k=args.k,
                    smoother=args.s,
                ),
                force=args.force,
            )
        except ValueError:
            pass
