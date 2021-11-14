AS BRIEF AS POSSIBLE

Generated TOC

Requirements:
Python 3

python3 ...


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



make help

User Doc
Task implementation remarks
Developer doc

examples
make example (check Makefile)
python solution -h

Solution remarks:

- return ticket: arrival CAN be BEFORE departure of the return trip as
  task description states "..."
- bags allowed: minimum of bags of all flights

Additional remarks

- if you want to run test then then copy datasets from the task GH repository (intentionally skipped) 
