# Licensed to Elasticsearch B.V under one or more agreements.
# Elasticsearch B.V licenses this file to you under the Apache 2.0 License.
# See the LICENSE file in the project root for more information

# File called _pytest for PyCharm compatability

import pytest
from matplotlib.testing.decorators import check_figures_equal

from eland.tests.common import TestData


@check_figures_equal(extensions=["png"])
def test_plot_hist(fig_test, fig_ref):
    test_data = TestData()

    pd_flights = test_data.pd_flights()[
        ["DistanceKilometers", "DistanceMiles", "FlightDelayMin", "FlightTimeHour"]
    ]
    ed_flights = test_data.ed_flights()[
        ["DistanceKilometers", "DistanceMiles", "FlightDelayMin", "FlightTimeHour"]
    ]

    # This throws a userwarning
    # (https://github.com/pandas-dev/pandas/blob/171c71611886aab8549a8620c5b0071a129ad685/pandas/plotting/_matplotlib/tools.py#L222)
    with pytest.warns(UserWarning):
        pd_ax = fig_ref.subplots()
        pd_flights.hist(ax=pd_ax)

    # This throws a userwarning
    # (https://github.com/pandas-dev/pandas/blob/171c71611886aab8549a8620c5b0071a129ad685/pandas/plotting/_matplotlib/tools.py#L222)
    with pytest.warns(UserWarning):
        ed_ax = fig_test.subplots()
        ed_flights.hist(ax=ed_ax)


@check_figures_equal(extensions=["png"])
def test_plot_filtered_hist(fig_test, fig_ref):
    test_data = TestData()

    pd_flights = test_data.pd_flights()[
        ["DistanceKilometers", "DistanceMiles", "FlightDelayMin", "FlightTimeHour"]
    ]
    ed_flights = test_data.ed_flights()[
        ["DistanceKilometers", "DistanceMiles", "FlightDelayMin", "FlightTimeHour"]
    ]

    pd_flights = pd_flights[pd_flights.FlightDelayMin > 0]
    ed_flights = ed_flights[ed_flights.FlightDelayMin > 0]

    # This throws a userwarning
    # (https://github.com/pandas-dev/pandas/blob/171c71611886aab8549a8620c5b0071a129ad685/pandas/plotting/_matplotlib/tools.py#L222)
    with pytest.warns(UserWarning):
        pd_ax = fig_ref.subplots()
        pd_flights.hist(ax=pd_ax)

    # This throws a userwarning
    # (https://github.com/pandas-dev/pandas/blob/171c71611886aab8549a8620c5b0071a129ad685/pandas/plotting/_matplotlib/tools.py#L222)
    with pytest.warns(UserWarning):
        ed_ax = fig_test.subplots()
        ed_flights.hist(ax=ed_ax)
