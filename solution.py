# Kiwi.com Python weekend task '21: Martin Dvorak <martin.dvorak@mindforger.com>
#
# Solution of https://github.com/kiwicom/python-weekend-xmas-task
#
# Usage examples:
#
#   python3 -m solution example/example0.csv RFZ WIW --bags=1 --return
#   python3 -m solution -h
#
# IMPORTANT task assignment related notes:
#
# - travel_time LONGER than 1 day is serialized using timedelta format,
#   for instance "1 day, 19:50:00"
# - RETURN trips: task assignment explicitly states that
#   LAYOVER constraint (1h - 6h) MUST NOT be used between "there trip"
#   (arrival stop) and "back trip" (departure stop),
#   THEREFORE "there trip" arrival time MIGHT be AFTER "back trip" departure time
#   (traveller would MISS "back trip" departure in the real world)
#
# Implementation notes:
#
# - breath first search
# - in-memory
#
import argparse
import collections
import csv
import datetime
import json
import os
from typing import Dict
from typing import List
from typing import Optional


class FlightQuery:
    def __init__(
        self,
        origin: str = "",
        destination: str = "",
        bags_count: int = 0,
        return_ticket: bool = False,
        min_layover_hours: int = 1,
        max_layover_hours: int = 6,
        max_stops: int = 0,
        max_price: float = 0.0,
    ):
        self.origin = origin
        self.destination = destination
        self.bags_count = bags_count
        self.return_ticket = return_ticket
        # constraints
        self.min_layover_hours = min_layover_hours
        self.max_layover_hours = max_layover_hours
        # extra
        self.max_stops = max_stops
        self.max_price = max_price

    def __str__(self) -> str:
        return (
            f"Query:\n"
            f"  origin     : {self.origin}\n"
            f"  destination: {self.destination}\n"
            f"  bags count : {self.bags_count}\n"
            f"  return     : {self.return_ticket}\n"
            f"  ------------\n"
            f"  max stops  : {self.max_stops}\n"
            f"  max price  : {self.max_price}\n"
        )

    def init(self, cli_args: Optional[argparse.Namespace] = None) -> "FlightQuery":
        if cli_args:
            self.origin = cli_args.origin
            self.destination = cli_args.destination
            self.bags_count = cli_args.bags
            self.return_ticket = getattr(cli_args, "return")
        return self

    def validate(self):
        if not self.origin:
            raise ValueError("Origin airport must be specified - it is empty.")
        if not self.destination:
            raise ValueError("Destination airport must be specified - it is empty.")
        if self.origin == self.destination:
            raise ValueError(
                f"Origin airport {self.origin} must be different from destination "
                f"airport"
            )
        if self.bags_count < 0:
            raise ValueError(
                f"Number of bags must be positive number: {self.bags_count}"
            )
        if self.max_stops < 0:
            raise ValueError(
                f"Maximum number of stops must be positive number: {self.max_stops}"
            )
        if self.max_price < 0.0:
            raise ValueError(f"Maximum price must be positive number: {self.max_price}")
        if self.min_layover_hours < 0:
            raise ValueError(
                f"Minimum layover time must be positive number: "
                f"{self.min_layover_hours}"
            )
        if self.max_layover_hours < 0:
            raise ValueError(
                f"Maximum layover time must be positive number: "
                f"{self.max_layover_hours}"
            )
        if self.min_layover_hours > self.max_layover_hours:
            raise ValueError(
                f"Minimum layover ({self.min_layover_hours}h) must be smaller than "
                f"maximum layover ({self.max_layover_hours}h)"
            )


