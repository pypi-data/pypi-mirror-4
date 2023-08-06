from reaktor import *
import json
from datetime import datetime

# connect to reaktor
reaktor = Reaktor("test@test.de", "test")

# trigger "Test" event
total1 = datetime.now()
for i in range(2):
	d = {
		"name": "Thomas_" + str(i)
	}
	ok = reaktor.trigger("Test", data=d, safe=True)

	# print result
	print str(i) + " event triggered: " + str(ok)

total2 = datetime.now()
total_delta = (total2 - total1)
print "total time: " + str(total_delta)
