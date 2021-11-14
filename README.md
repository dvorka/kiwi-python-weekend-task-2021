# Solution of kiwi.com Python weekend entry task
This is solution of [kiwi.com Python weekend entry task](https://github.com/kiwicom/python-weekend-xmas-task):

* `solution.py`
    - [solution](#solution) of the task [implemented](#implementation) in **Python 3**

Development resources:

* `tests/`
    - directory with solution tests
* `datasets/`
    - directory with CSV datasets used by tests
* `Makefile`
    - used in solution development - check `make help`
# Solution
Requirements:

* **Python 3**

Run solution:

```
$ python3 -m solution -h
usage: solution.py [-h] [--bags BAGS] [--return] [--max_stops MAX_STOPS] [--max_price MAX_PRICE] dataset_path origin destination

Flights finder (Kiwi.com Python weekend entry task).

positional arguments:
  dataset_path          path to CSV file with flights
  origin                flight trip origin
  destination           flight trip destination

optional arguments:
  -h, --help            show this help message and exit
  --bags BAGS           optional number of bags (default: 0)
  --return              optional one way vs. return trip (default: one way)
  --max_stops MAX_STOPS
                        optional maximum number of stops (one way)
  --max_price MAX_PRICE
                        optional maximum flight trip price
```

Examples:

* `python -m solution datasets/example0.csv RFZ WIW --bags=1 --return`
* `python -m solution datasets/example3.csv VVH ZRW --bags=2 --max_stops 2`
* `python -m solution datasets/example3.csv WUE NNB --bags=1 --max_price 75`
* `python -m solution -h`
# Implementation
**Important** task assignment and implementation related notes:

- **return trips**: 
    - task assignment explicitly states that **layover** constraint (1h - 6h) **must not** be 
      used between "there trip" (arrival stop) and "back trip" (departure stop)
    - therefore "there trip" arrival time might be **AFTER** "back trip" departure time
      i.e. **traveller would miss** "back trip" departure
    - **please** set option below in `solution.py` to `True` to enable 
      `"there trip" arrival time` < `"back trip" departure time` constraint (ordering
      of there and back trips does not have to be ordered by default):
        - `solution.py::OPT_TIME_ORDERED_RETURN_TRIP = True`
- **result serialization**
   - `travel_time` **longer** than 1 day is serialized using Python's `timedelta` format,
   for instance:
        - `"1 day, 19:50:00"`

 **Implementation** notes:

- breath first search
    - flights are searched using BFS algorithm
- in-memory
    - implementation is in-memory only - it won't be scale/handle big(ger) datasets
# Contact
* Martin Dvorak [martin.dvorak@mindforger.com](martin.dvorak@mindforger.com)
