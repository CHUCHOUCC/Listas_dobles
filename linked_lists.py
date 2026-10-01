"""
Low-level linked lists built from scratch.

No Python lists, tuples, dicts or built-in collection methods are used to
store data: every element lives inside a node connected by references, and
sizes are tracked with manual counters (no len()).
"""


# ---------------------------------------------------------------------------
# Singly linked list
# ---------------------------------------------------------------------------

class SingleNode:
    """Node of a singly linked list: a value and a reference to the next node."""

    def __init__(self, value):
        self.value = value
        self.next = None


class SinglyLinkedList:
    """Singly linked list with head/tail references and a manual size counter."""

    def __init__(self):
        self.head = None
        self.tail = None
        self.size = 0

    def is_empty(self):
        return self.head is None

    def append(self, value):
        """Adds a value at the end. O(1) thanks to the tail reference."""
        new_node = SingleNode(value)
        if self.head is None:
            self.head = new_node
            self.tail = new_node
        else:
            self.tail.next = new_node
            self.tail = new_node
        self.size += 1

    def remove_last(self):
        """Removes and returns the last value.

        O(n): a singly linked list has no 'prev' reference, so it must walk
        from the head to find the node that comes before the tail.
        """
        if self.head is None:
            return None
        removed_value = self.tail.value
        if self.head is self.tail:
            self.head = None
            self.tail = None
        else:
            current = self.head
            while current.next is not self.tail:
                current = current.next
            current.next = None
            self.tail = current
        self.size -= 1
        return removed_value

    def clear(self):
        self.head = None
        self.tail = None
        self.size = 0


# ---------------------------------------------------------------------------
# Doubly linked list
# ---------------------------------------------------------------------------

class DoubleNode:
    """Node of a doubly linked list: a value plus references to both neighbors."""

    def __init__(self, value):
        self.value = value
        self.prev = None
        self.next = None


class DoublyLinkedList:
    """Doubly linked list with head (cabeza), tail (cola) and a manual size counter."""

    def __init__(self):
        self.head = None
        self.tail = None
        self.size = 0

    def is_empty(self):
        return self.head is None

    def append(self, value):
        """Adds a value at the end and returns its node. O(1)."""
        new_node = DoubleNode(value)
        if self.head is None:
            self.head = new_node
            self.tail = new_node
        else:
            new_node.prev = self.tail
            self.tail.next = new_node
            self.tail = new_node
        self.size += 1
        return new_node

    def prepend(self, value):
        """Adds a value at the start and returns its node. O(1)."""
        new_node = DoubleNode(value)
        if self.head is None:
            self.head = new_node
            self.tail = new_node
        else:
            new_node.next = self.head
            self.head.prev = new_node
            self.head = new_node
        self.size += 1
        return new_node

    def insert_after(self, node, value):
        """Inserts a value right after a given node and returns the new node. O(1)."""
        if node is self.tail:
            return self.append(value)
        new_node = DoubleNode(value)
        follower = node.next
        new_node.prev = node
        new_node.next = follower
        node.next = new_node
        follower.prev = new_node
        self.size += 1
        return new_node

    def remove(self, node):
        """Unlinks a node in O(1): thanks to 'prev' no traversal is needed.

        Returns the neighbor that should take its place (next if it exists,
        otherwise prev), or None if the list became empty.
        """
        leader = node.prev
        follower = node.next
        if leader is None:
            self.head = follower
        else:
            leader.next = follower
        if follower is None:
            self.tail = leader
        else:
            follower.prev = leader
        node.prev = None
        node.next = None
        self.size -= 1
        if follower is not None:
            return follower
        return leader

    def swap_with_next(self, node):
        """Exchanges the positions of a node and its next node by relinking pointers.

        Before: leader <-> node <-> second <-> follower
        After:  leader <-> second <-> node <-> follower
        """
        second = node.next
        if second is None:
            return False
        leader = node.prev
        follower = second.next

        second.prev = leader
        second.next = node
        node.prev = second
        node.next = follower

        if leader is None:
            self.head = second
        else:
            leader.next = second
        if follower is None:
            self.tail = node
        else:
            follower.prev = node
        return True

    def get_at(self, index):
        """Returns the node at an index walking from the closest end.

        Indexes in the first half are reached forward from the head; indexes
        in the second half are reached backward from the tail.
        """
        if index < 0 or index >= self.size:
            return None
        if index < self.size // 2:
            current = self.head
            i = 0
            while i < index:
                current = current.next
                i += 1
        else:
            current = self.tail
            i = self.size - 1
            while i > index:
                current = current.prev
                i -= 1
        return current

    def index_of(self, node):
        """Returns the position of a node, or -1 if it is not in the list. O(n)."""
        current = self.head
        i = 0
        while current is not None:
            if current is node:
                return i
            current = current.next
            i += 1
        return -1