class FlightDataset:
    """Flight dataset loading, preprocessing and in-memory representation."""

    COL_FLIGHT = "flight_no"
    COL_ORIGIN = "origin"
    COL_DESTINATION = "destination"
    COL_DEPARTURE = "departure"
    COL_ARRIVAL = "arrival"
    COL_DEPARTURE_O = "departure_obj"
    COL_ARRIVAL_O = "arrival_obj"
    COL_FLIGHT_S = "flight_seconds"
    COL_BASE_PRICE = "base_price"
    COL_BAG_PRICE = "bag_price"
    COL_BAGS_ALLOWED = "bags_allowed"

    FORMAT_DATETIME = "%Y-%m-%dT%H:%M:%S"

    def __init__(
        self,
        dataset_path: str,
    ):
        """Create flight dataset instance.

        Parameters
        ----------
        dataset_path : str
          Filesystem (relative or absolute) path to CSV file with dataset.

        """
        self._dataset_path = dataset_path
        self.srcs: set = set()
        self.dsts: set = set()
        self.dg_edges_by_src: collections.defaultdict[
            str, List
        ] = collections.defaultdict(list)
        self.dg_edges_by_dst: collections.defaultdict[
            str, List
        ] = collections.defaultdict(list)

    def add_row(self, row: dict) -> None:
        src: str = row[FlightDataset.COL_ORIGIN]
        dst: str = row[FlightDataset.COL_DESTINATION]
        row[FlightDataset.COL_DEPARTURE_O] = datetime.datetime.strptime(
            row[FlightDataset.COL_DEPARTURE], FlightDataset.FORMAT_DATETIME
        )
        row[FlightDataset.COL_ARRIVAL_O] = datetime.datetime.strptime(
            row[FlightDataset.COL_ARRIVAL], FlightDataset.FORMAT_DATETIME
        )
        row[FlightDataset.COL_FLIGHT_S] = (
            row[FlightDataset.COL_ARRIVAL_O] - row[FlightDataset.COL_DEPARTURE_O]
        ).total_seconds()
        row[FlightDataset.COL_BASE_PRICE] = float(row[FlightDataset.COL_BASE_PRICE])
        row[FlightDataset.COL_BAG_PRICE] = float(row[FlightDataset.COL_BAG_PRICE])
        row[FlightDataset.COL_BAGS_ALLOWED] = int(row[FlightDataset.COL_BAGS_ALLOWED])
        self.srcs.add(src)
        self.dg_edges_by_src[src].append(row)
        self.dsts.add(dst)
        self.dg_edges_by_dst[dst].append(row)

    def load(self) -> "FlightDataset":
        if not os.path.isfile(self._dataset_path):
            raise FileNotFoundError(
                f"Invalid input dataset path: '{self._dataset_path}'"
            )

        with open(self._dataset_path, mode="r") as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                self.add_row(row)

        return self

    def validate(self, query: FlightQuery) -> "FlightDataset":
        if query.origin not in self.srcs:
            raise ValueError(f"Origin airport '{query.origin}' is invalid (unknown)")
        if query.destination not in self.dsts:
            raise ValueError(
                f"Destination airport '{query.destination}' is invalid (unknown)"
            )

        return self


