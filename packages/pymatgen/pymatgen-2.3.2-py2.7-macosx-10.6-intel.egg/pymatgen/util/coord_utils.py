#!/usr/bin/env python

"""
Utilities for manipulating coordinates or list of coordinates, under periodic
boundary conditions or otherwise. Many of these are heavily vectorized in
numpy for performance.
"""

from __future__ import division

__author__ = "Shyue Ping Ong"
__copyright__ = "Copyright 2011, The Materials Project"
__version__ = "1.0"
__maintainer__ = "Shyue Ping Ong"
__email__ = "shyue@mit.edu"
__date__ = "Nov 27, 2011"

import numpy as np
import math
import itertools


def find_in_coord_list(coord_list, coord, atol=1e-8):
    """
    Find the indices of matches of a particular coord in a coord_list.

    Args:
        coord_list:
            List of coords to test
        coord:
            Specific coordinates
        atol:
            Absolute tolerance. Defaults to 1e-8.

    Returns:
        Indices of matches, e.g., [0, 1, 2, 3]. Empty list if not found.
    """
    if len(coord_list) == 0:
        return []
    coords = np.tile(coord, (len(coord_list), 1))
    diff = coord_list - coords
    return np.where(np.all(np.abs(diff) < atol, axis=1))[0]


def in_coord_list(coord_list, coord, atol=1e-8):
    """
    Tests if a particular coord is within a coord_list.

    Args:
        coord_list:
            List of coords to test
        coord:
            Specific coordinates
        atol:
            Absolute tolerance. Defaults to 1e-8.

    Returns:
        True if coord is in the coord list.
    """
    return len(find_in_coord_list(coord_list, coord, atol=atol)) > 0


def get_linear_interpolated_value(x_values, y_values, x):
    """
    Returns an interpolated value by linear interpolation between two values.
    This method is written to avoid dependency on scipy, which causes issues on
    threading servers.

    Args:
        x_values:
            Sequence of x values.
        y_values:
            Corresponding sequence of y values
        x:
            Get value at particular x
    """
    val_dict = dict(zip(x_values, y_values))
    if x < min(x_values) or x > max(x_values):
        raise ValueError("x is out of range of provided x_values")

    for val in sorted(x_values):
        if val < x:
            x1 = val
        else:
            x2 = val
            break

    y1 = val_dict[x1]
    y2 = val_dict[x2]

    return y1 + (y2 - y1) / (x2 - x1) * (x - x1)


def pbc_diff(fcoords1, fcoords2):
    """
    Returns the 'fractional distance' between two coordinates taking into
    account periodic boundary conditions.

    Args:
        fcoords1:
            First set of fractional coordinates. e.g., [0.5, 0.6,
            0.7] or [[1.1, 1.2, 4.3], [0.5, 0.6, 0.7]]. It can be a single
            coord or any array of coords.
        fcoords2:
            Second set of fractional coordinates.

    Returns:
        Fractional distance. Each coordinate must have the property that
        abs(a) <= 0.5. Examples:
        pbc_diff([0.1, 0.1, 0.1], [0.3, 0.5, 0.9]) = [-0.2, -0.4, 0.2]
        pbc_diff([0.9, 0.1, 1.01], [0.3, 0.5, 0.9]) = [-0.4, -0.4, 0.11]
    """
    fdist = np.subtract(fcoords1, fcoords2)
    return fdist - np.round(fdist)


def find_in_coord_list_pbc(fcoord_list, fcoord, atol=1e-8):
    """
    Get the indices of all points in a fracitonal coord list that are
    equal to a fractional coord (with a tolerance), taking into account
    periodic boundary conditions.

    Args:
        fcoord_list:
            List of fractional coords
        fcoord:
            A specific fractional coord to test.
        atol:
            Absolute tolerance. Defaults to 1e-8.

    Returns:
        Indices of matches, e.g., [0, 1, 2, 3]. Empty list if not found.
    """
    if len(fcoord_list) == 0:
        return []
    fcoords = np.tile(fcoord, (len(fcoord_list), 1))
    fdist = fcoord_list - fcoords
    fdist -= np.round(fdist)
    return np.where(np.all(np.abs(fdist) < atol, axis=1))[0]


def in_coord_list_pbc(fcoord_list, fcoord, atol=1e-8):
    """
    Tests if a particular fractional coord is within a fractional coord_list.

    Args:
        fcoord_list:
            List of fractional coords to test
        fcoord:
            A specific fractional coord to test.
        atol:
            Absolute tolerance. Defaults to 1e-8.

    Returns:
        True if coord is in the coord list.
    """
    return len(find_in_coord_list_pbc(fcoord_list, fcoord, atol=atol)) > 0


def get_points_in_sphere_pbc(lattice, frac_points, center, r):
    """
    Find all points within a sphere from the point taking into account
    periodic boundary conditions. This includes sites in other periodic images.

    Algorithm:

    1. place sphere of radius r in crystal and determine minimum supercell
       (parallelpiped) which would contain a sphere of radius r. for this
       we need the projection of a_1 on a unit vector perpendicular
       to a_2 & a_3 (i.e. the unit vector in the direction b_1) to
       determine how many a_1"s it will take to contain the sphere.

       Nxmax = r * length_of_b_1 / (2 Pi)

    2. keep points falling within r.

    Args:
        lattice:
            The lattice/basis for the periodic boundary conditions.
        frac_points:
            All points in the lattice in fractional coordinates.
        center:
            cartesian coordinates of center of sphere.
        r:
            radius of sphere.

    Returns:
        [(site, dist) ...] since most of the time, subsequent processing
        requires the distance.
    """
    recp_len = lattice.reciprocal_lattice.abc
    sr = r + 0.15
    nmax = [sr * l / (2 * math.pi) for l in recp_len]
    pcoords = lattice.get_fractional_coords(center)
    axis_ranges = []
    floor = math.floor
    for i in range(3):
        rangemax = int(floor(pcoords[i] + nmax[i]))
        rangemin = int(floor(pcoords[i] - nmax[i]))
        axis_ranges.append(range(rangemin, rangemax + 1))
    neighbors = []
    n = len(frac_points)
    fcoords = np.array(frac_points)
    frac_2_cart = lattice.get_cartesian_coords
    pts = np.tile(center, (n, 1))
    indices = np.array(range(n))
    for image in itertools.product(*axis_ranges):
        shift = np.tile(image, (n, 1))
        shifted_coords = fcoords + shift
        coords = frac_2_cart(shifted_coords)
        dists = np.sqrt(np.sum((coords - pts) ** 2, axis=1))
        within_r = dists <= r
        d = [shifted_coords[within_r], dists[within_r], indices[within_r]]
        neighbors.extend(np.transpose(d))
    return neighbors
