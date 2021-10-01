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

def generateRoute(steps):
    random.seed(42)  # make tests reproducible
    # demand per second from different directions
    pWE = 1. / 20
    pEW = 1. / 20
    pNS = 1. / 20
    pSN = 1. / 20
    with open("data/cross.rou.xml", "w") as routes:
        print("""<routes>
<vType id="typeWE" accel="0.8" decel="4.5" sigma="0.5" length="5" minGap="2.5" maxSpeed="16.67" guiShape="passenger">
</vType>
<vType id="typeNS" accel="0.8" decel="4.5" sigma="0.5" length="5" minGap="2.5" maxSpeed="25" guiShape="passenger">
</vType>

<route id="right" edges="51o 1i 2o 52i" />
<route id="left" edges="52o 2i 1o 51i" />
<route id="down" edges="54o 4i 3o 53i" />
<route id="up" edges="53o 3i 4o 54i" />""", file=routes)
        vehNr = 0
        for i in range(steps):
            if random.uniform(0, 1) < pWE:
                print('    <vehicle id="right_%i" type="typeWE" route="right" depart="%i" />' % (
                    vehNr, i), file=routes)
                vehNr += 1
            if random.uniform(0, 1) < pEW:
                print('    <vehicle id="left_%i" type="typeWE" route="left" depart="%i" />' % (
                    vehNr, i), file=routes)
                vehNr += 1
            if random.uniform(0, 1) < pNS:
                print('    <vehicle id="down_%i" type="typeNS" route="down" depart="%i" color="1,0,0"/>' % (
                    vehNr, i), file=routes)
                vehNr += 1
            if random.uniform(0, 1) < pSN:
                print('    <vehicle id="up_%i" type="typeNS" route="up" depart="%i" color="1,0,0"/>' % (
                    vehNr, i), file=routes)
                vehNr += 1
        print("</routes>", file=routes)

def setDuration(move, yellow=5):
    tree = ET.parse("data/cross.net.xml")

    tl = tree.find(".//phase[@state='GrGr']")
    tl.set("duration", str(move))
    tl = tree.find(".//phase[@state='rGrG']")
    tl.set("duration", str(move))

    tl = tree.find(".//phase[@state='yryr']")
    tl.set("duration", str(yellow))
    tl = tree.find(".//phase[@state='ryry']")
    tl.set("duration", str(yellow))

    tree.write("data/cross.net.xml")

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

def main(csv_path, duration_min, duration_max, time_steps=3000):
    durations = []
    rates = []
    for duration in range(duration_min, duration_max + 1):
        generateRoute(time_steps)
        setDuration(duration)
        traci.start([checkBinary('sumo'), "-c", "data/cross.sumocfg",
                     "--tripinfo-output", "tripinfo.xml"])
        runSim()
        durations.append(duration)
        rates.append(findRate("tripinfo.xml"))
    data = pd.DataFrame({"duration": durations, "rates": rates})
    data.to_csv("record.csv")


if __name__ == "__main__":
    main("record.csv", 50, 58)