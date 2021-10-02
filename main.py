from __future__ import absolute_import
from __future__ import print_function
from bs4 import BeautifulSoup
from sumolib import checkBinary  # noqa
import traci  # noqa
import pandas as pd
import os
import sys
import xml.etree.ElementTree as ET
import random
import csv

# we need to import python modules from the $SUMO_HOME/tools directory
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

def generateRoute(lanesNS, lanesWE, steps, demandN=0.20, demandS=0.20, demandW=0.20, demandE=0.20, accel=0.8, decel=4.5, minLength=5, maxLength=5, minGap=2.5, maxSpeed=25.0,
                  demandProb=None):
    random.seed(42)  # make tests reproducible
    vtypes = []
    # demand per second from different directions
    if demandProb is None:
        # left, straight, right
        demandProb = [1, 1, 1, 1]
    chance = []
    draw_count = 0
    for draw in demandProb:
        for i in range(draw):
            if draw_count == 0:
                chance.append("left")
            elif draw_count == 1:
                chance.append("straight")
            elif draw_count == 2:
                chance.append("right")
            else:
                chance.append("uturn")
        draw_count += 1
    with open("data/cross.rou.xml", "w") as routes:
        print("""<routes>""", file=routes)
        for length in range(minLength, maxLength + 1):
            print("""
<vType id="length_%s" length="%i" accel="%f" decel="%f" sigma="0.5" minGap="%f" maxSpeed="%f" guiShape="passenger">
</vType>""" % (str(length), length, accel, decel, minGap, maxSpeed), file=routes)
            vtypes.append("length_" + str(length))
        print("""
<route id="edgeN_edgeN" edges="edgeN_O edgeN_I" />
<route id="edgeN_edgeS" edges="edgeN_O edgeS_I" />
<route id="edgeN_edgeW" edges="edgeN_O edgeW_I" />
<route id="edgeN_edgeE" edges="edgeN_O edgeE_I" />
<route id="edgeS_edgeN" edges="edgeS_O edgeN_I" />
<route id="edgeS_edgeS" edges="edgeS_O edgeS_I" />
<route id="edgeS_edgeW" edges="edgeS_O edgeW_I" />
<route id="edgeS_edgeE" edges="edgeS_O edgeE_I" />
<route id="edgeW_edgeN" edges="edgeW_O edgeN_I" />
<route id="edgeW_edgeS" edges="edgeW_O edgeS_I" />
<route id="edgeW_edgeW" edges="edgeW_O edgeW_I" />
<route id="edgeW_edgeE" edges="edgeW_O edgeE_I" />
<route id="edgeE_edgeN" edges="edgeE_O edgeN_I" />
<route id="edgeE_edgeS" edges="edgeE_O edgeS_I" />
<route id="edgeE_edgeW" edges="edgeE_O edgeW_I" />
<route id="edgeE_edgeE" edges="edgeE_O edgeE_I" />""", file=routes)
        vehicleCount = 0
        for i in range(steps):
            if random.uniform(0, 1) < demandN:
                direction = random.choice(chance)
                vehicleType = random.choice(vtypes)
                if direction == "left":
                    print('    <vehicle id="%sN_%i" type="%s" route="edgeN_edgeE" depart="%i" departLane="%i" />' % (
                        direction, vehicleCount, vehicleType, i, lanesNS - 1), file=routes)
                elif direction == "right":
                    print('    <vehicle id="%sN_%i" type="%s" route="edgeN_edgeW" depart="%i" departLane="0" />' % (
                        direction, vehicleCount, vehicleType, i), file=routes)
                elif direction == "uturn":
                    print('    <vehicle id="%sN_%i" type="%s" route="edgeN_edgeN" depart="%i" departLane="%i" />' % (
                            direction, vehicleCount, vehicleType, i, lanesNS - 1), file=routes)
                else:
                    print('    <vehicle id="%sN_%i" type="%s" route="edgeN_edgeS" depart="%i" departLane="random" />' % (
                        direction, vehicleCount, vehicleType, i), file=routes)
                vehicleCount += 1
            if random.uniform(0, 1) < demandS:
                direction = random.choice(chance)
                vehicleType = random.choice(vtypes)
                if direction == "left":
                    print('    <vehicle id="%sS_%i" type="%s" route="edgeS_edgeW" depart="%i" departLane="%i" />' % (
                        direction, vehicleCount, vehicleType, i, lanesNS - 1), file=routes)
                elif direction == "right":
                    print('    <vehicle id="%sS_%i" type="%s" route="edgeS_edgeE" depart="%i" departLane="0" />' % (
                        direction, vehicleCount, vehicleType, i), file=routes)
                elif direction == "uturn":
                    print('    <vehicle id="%sS_%i" type="%s" route="edgeS_edgeS" depart="%i" departLane="%i" />' % (
                            direction, vehicleCount, vehicleType, i, lanesNS - 1), file=routes)
                else:
                    print('    <vehicle id="%sS_%i" type="%s" route="edgeS_edgeN" depart="%i" departLane="random" />' % (
                        direction, vehicleCount, vehicleType, i), file=routes)
                vehicleCount += 1
            if random.uniform(0, 1) < demandW:
                direction = random.choice(chance)
                vehicleType = random.choice(vtypes)
                if direction == "left":
                    print('    <vehicle id="%sW_%i" type="%s" route="edgeW_edgeN" depart="%i" departLane="%i" />' % (
                        direction, vehicleCount, vehicleType, i, lanesWE - 1), file=routes)
                elif direction == "right":
                    print('    <vehicle id="%sW_%i" type="%s" route="edgeW_edgeS" depart="%i" departLane="0" />' % (
                        direction, vehicleCount, vehicleType, i), file=routes)
                elif direction == "uturn":
                    print('    <vehicle id="%sW_%i" type="%s" route="edgeW_edgeW" depart="%i" departLane="%i" />' % (
                            direction, vehicleCount, vehicleType, i, lanesWE - 1), file=routes)
                else:
                    print(
                        '    <vehicle id="%sW_%i" type="%s" route="edgeW_edgeE" depart="%i" departLane="random" />' % (
                            direction, vehicleCount, vehicleType, i), file=routes)
                vehicleCount += 1
            if random.uniform(0, 1) < demandE:
                direction = random.choice(chance)
                vehicleType = random.choice(vtypes)
                if direction == "left":
                    print('    <vehicle id="%sE_%i" type="%s" route="edgeE_edgeS" depart="%i" departLane="%i" />' % (
                        direction, vehicleCount, vehicleType, i, lanesWE - 1), file=routes)
                elif direction == "right":
                    print('    <vehicle id="%sE_%i" type="%s" route="edgeE_edgeN" depart="%i" departLane="0" />' % (
                        direction, vehicleCount, vehicleType, i), file=routes)
                elif direction == "uturn":
                    print('    <vehicle id="%sE_%i" type="%s" route="edgeE_edgeE" depart="%i" departLane="%i" />' % (
                            direction, vehicleCount, vehicleType, i, lanesWE - 1), file=routes)
                else:
                    print(
                        '    <vehicle id="%sE_%i" type="%s" route="edgeE_edgeW" depart="%i" departLane="random" />' % (
                            direction, vehicleCount, vehicleType, i), file=routes)
                vehicleCount += 1
        print("</routes>", file=routes)

