# RP-growth
Implementation of RP-growth in Python from the paper "Discovering Recurring Patterns in Time Series"

## Example
1. Create a Transaction Database from your data. Transaction databases have the following format:
`tdb = {
    1: ["a", "b", "g"],
    2: ["a", "c", "d"],
    3: ["a", "b", "e", "f"],
    4: ["a", "b", "c", "d"],
    5: ["c", "d", "e", "f", "g"],
    6: ["e", "f", "g"],
    7: ["a", "b", "c", "g"],
    9: ["c", "d"],
    10: ["c", "d", "e", "f"],
    11: ["a", "b", "e", "f"],
    12: ["a", "b", "c", "d", "e", "f", "g"],
    14: ["a", "b", "g"],
}`

- Each row represents a transaction which has a timestamps and events/items that occurred in this transaction
- Transactions need to be equally spaced, e.g., every month/day/hour
- Empty transactions are skipped
- Items/Events need to be hashable

2. Create an instance of the PatternFinder class
`pattern_finder = PatternFinder(tdb, per, min_ps, min_rec)`
- tdb: the transaction database
- per (period): maximum distance between two consecutive occurrences of an item to be counted periodic
- minPS (minimum support): minimum number of items in a given recurrence
- minRec (minimum recurrence): minimum number of recurrences

3. Get the patterns
`patterns = pattern_finder.find_recurring_patterns()`

## References
This repository is based on the following paper:
Kiran, R., Shang, H., Toyoda, M., & Kitsuregawa, M. (2015). Discovering Recurring Patterns in
Time Series. 18th International Conference on Extending Database Technology.
ISBN:978-3-89318-067-7

Link: https://openproceedings.org/2015/conf/edbt/paper-23.pdf
