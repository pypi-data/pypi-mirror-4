from factory import start_pulse_monitor
import json

def pulseCallback(msg):
    pass

def testCallback(msg):
    pass

def buildCallback(builddata):
    print json.dumps(builddata, indent=2)

if __name__ == "__main__":
    monitor = start_pulse_monitor(buildCallback=buildCallback,
                                  pulseCallback=pulseCallback,
#                                  testCallback=testCallback,
                                  trees=['mozilla-central', 'mozilla-inbound'],
                                  buildtypes=['opt'],
                                  platforms=['android'])
    monitor.join()

