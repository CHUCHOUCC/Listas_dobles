"""
Domain model of the flipbook animator.

    Animation --(DoublyLinkedList)--> Frame --(SinglyLinkedList)--> Stroke --(SinglyLinkedList)--> Point

Frames use a doubly linked list because the user moves forward AND backward
through them, plays the animation in reverse, sees the previous and next frame
at the same time (onion skin) and inserts, deletes or reorders frames in the
middle. Strokes and points only grow at the end and are read from start to end,
so a singly linked list is enough for them.
"""

from linked_lists import DoublyLinkedList, SinglyLinkedList


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Stroke:
    """A continuous brush line drawn with one color and one width."""

    def __init__(self, color, width):
        self.color = color
        self.width = width
        self.points = SinglyLinkedList()

    def add_point(self, x, y):
        self.points.append(Point(x, y))

    def copy(self):
        clone = Stroke(self.color, self.width)
        current = self.points.head
        while current is not None:
            clone.add_point(current.value.x, current.value.y)
            current = current.next
        return clone


class Frame:
    """One drawing of the animation: a sequence of strokes."""

    def __init__(self):
        self.strokes = SinglyLinkedList()

    def add_stroke(self, stroke):
        self.strokes.append(stroke)

    def undo(self):
        return self.strokes.remove_last()

    def clear(self):
        self.strokes.clear()

    def copy(self):
        clone = Frame()
        current = self.strokes.head
        while current is not None:
            clone.add_stroke(current.value.copy())
            current = current.next
        return clone


class Animation:
    """A flipbook: frames stored in a doubly linked list.

    `current` is a reference to the node being edited/shown (the playhead),
    so moving to the next or previous frame is just following a pointer.
    """

    def __init__(self):
        self.frames = DoublyLinkedList()
        self.current = self.frames.append(Frame())

    # --- queries ---------------------------------------------------------

    def current_frame(self):
        return self.current.value

    def frame_count(self):
        return self.frames.size

    def current_index(self):
        return self.frames.index_of(self.current)

    # --- editing ---------------------------------------------------------

    def add_frame(self):
        """Inserts a blank frame right after the current one."""
        self.current = self.frames.insert_after(self.current, Frame())

    def duplicate_frame(self):
        """Inserts a deep copy of the current frame right after it."""
        self.current = self.frames.insert_after(self.current, self.current.value.copy())

    def delete_frame(self):
        """Deletes the current frame. The animation always keeps at least one."""
        if self.frames.size == 1:
            self.current.value.clear()
            return
        self.current = self.frames.remove(self.current)

    def move_frame_forward(self):
        return self.frames.swap_with_next(self.current)

    def move_frame_backward(self):
        if self.current.prev is None:
            return False
        return self.frames.swap_with_next(self.current.prev)

    def undo_stroke(self):
        self.current.value.undo()

    def clear_frame(self):
        self.current.value.clear()

    # --- navigation ------------------------------------------------------

    def go_next(self, loop=False):
        if self.current.next is not None:
            self.current = self.current.next
            return True
        if loop and self.frames.size > 1:
            self.current = self.frames.head
            return True
        return False

    def go_previous(self, loop=False):
        if self.current.prev is not None:
            self.current = self.current.prev
            return True
        if loop and self.frames.size > 1:
            self.current = self.frames.tail
            return True
        return False

    def go_first(self):
        self.current = self.frames.head

    def go_last(self):
        self.current = self.frames.tail

    def go_to(self, index):
        node = self.frames.get_at(index)
        if node is None:
            return False
        self.current = node
        return True
