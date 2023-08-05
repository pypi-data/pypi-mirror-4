
# Created on 2012.05.03
#
# @author: german

import ars.utils.containers as cont

def test_Queue():
	q = cont.Queue()
	print(q.is_empty())
	print(q.count())

	q.put('first element')
	q.put('second')
	q.put(('third', {'key 1': 1, 'another key': []}))
	print(q.count())

	print(q.pull())
	print(q.pull())

	print(q.count())
	q.put('after some pulls')
	print(q.count())

	print(q.pull())
	print(q.pull())
	print(q.count())

if __name__ == "__main__":
	test_Queue()