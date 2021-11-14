# Kiwi.com Python weekend task '21: Martin Dvorak <martin.dvorak@mindforger.com>
#
# Tests
#
from typing import List
from typing import Tuple

import pytest

from solution import oracle


# test utils


def gather_results_list(result: oracle.FlightSearchResult) -> Tuple[List, List]:
    prices: List = []
    times: List = []
    if result:
        for trip in result.trips:
            prices.append(trip.total_price)
            times.append(trip.travel_time)
    return prices, times


# tests


def test_negative_invalid_dataset_path():
    raise NotImplementedError


def test_negative_invalid_src_dst():
    raise NotImplementedError


def test_query_load():
    # augment
    raise NotImplementedError


TASK_SERIALIZATION_EXAMPLE = """[
    {
        "flights": [
            {
                "flight_no": "XC233",
                "origin": "BTW",
                "destination": "WTF",
                "departure": "2021-09-02T05:50:00",
                "arrival": "2021-09-02T8:20:00",
                "base_price": 67.0,
                "bag_price": 7.0,
                "bags_allowed": 2
            },
            {
                "flight_no": "VJ832",
                "origin": "WTF",
                "destination": "REJ",
                "departure": "2021-09-02T11:05:00",
                "arrival": "2021-09-02T12:45:00",
                "base_price": 31.0,
                "bag_price": 5.0,
                "bags_allowed": 1
            }
        ],
        "bags_allowed": 1,
        "bags_count": 1,
        "destination": "REJ",
        "origin": "BTW",
        "total_price": 110.0,
        "travel_time": "6:55:00"
    },
    {
        "flights": [
            {
                "flight_no": "JV042",
                "origin": "BTW",
                "destination": "REJ",
                "departure": "2021-09-01T17:35:00",
                "arrival": "2021-09-01T21:05:00",
                "base_price": 216.0,
                "bag_price": 11.0,
                "bags_allowed": 2
            }
        ],
        "bags_allowed": 2,
        "bags_count": 1,
        "destination": "REJ",
        "origin": "BTW",
        "total_price": 227.0,
        "travel_time": "3:30:00"
    }
]"""


def test_result_serialization():
    # GIVEN
    expected_output = TASK_SERIALIZATION_EXAMPLE
    flight_oracle = oracle.FlightOracle(
        oracle.FlightDataset("datasets/exampleSerialization.csv").load()
    )
    origin = "BTW"
    destination = "REJ"
    bags = 1

    # WHEN
    result: oracle.FlightSearchResult = flight_oracle.find_flights(
        origin=origin,
        destination=destination,
        bags=bags,
        return_ticket=False,
    )

    # THEN
    print(result.to_json())
    assert result.to_json() == expected_output


@pytest.mark.parametrize(
    (
        "dataset_path,origin,destination,bags,return_ticket,"
        "expected_result_count,"
        "expected_first_price,expected_last_price,"
        "expected_first_duration,expected_last_duration"
    ),
    [
        # # direct flight
        # (
        #     "datasets/exampleA.csv",
        #     "WIW",
        #     "ECV",
        #     1,
        #     False,
        #     1,
        #     [245.0 + 12.0],
        #     ["5:10:00"],
        # ),
        # # one flights: direct (1 hop has SHORT overlay)
        # ("datasets/exampleA.csv", "WIW", "RFZ", 1, False, 1, [123.0], ["5:00:00"]),
        # # dataset 0: one way THERE
        # (
        #     "datasets/example0.csv",
        #     "WIW",
        #     "RFZ",
        #     1,
        #     False,
        #     3,
        #     [180.0, 180.0, 180.0],
        #     ["4:30:00", "4:30:00", "4:30:00"],
        # ),
        # # dataset 0: one way BACK
        # (
        #         "datasets/example0.csv",
        #         "RFZ",
        #         "WIW",
        #         1,
        #         False,
        #         3,
        #         [180.0, 180.0, 180.0],
        #         ["4:30:00", "4:30:00", "4:30:00"],
        # ),
        # # dataset 0: return
        # (
        #     "datasets/example0.csv",
        #     "WIW",
        #     "RFZ",
        #     1,
        #     True,
        #     3 * 3,
        #     [360.0, 360.0, 360.0, 360.0, 360.0, 360.0, 360.0, 360.0, 360.0],
        #     [
        #         "4:30:00",
        #         "4:30:00",
        #         "4:30:00",
        #         "4:30:00",
        #         "4:30:00",
        #         "4:30:00",
        #         "4:30:00",
        #         "4:30:00",
        #         "4:30:00",
        #      ],
        # ),
        # dataset 3: one way
        (
                "datasets/example3.csv",
                "WUE",
                "NNB",
                1,
                False,
                137,
                38.0,
                1146.0,
                "4:25:00",
                "1 day, 19:50:00",
        ),
    ],
)
def test_query(
    dataset_path,
    origin,
    destination,
    bags,
    return_ticket,
    expected_result_count,
    expected_first_price, expected_last_price,
    expected_first_duration, expected_last_duration,
):
    #
    # GIVEN
    #
    flight_oracle = oracle.FlightOracle(oracle.FlightDataset(dataset_path).load())

    #
    # WHEN
    #
    result: oracle.FlightSearchResult = flight_oracle.find_flights(
        origin=origin,
        destination=destination,
        bags=bags,
        return_ticket=return_ticket,
    )

    #
    # THEN
    #
    print(
        f"\nRESULT of {origin} -> {destination} (return={return_ticket}):\n"
        f"{result.to_json()}"
    )
    assert result
    assert len(result.trips) == expected_result_count
    assert expected_first_price == result.trips[0].total_price
    assert expected_last_price == result.trips[-1].total_price
    assert expected_first_duration == result.trips[0].travel_time
    assert expected_last_duration == result.trips[-1].travel_time


# TODO test layover SMALLER
# TODO test layover BIGGER
