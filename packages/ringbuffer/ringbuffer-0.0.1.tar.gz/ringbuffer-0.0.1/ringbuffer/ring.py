from collections import OrderedDict

class Ring(OrderedDict):
    """
    O(1) random access  ring buffer.
    Kind of like fixed size deque, but associative.
    """

    def __init__(self, sequence={}, pieces=20, *args, **kwargs):
        """
        @param sequence: sequence that will be passed to dict constructor.
        @param pieces: how much pieces will the buffer have.
        """
        self.pieces = max(pieces, 1)
        if len(sequence) > self.pieces:
            raise BufferError("Sequence is too long, increase pieces.")
        OrderedDict.__init__(self, sequence, *args, **kwargs)

    def __setitem__(self, key, item):
        """
        @param key: unique index of the piece(or overwrite something).
        @param item: item corresponding to the key.
        """
        OrderedDict.__setitem__(self, key, item)
        if len(self) > self.pieces:
            self.popitem(False)