class Trip:
    def __init__(self, origin: str, destination: str, bags_count: int):
        self.flights: List[Dict] = []
        self.origin: str = origin
        self.destination: str = destination
        self.bags_allowed: int = 42  # min of bags allowed @ all flights
        self.bags_count: int = bags_count
        self.total_price: float = 0.0
        self.travel_time: str = ""

        self.stops: List[str] = [origin]
        self.travel_secs: int = 0

    def __str__(self) -> str:
        return (
            f"Trip from {self.origin} to {self.destination}:\n"
            f"  stops       : {self.stops}\n"
            f"  flights     : {[f[FlightDataset.COL_FLIGHT] for f in self.flights]}\n"
            f"  bags count  : {self.bags_count}\n"
            f"  bags allowed: {self.bags_allowed}\n"
            f"  total price : {self.total_price}\n"
            f"  travel time : {self.travel_time}\n"
            f"  travel secs : {self.travel_secs}\n"
        )

    def add_stop(self, flight: Dict):
        self.stops.append(flight[FlightDataset.COL_DESTINATION])
        self.total_price += flight[FlightDataset.COL_BASE_PRICE]
        self.total_price += float(self.bags_count) * flight[FlightDataset.COL_BAG_PRICE]
        # travel time: flight + wait time
        self.travel_secs += flight[FlightDataset.COL_FLIGHT_S]
        if self.flights:
            self.travel_secs += (
                flight[FlightDataset.COL_DEPARTURE_O]
                - self.flights[-1][FlightDataset.COL_ARRIVAL_O]
            ).total_seconds()

        self.flights.append(flight)
        self.bags_allowed = min(
            self.bags_allowed, flight[FlightDataset.COL_BAGS_ALLOWED]
        )

    def copy(self) -> "Trip":
        t: Trip = Trip(
            origin=self.origin, destination=self.destination, bags_count=self.bags_count
        )
        t.flights = self.flights.copy()
        t.bags_allowed = self.bags_allowed
        t.total_price = self.total_price
        t.travel_time = self.travel_time
        t.stops = self.stops.copy()
        t.travel_secs = self.travel_secs
        return t

    def finalize(self):
        # WITH padding: "travel_time": "06:55:00"
        # self.travel_time = time.strftime("%H:%M:%S", time.gmtime(self.travel_secs))
        # WITHOUT padding: "travel_time": "6:55:00"
        self.travel_time = f"{datetime.timedelta(seconds=self.travel_secs)}"

    @staticmethod
    def flight_to_dict(flight: Dict):
        result = {}
        for c in [
            FlightDataset.COL_FLIGHT,
            FlightDataset.COL_ORIGIN,
            FlightDataset.COL_DESTINATION,
            FlightDataset.COL_DEPARTURE,
            FlightDataset.COL_ARRIVAL,
            FlightDataset.COL_BASE_PRICE,
            FlightDataset.COL_BAG_PRICE,
            FlightDataset.COL_BAGS_ALLOWED,
        ]:
            result[c] = flight[c]
        return result

    def to_dict(self):
        return {
            "flights": [Trip.flight_to_dict(f) for f in self.flights],
            "bags_allowed": self.bags_allowed,
            "bags_count": self.bags_count,
            "destination": self.destination,
            "origin": self.origin,
            "total_price": self.total_price,
            "travel_time": self.travel_time,
        }


class FlightSearchResult:
    def __init__(self):
        self.trips: List[Trip] = []

    def __str__(self) -> str:
        result: List[str] = [f"Search result ({len(self.trips)}):"]
        for t in self.trips:
            result.append(f"  {str(t)}")
        return "\n".join(result)

    def add_trip(self, trip: Trip) -> None:
        trip.finalize()
        self.trips.append(trip)

    def add_back_result(self, back: "FlightSearchResult"):
        if self.trips:
            if not back.trips:
                # no valid back trips
                self.trips.clear()
                return

            # cartesian product 8-/
            new_trips: List[Trip] = []
            for there_trip in self.trips:
                for back_trip in back.trips:
                    new_trip = there_trip.copy()

                    new_trip.flights.extend(back_trip.flights)
                    new_trip.bags_allowed = min(
                        there_trip.bags_allowed, back_trip.bags_allowed
                    )
                    new_trip.total_price += back_trip.total_price

                    new_trip.travel_time = (
                        there_trip.travel_secs + back_trip.travel_secs
                    )
                    new_trip.finalize()

                    new_trips.append(new_trip)

            self.trips = new_trips

    def sort(self):
        self.trips.sort(key=lambda t: t.total_price)

    def to_dict(self) -> List:
        return [t.to_dict() for t in self.trips]

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=4)


