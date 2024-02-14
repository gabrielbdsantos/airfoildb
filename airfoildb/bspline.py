# coding: utf-8
"""Define functions related to spline representation."""

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
        A list of vector arrays representing the curve. It must be passed as a
        two-dimensional array.
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
