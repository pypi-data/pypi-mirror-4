from reaktor import *
import json

# connect to reaktor
reaktor = Reaktor("test@test.de", "test")

# trigger "Test" event
d = {
	"test": "Thomas"
}
ok = reaktor.trigger("Test", data=d, safe=False)

# print result
print "event triggered: " + str(ok)