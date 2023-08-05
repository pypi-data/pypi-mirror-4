
# Created on 2012.04.28
#
# @author: german

import collections # High-performance container datatypes

class Queue:
	"""FIFO"""
	
	def __init__(self):
		self._queue = collections.deque()
	
	def pull(self):
		"""Remove and return the first element of the queue"""

		try:
			# Remove and return an element from the left side of the deque
			element = self._queue.popleft()
		except IndexError:
			raise Exception('no elements are present')
		return element
		
	def put(self, element):
		"""Appends the element as the last object of the queue"""
		self._queue.append(element) # Add x to the right side of the deque
	
	def is_empty(self):
		return len(self._queue) == 0
	
	def count(self):
		return len(self._queue)
	
	def clear(self):
		"""Remove all elements of the queue"""
		self._queue.clear()
	
	def convert_to_list(self):
		"""Return the elements in an ordered list"""
		return list(self._queue)

	def __str__(self):
		line = ''
		data_list = self.convert_to_list()
		for item in data_list:
			line += '%s\n' % str(item)
		return line

# class Stack(Queue)
# override 'put' and 'pull' methods, and change deque's called methods