class FlightOracle:
    """Flight search engine."""

    def __init__(self, dataset: FlightDataset):
        self.dataset: FlightDataset = dataset

    @staticmethod
    def _is_flight_admissible(
        flight,
        trip: Trip,
        min_layover_hours: int,
        max_layover_hours: int,
        max_price: float,
        max_stops: int,
    ):
        if flight[FlightDataset.COL_DESTINATION] in trip.stops:
            return False
        if trip.bags_count > flight[FlightDataset.COL_BAGS_ALLOWED]:
            return False
        # layover
        if trip.flights:
            if not (
                trip.flights[-1][FlightDataset.COL_ARRIVAL_O]
                < flight[FlightDataset.COL_DEPARTURE_O]
            ):
                return False
            layover = (
                flight[FlightDataset.COL_DEPARTURE_O]
                - trip.flights[-1][FlightDataset.COL_ARRIVAL_O]
            ).total_seconds()
            if not (min_layover_hours * 3600 <= layover <= max_layover_hours * 3600):
                return False
        # extra
        if max_price and max_price < (
            trip.total_price
            + flight[FlightDataset.COL_BASE_PRICE]
            + float(trip.bags_count) * flight[FlightDataset.COL_BAG_PRICE]
        ):
            return False
        # max stops
        if max_stops and max_stops < len(trip.stops) - 1:
            return False

        return True

    def _find_one_way_flights(self, query: FlightQuery) -> FlightSearchResult:
        result = FlightSearchResult()
        trips = collections.deque()
        trips.append(
            Trip(
                origin=query.origin,
                destination=query.destination,
                bags_count=query.bags_count,
            )
        )
        while trips:
            trip: Trip = trips.popleft()
            current_stop = trip.stops[-1]
            if query.destination == current_stop:
                result.add_trip(trip)

            # schedule next stops from the current stop
            for flight in self.dataset.dg_edges_by_src.get(current_stop, []):
                if FlightOracle._is_flight_admissible(
                    flight=flight,
                    trip=trip,
                    min_layover_hours=query.min_layover_hours,
                    max_layover_hours=query.max_layover_hours,
                    max_price=query.max_price,
                    max_stops=query.max_stops,
                ):
                    new_trip: Trip = trip.copy()
                    new_trip.add_stop(flight)
                    trips.append(new_trip)

        return result

    def find_flights(self, query: FlightQuery) -> FlightSearchResult:
        there: FlightSearchResult = self._find_one_way_flights(query)
        if query.return_ticket and there.trips:
            # IMPORTANT: no layover + "there" arrival might be AFTER "back" departure
            back: FlightSearchResult = self._find_one_way_flights(query)
            there.add_back_result(back)

        there.sort()
        return there


def main() -> FlightSearchResult:
    parser = argparse.ArgumentParser(
        description="Flights finder (Kiwi.com Python weekend entry task)."
    )
    parser.add_argument(
        "dataset_path",
        metavar="dataset_path",
        type=str,
        help="path to CSV file with flights",
    )
    parser.add_argument("origin", metavar="origin", type=str, help="flight trip origin")
    parser.add_argument(
        "destination", metavar="destination", type=str, help="flight trip destination"
    )
    parser.add_argument(
        "--bags",
        type=int,
        default=0,
        help="optional number of bags (default: 0)",
    )
    parser.add_argument(
        "--return",
        action="store_false",
        default=False,
        help="optional one way vs. return trip (default: one way)",
    )
    parser.add_argument(
        "--max_stops",
        type=int,
        default=0,
        help="optional maximum number of stops (one way)",
    )
    parser.add_argument(
        "--max_price",
        type=int,
        default=0,
        help="optional maximum flight trip price",
    )
    args = parser.parse_args()

    query = FlightQuery().init(args)
    query.validate()

    dataset = FlightDataset(args.dataset_path).load()
    dataset.validate(query)

    flight_oracle = FlightOracle(dataset)
    result: FlightSearchResult = flight_oracle.find_flights(query)
    print(result.to_json())
    return result


if __name__ == "__main__":
    print(main().to_json())