def setDuration(move, yellow=5):
    with open("data/cross.tls.xml", "w") as tls:
        print("<additional>", file=tls)
        print("""   <tlLogic id="juncMain" type="static" programID="1" offset="0">""", file=tls)
        print("""   </tlLogic>""", file=tls)
        print("</additional>", file=tls)


def createNetwork(lanesNS, lanesWE, outspeedNS=19.0, inspeedNS=11.0, outspeedWE=19.0, inspeedWE=11.0):
    tree = ET.parse("data/cross.edg.xml")

    tl = tree.find(".//edge[@id='edgeN_O']")
    tl.set("numLanes", str(lanesNS))
    tl.set("speed", str(outspeedNS))
    tl = tree.find(".//edge[@id='edgeN_I']")
    tl.set("numLanes", str(lanesNS))
    tl.set("speed", str(inspeedNS))

    tl = tree.find(".//edge[@id='edgeS_O']")
    tl.set("numLanes", str(lanesNS))
    tl.set("speed", str(outspeedNS))
    tl = tree.find(".//edge[@id='edgeS_I']")
    tl.set("numLanes", str(lanesNS))
    tl.set("speed", str(inspeedNS))

    tl = tree.find(".//edge[@id='edgeW_O']")
    tl.set("numLanes", str(lanesWE))
    tl.set("speed", str(outspeedWE))
    tl = tree.find(".//edge[@id='edgeW_I']")
    tl.set("numLanes", str(lanesWE))
    tl.set("speed", str(inspeedWE))

    tl = tree.find(".//edge[@id='edgeE_O']")
    tl.set("numLanes", str(lanesWE))
    tl.set("speed", str(outspeedWE))
    tl = tree.find(".//edge[@id='edgeE_I']")
    tl.set("numLanes", str(lanesWE))
    tl.set("speed", str(inspeedWE))

    tree.write("data/cross.edg.xml")

    os.system("netconvert --node-files=data/cross.nod.xml --edge-files=data/cross.edg.xml --output-file=data/cross.net.xml")

def runSim():
    step = 0
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        step += 1
    traci.close()
    sys.stdout.flush()

def findRate(data):
    with open(data, "r", encoding="utf-8") as file:
        content = file.readlines()
        content = "".join(content)
        soup = BeautifulSoup(content, "lxml")
    all_trips = soup.findAll("tripinfo")
    total = 0
    for trip in all_trips:
        duration = float(trip["duration"])
        loss = float(trip["timeloss"])
        total += (duration / (duration - loss))
    return total / len(all_trips)

def main(duration_min, duration_max, time_steps, lanesNS, lanesWE, csv_path):
    durations = []
    rates = []
    createNetwork(lanesNS, lanesWE)
    for duration in range(duration_min, duration_max + 1):
        generateRoute(lanesNS, lanesWE, time_steps)
        setDuration(duration)
        traci.start([checkBinary('sumo-gui'), "-c", "data/cross.sumocfg",
                     "--tripinfo-output", "tripinfo.xml"])
        runSim()
        durations.append(duration)
        rates.append(findRate("tripinfo.xml"))
    data = pd.DataFrame({"duration": durations, "rates": rates})
    data.to_csv(csv_path)


if __name__ == "__main__":
    main(50, 58, 3000, 5, 5, "record.csv")