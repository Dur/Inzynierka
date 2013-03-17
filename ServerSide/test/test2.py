from Queue import Queue

que = Queue(5)
que.put("ll")
que.put("ll1")
que.put("ll2")
que.put("ll3")
que.put("ll4")

while que.empty() != True:
	print que.get_nowait()
