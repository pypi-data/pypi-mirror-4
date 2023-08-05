from reaktor import *
import json

# connect to reaktor
reaktor = Reaktor("test@test.de", "test")

# trigger "Test" event
d = {
	"name": "Thomas"
}
ok = reaktor.trigger("Test", data=d, safe=True)

# print result
print "event triggered: " + str(ok)