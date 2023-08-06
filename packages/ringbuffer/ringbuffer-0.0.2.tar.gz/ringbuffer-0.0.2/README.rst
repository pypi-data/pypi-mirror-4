=========
 Summary
=========

General implementation of an associative ring buffer.
Random access time is like with any other dictionary - O(1),
memory consumption is also similar.

=======
 Usage
=======

.. code-block:: python

		>>> r = Ring({}, 5)
		>>> r[0] = "A"
		>>> r[1] = "B"
		>>> r[2] = "C"
		>>> r[3] = "D"
		>>> r[4] = "E"
		>>> r
		Ring([(0, 'A'), (1, 'B'), (2, 'C'), (3, 'D'), (4, 'E')])
		>>> r[5] = "F"
		>>> r
		Ring([(1, 'B'), (2, 'C'), (3, 'D'), (4, 'E'), (5, 'F')])
		>>> 
