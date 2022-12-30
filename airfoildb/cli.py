# coding: utf-8
"""Command line interface for the airfoil-database."""

import functools
import multiprocessing
import pathlib

import typer

from .bspline import curvature_based_bspline
from .io import export_airfoil_data, export_as_bspline, list_files_in_directory
from .webscrap import list_airfoil_urls

app = typer.Typer(add_completion=False, no_args_is_help=True)


@app.command()
def download(
    output: pathlib.Path = typer.Option(..., help="The output directory."),
    force: bool = typer.Option(
        default=False, help="Overwrite existing files."
    ),
):
    """Download airfoil data from the UIUC database."""
    # Create the output directory if it already does not exist.
    output.mkdir(parents=True, exist_ok=True)

    # We are doing just web scraping. It should be okay to use more processes
    # than the maximum number of CPUS.
    with multiprocessing.Pool(
        processes=multiprocessing.cpu_count() * 4
    ) as pool:
        func = functools.partial(
            export_airfoil_data, output_dir=output, force=force
        )
        pool.map(func, list_airfoil_urls())


@app.command()
def uniformize(
    database: pathlib.Path = typer.Option(
        ..., help="Where to read the files from."
    ),
    output: pathlib.Path = typer.Option(
        ..., help="Where to save the smoothed files."
    ),
    num_points: int = typer.Option(default=192, help="The number of points."),
    degree: int = typer.Option(default=3, help="The B-spline degree."),
    unsmoother: float = typer.Option(
        default=50, help="Reduce the curvature-based smoothing factor."
    ),
    force: bool = typer.Option(
        default=False, help="Overwrite existing files."
    ),
):
    """Uniformize the coordinates accross the database using B-splines."""
    # Create the output directory if it already does not exist.
    output.mkdir(parents=True, exist_ok=True)

    for file in list_files_in_directory(database):
        # For some reason, scipy.interpolate.splprep cannot approximate some
        # airfoil coordinates to a B-spline, which causes the routine to throw
        # a ValueError.
        # So far, I could not find what causes such behavior. As the error only
        # affects 3 airfoils, a try-except is completely acceptable as a
        # workaround.
        try:
            export_as_bspline(
                file=file,
                output_dir=output,
                func=functools.partial(
                    curvature_based_bspline,
                    npoints=num_points,
                    k=degree,
                    smoother=unsmoother,
                ),
                force=force,
            )
        except ValueError:
            pass
