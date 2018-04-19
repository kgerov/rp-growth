import math

from tree import RPTree


class PatternFinder():
    def __init__(self, tdb, per, min_ps, min_rec):
        self._tdb = tdb
        self._per = per
        self._min_ps = min_ps
        self._min_rec = min_rec

    def find_recurring_patterns(self):
        # Algorithm 1: RP-List - reduce the number of possible patterns
        rp_list = {}

        for timestamp, items in self.tdb.items():
            for item in items:
                if item not in rp_list:
                    # First time we see this item
                    rp_list[item] = Item(item, 1, 0, 1)
                else:
                    if timestamp - rp_list[item].last_timestamp <= self.per:
                        # the recurrence is continuing
                        rp_list[item].support += 1
                        rp_list[item].periodic_support += 1
                    else:
                        # recurrence is over, update values
                        rp_list[item].max_recurrence += math.floor(
                            float(rp_list[item].periodic_support) / self.min_ps
                        )
                        rp_list[item].support += 1
                        rp_list[item].periodic_support = 1

                # update last timestamps of item
                rp_list[item].last_timestamp = timestamp

        final_rp_list = {}  # RP-list with all final items

        for item in rp_list.keys():
            # add all recurrences that were still continuing before the last
            # timestamp in the transactional database
            if rp_list[item].periodic_support > 1:
                rp_list[item].max_recurrence += math.floor(
                    float(rp_list[item].periodic_support) / self.min_ps
                )

                rp_list[item].periodic_support = 1

            if rp_list[item].max_recurrence >= self.min_rec:
                # only add items that have max recurrences above our min
                # this estimate reduces the number of items we need to go over
                final_rp_list[item] = rp_list[item]

        # sort final list by support; NOTE: here I also sort by item
        # name as 2nd criteria to match the example in the paper
        final_rp_list = sorted(
            final_rp_list, key=lambda x: (-1*final_rp_list[x].support, x)
        )

        # Algorithm 2 from the paper: build RP-Tree
        tree = RPTree(final_rp_list)

        for timestamp, items in self.tdb.items():
            sorted_items = []

            # sort items (in order of RP-List) before adding them to tree
            for item in final_rp_list:
                if item in items:
                    sorted_items.append(item)

            # Algorithm 3: insert node into rp-tree
            tree.insert_node(sorted_items, timestamp)

        # Algorithm 4 and 5: Mine patterns from tree
        patterns = []

        for pattern in self._rp_growth(tree, []):
            patterns.append(pattern)

        return patterns

    def _rp_growth(self, tree, pattern):
        """
        RP-Growth - Algorithm 4 from the paper
        """
        for node in tree.items_ordered():
            curr_item = node[0]
            # get prefix tree and temporary timestamps array which maps
            # items to all the timestamps in which they occur
            timestamps, prefix_tree = tree.prefix_tree(curr_item)

            if self._get_recurrence(curr_item,
               sorted(timestamps[curr_item])) and curr_item not in pattern:

                new_pattern = pattern + [curr_item]  # generate new pattern
                del timestamps[curr_item]  # remove item from temp array

                yield new_pattern  # return pattern

                # construct conditional tree
                conditional_tree = self._construct_conditional_from_prefix(
                    prefix_tree, timestamps
                )

                # if tree is non-empty, recurse
                if conditional_tree.node_count > 0:
                    for pset in self._rp_growth(conditional_tree, new_pattern):
                        yield pset

            # remove item from tree and push item's timestamps up
            tree.remove_nodes(curr_item)

    def _get_recurrence(self, pattern, timestamps):
        """
        Algorithm 5: Get Recurrence

        Returns the number of recurrences for the timestamps of a given pattern
        """
        last_occurence = None
        sub_db = []
        start_ts = None
        current_ps = 1

        for timestamp in timestamps:
            if last_occurence is None:
                current_ps = 1
                start_ts = timestamp
            else:
                if timestamp - last_occurence <= self.per:
                    current_ps += 1
                else:
                    if current_ps >= self.min_ps:
                        sub_db.append((start_ts, last_occurence))

                    current_ps = 1
                    start_ts = timestamp

            last_occurence = timestamp

        if current_ps >= self.min_ps:
            sub_db.append((start_ts, last_occurence))

        return len(sub_db) >= self.min_rec

    def _construct_conditional_from_prefix(self, prefix_tree, timestamps):
        """
        Construct and return a conditional tree from a prefix tree
        """
        # we don't need a deep copy because we are not using
        # the prefix tree anymore
        conditional_tree = prefix_tree

        for node in conditional_tree.items_ordered():
            if not self._get_recurrence(node[0], sorted(timestamps[node[0]])):
                # remove nodes with that don't satisfy the min_rec parameter
                conditional_tree.remove_nodes(node[0])

        return conditional_tree

    @property
    def tdb(self):
        """
        The transactional database
        """
        return self._tdb

    @property
    def per(self):
        """
        The user-defined per
        """
        return self._per

    @property
    def min_ps(self):
        """
        The user-defined minimum periodic support
        """
        return self._min_ps

    @property
    def min_rec(self):
        """
        The user-defined minimum recurrence
        """
        return self._min_rec


class Item():
    """
    Item in a transactional database.
    """

    def __init__(self, item, support, max_recurrence, periodic_support):
        self.item = item
        self.support = support  # number of txns in TDB that contain this item
        self.max_recurrence = max_recurrence
        self.periodic_support = periodic_support
        self.last_timestamp = None
