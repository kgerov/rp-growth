import time

from rp_growth import PatternFinder


def run_paper_example():
    # Initialize TBD from the paper
    tdb = {
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
    }

    # Paramter settings
    per = 2
    min_ps = 3  # minimum length of a periodic-interval
    min_rec = 2

    start_time = time.time()

    pattern_finder = PatternFinder(tdb, per, min_ps, min_rec)
    patterns = pattern_finder.find_recurring_patterns()

    print("--- %s seconds ---" % (time.time() - start_time))

    for pattern in patterns:
        print(pattern)

    print(len(patterns))


def run_t10_example():
    # Generate TBD from T10I4D100K
    tdb = {}

    with open('T10I4D100K.dat', 'r') as f:
        d = f.readlines()
        counter = 1

        for i in d:
            k = i.rstrip().split(" ")
            tdb[counter] = k
            counter += 1

    # Paramter settings
    per = 720
    min_ps = (counter-1) * 0.003  # minimum length of a periodic-interval
    min_rec = 2

    start_time = time.time()

    pattern_finder = PatternFinder(tdb, per, min_ps, min_rec)
    patterns = pattern_finder.find_recurring_patterns()

    print("--- %s seconds ---" % (time.time() - start_time))
    print(len(patterns))


run_t10_example()
