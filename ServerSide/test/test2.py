from threading import Event

event = Event()
event.set()
event.wait(5)
print "mama"