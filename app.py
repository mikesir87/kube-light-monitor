from kubernetes import client, config, watch
from blinkstick import blinkstick
import os, sys

if (os.getenv("NODE_HOSTNAME") is None):
    sys.exit("NODE_HOSTNAME is not defined")

hostName = os.getenv("NODE_HOSTNAME")

# 0 = normal top/bottom; 1 = flipped; anything else is same lights
lightMode = os.getenv("LIGHT_MODE", "0")

print("Will be watching for pods on host %s" % hostName)

if (os.getenv("KUBERNETES_SERVICE_HOST") is not None):
    config.load_incluster_config()
else:
    config.load_kube_config()

v1 = client.CoreV1Api()

w = watch.Watch()

pendingPods = []
runningPods = []
failedPods = []
deletingPods = []

light = blinkstick.find_first()

green  = { "red" : 0,  "green" : 25, "blue" : 0  }
blue   = { "red" : 0,  "green" : 0,  "blue" : 50 }
red    = { "red" : 50, "green" : 0,  "blue" : 0  }
orange = { "red" : 60, "green" : 20, "blue" : 0  }
yellow = { "red" : 50, "green" : 50, "blue" : 0  }
black  = { "red" : 0,  "green" : 0,  "blue" : 0  }


def updateLights():
    topColor = {}
    bottomColor = {}

    if len(runningPods) > 0:
        topColor = green
        if len(failedPods) > 0:
            bottomColor = red
        elif len(deletingPods) > 0:
            bottomColor = blue
        elif len(pendingPods):
            bottomColor = yellow
        else:
            bottomColor = green
    else:
        if len(deletingPods) > 0:
            topColor = blue
            bottomColor = blue
        elif len(pendingPods) > 0:
            topColor = yellow
            bottomColor = yellow
        else:
            topColor = black
            bottomColor = black

    if lightMode == "0":
        light.morph(red = topColor['red'], green = topColor['green'], blue = topColor['blue'], index = 0)
        light.morph(red = bottomColor['red'], green = bottomColor['green'], blue = bottomColor['blue'], index = 1)
    elif lightMode == "1":
        light.morph(red = bottomColor['red'], green = bottomColor['green'], blue = bottomColor['blue'], index = 0)
        light.morph(red = topColor['red'], green = topColor['green'], blue = topColor['blue'], index = 1)
    else:
        light.morph(red = bottomColor['red'], green = bottomColor['green'], blue = bottomColor['blue'], index = 0)
        light.morph(red = bottomColor['red'], green = bottomColor['green'], blue = bottomColor['blue'], index = 1)

    print("Number of running: %d" % len(runningPods))
    print("Number of pending: %d" % len(pendingPods))
    print("Number of deleting: %d" % len(deletingPods))
    print("Number of failed: %d\n------------------" % len(failedPods))

for event in w.stream(v1.list_namespaced_pod, namespace = "default"):
    pod = event["object"]

    if pod.spec.node_name != hostName:
        print("Skipping because names don't match %s %s" % (pod.spec.node_name, hostName))
        continue

    podId = pod.metadata.name

    if podId in pendingPods: pendingPods.remove(podId)
    if podId in failedPods: failedPods.remove(podId)
    if podId in runningPods: runningPods.remove(podId)
    if podId in deletingPods: deletingPods.remove(podId)

    if event["type"] != "DELETED":
        if pod.status.phase == "Pending":
            if (pod.status.container_statuses is not None and 
                    pod.status.container_statuses[0].state is not None and 
                    pod.status.container_statuses[0].state.waiting is not None and 
                    pod.status.container_statuses[0].state.waiting.message is not None):
                failedPods.append(podId)
            else:
                pendingPods.append(podId)
        elif pod.metadata.deletion_timestamp is not None:
            deletingPods.append(podId)
        elif pod.status.phase == "Running":
            runningPods.append(podId)
    updateLights()
