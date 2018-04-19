from collections import namedtuple


class RPTree(object):
    """
    An RP-tree as specified in "Discovering Recurring Patterns in Time Series"
    paper.

    The tree is used to store transactions without any loss of information
    regarding the recurring patterns which can later be extracted. All items
    stored need to be hashable.
    """

    # Routes adopted from enaeseth's GitHub library for FP-Growth
    Route = namedtuple('Route', 'head tail')

    def __init__(self, rp_list):
        # Set the root item as None
        self._root = RPNode(self, None)
        # RP-list from Algorithm 1 in the paper used for the order of the items
        self._rp_list = rp_list

        # A dictionary mapping items to the head and tail of a path of
        # "neighbors" that will hit every node containing that item.
        self._routes = {}

    def insert_node(self, items, timestamp):
        """
        Insert transaction (its items and timtestamp) into the tree.
        (Algorithm 3 from the paper)
        """
        current_node = self.root

        for item in items:
            next_node = current_node.get_child(item)

            if next_node is None:
                next_node = RPNode(self, item)
                current_node.add(next_node)

                # Add node to route that contain this item
                self._update_route(next_node)

            current_node = next_node

        current_node.add_timestamp(timestamp)

    def items(self):
        """
        Returns all unique items in the tree in the format of a tuple which
        holds the item and the generator for all of its neighbors.
        """
        for item in self._routes.keys():
            yield (item, self.nodes(item))

    def items_ordered(self):
        """
        Returns all unique items in the tree in the format of a tuple which
        holds the item and the generator for all of its neighbors. The items
        are orderd based on the RP-list (sorted by support in descending order)
        """
        for item in reversed(self._rp_list):
            if item in self._routes.keys():
                yield (item, self.nodes(item))

    def nodes(self, item):
        """
        Returns a generator with all nodes that contain the given item.
        """
        if item not in self._routes:
            raise KeyError("Item is not in tree")

        node = self._routes[item][0]

        while node:
            yield node
            node = node.neighbor

    def prefix_tree(self, item):
        """
        Generate the prefix tree for a given item.

        Return a tuple holding the temporary dictionary mapping items to all
        of their transactions and the prefix tree.
        """
        def walk_path(node, temp_transactions, prefix_tree):
            current_ts = node.timestamps
            path = []

            while node and not node.root:
                path.append(node)

                if node.item in temp_transactions:
                    temp_transactions[node.item] += current_ts
                else:
                    temp_transactions[node.item] = current_ts

                node = node.parent

            root = prefix_tree.root

            for curr_node in reversed(path[1:]):
                new_node = root.get_child(curr_node.item)

                if new_node is None:
                    new_node = RPNode(prefix_tree, curr_node.item)
                    root.add(new_node)
                    prefix_tree._update_route(new_node)

                root = new_node

            root.add_timestamps(path[0].timestamps)

        prefix_tree = RPTree(self._rp_list)
        temp_transactions = {}

        for node in self.nodes(item):
            walk_path(node, temp_transactions, prefix_tree)

        return temp_transactions, prefix_tree

    def remove_nodes(self, item):
        """
        Remove all nodes that hold a given item
        """

        # go over all nodes with this value
        for node in self.nodes(item):
            parent = node.parent

            # move node's timestamps up the tree
            if not parent.root:
                node.parent.add_timestamps(node.timestamps)

            parent.remove(node)

        # remove node from routes
        if item in self._routes:
            del self._routes[item]

    @property
    def root(self):
        """
        The root node of the tree.
        """
        return self._root

    @property
    def node_count(self):
        """
        Number of nodes in the tree including the root.
        """
        return len(self._routes.keys())

    def _update_route(self, point):
        """
        Add the given node to the route through all nodes for its item.

        Routes adopted from enaeseth's GitHub library for FP-Growth
        """
        assert self is point.tree

        try:
            route = self._routes[point.item]
            route[1].neighbor = point  # route[1] is the tail
            self._routes[point.item] = self.Route(route[0], point)
        except KeyError:
            # First node for this item; start a new route.
            self._routes[point.item] = self.Route(point, point)


class RPNode(object):
    """
    A node in an RP-tree.
    """

    def __init__(self, tree, item):
        self._tree = tree
        self._item = item
        self._parent = None
        self._children = {}
        self._neighbor = None
        self._timestamps = []

    def add(self, child):
        """
        Add the given RPNode child
        """

        # check if the node is an instance of RPNode
        if not isinstance(child, RPNode):
            raise TypeError("Can only add other RPNodes as children")

        if child.item not in self._children:
            # add node to dictionary and assign its parent
            self._children[child.item] = child
            child.parent = self
        else:
            # if the child is already in the list, only add its timestamps
            new_ts = set(child._timestamps) - set(self._timestamps)
            self._children[child.item].add_timestamps(new_ts)

    def remove(self, child):
        """
        Remove the given RPNode child
        """
        if not isinstance(child, RPNode):
            raise TypeError("Can only add other RPNodes as children")

        if child.item not in self._children:
            raise Exception("Item is not a child of given element")

        if not child.is_leaf:
            parent = self._children[child.item].parent

            for grandchild in child.children:
                parent.add(grandchild)

        self._children[child.item].parent = None
        del self._children[child.item]

    def get_child(self, item):
        """
        Check whether this node contains a child node for the given item.
        If so, that node is returned; otherwise, `None` is returned.
        """
        try:
            return self._children[item]
        except KeyError:
            return None

    def add_timestamp(self, timestamp):
        self._timestamps.append(timestamp)

    def add_timestamps(self, timestamps):
        self._timestamps += timestamps

    def __contains__(self, item):
        return item in self._children

    @property
    def tree(self):
        """
        The node's tree.
        """
        return self._tree

    @property
    def item(self):
        """
        Return the item contained in this node.
        """
        return self._item

    @property
    def root(self):
        """
        Return Bool depending if the node is the root or not.
        """
        return self._item is None

    @property
    def is_leaf(self):
        """
        Return Bool depending if the node is a leaf or not.
        """
        return len(self._children) == 0

    @property
    def parent(self):
        """
        Return the node's parent.
        """
        return self._parent

    @parent.setter
    def parent(self, value):
        if value:
            if not isinstance(value, RPNode):
                raise TypeError("A node must have an RPNode as a parent.")

            if value.tree is not self.tree:
                raise ValueError("Parent and child must be from the same tree")

        self._parent = value

    @property
    def neighbor(self):
        """
        The node's neighbor; the one with the same value that is "to the right"
        of it in the tree.
        """
        return self._neighbor

    @neighbor.setter
    def neighbor(self, value):
        if value:
            if not isinstance(value, RPNode):
                raise TypeError("A node must have an RPNode as a neighbor.")

            if value.tree is not self.tree:
                raise ValueError("Cannot have a neighbor from another tree.")

        self._neighbor = value

    @property
    def children(self):
        """
        The nodes that are children of this node.
        """
        return tuple(self._children.values())

    @property
    def timestamps(self):
        """
        Timestamps associated with this node.
        """
        return tuple(self._timestamps)

    def __str__(self):
        return repr(self)

    def __repr__(self):
        if self.root:
            return "<%s (root)>" % type(self).__name__

        return "<%s %r [%r]>" % (
            type(self).__name__, self.item, self.timestamps
        )
