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
import multiprocessing as mp
import shutil
from distutils.dir_util import copy_tree
import time
import csv

# we need to import python modules from the $SUMO_HOME/tools directory
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

def generateRoute(folder_name, leftOnlyNS, leftStraightNS, straightOnlyNS, rightStraightNS, rightOnlyNS, allNS,
                  leftOnlyWE, leftStraightWE, straightOnlyWE, rightStraightWE, rightOnlyWE, allWE,
                  steps, demandN, demandS, demandW, demandE, minAccel, maxAccel, minDecel, maxDecel,
                  minLength, maxLength, minGap, maxSpeed, demandProbNS, demandProbWE):
    lanesNS = leftOnlyNS + leftStraightNS + straightOnlyNS + rightStraightNS + rightOnlyNS + allNS + 1
    lanesWE = leftOnlyWE + leftStraightWE + straightOnlyWE + rightStraightWE + rightOnlyWE + allWE + 1
    random.seed(42)  # make tests reproducible

    with open(str(folder_name) + "/cross.rou.xml", "w") as routes:
        print("""<routes>""", file=routes)
        print("""<personFlow id="p" begin="0" end="100" period="2">
       <walk from="edgeN_O" to="edgeS_I" />
   </personFlow>""", file=routes)
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
    <route id="edgeE_edgeE" edges="edgeE_O edgeE_I" />
    """, file=routes)
        vehicleCount = 0
        for i in range(steps):
            if random.uniform(0, 1) < demandN:
                random_direction = random.uniform(0, sum(demandProbNS))
                if random_direction < demandProbNS[0]:
                    direction = "left"
                elif random_direction < demandProbNS[0] + demandProbNS[1]:
                    direction = "straight"
                elif random_direction < demandProbNS[0] + demandProbNS[1] + demandProbNS[2]:
                    direction = "right"
                else:
                    direction = "uturn"
                print("""   <vType id="vehicleN_%i" length="%f" accel="%f" decel="%f" sigma="0.5" minGap="%f" maxSpeed="%f" guiShape="passenger" />"""
                      % (vehicleCount, round(random.uniform(minLength, maxLength), 3), round(random.uniform(minAccel, maxAccel), 3),
                         round(random.uniform(minDecel, maxDecel), 3), minGap, maxSpeed), file=routes)
                if direction == "left":
                    print("""   <vehicle id="%sN_%i" type="vehicleN_%i" route="edgeN_edgeE" depart="%i" departLane="%i" />""" % (
                        direction, vehicleCount, vehicleCount, i, random.randint(lanesNS - leftOnlyNS - leftStraightNS - allNS, lanesNS - 1)), file=routes)
                elif direction == "right":
                    print("""   <vehicle id="%sN_%i" type="vehicleN_%i" route="edgeN_edgeW" depart="%i" departLane="%i" />""" % (
                        direction, vehicleCount, vehicleCount, i, random.randint(1, rightOnlyNS + rightStraightNS + allNS)), file=routes)
                elif direction == "uturn":
                    print("""   <vehicle id="%sN_%i" type="vehicleN_%i" route="edgeN_edgeN" depart="%i" departLane="%i" />""" % (
                            direction, vehicleCount, vehicleCount, i, lanesNS - 1), file=routes)
                else:
                    print("""   <vehicle id="%sN_%i" type="vehicleN_%i" route="edgeN_edgeS" depart="%i" departLane="%i" />""" % (
                        direction, vehicleCount, vehicleCount, i, random.randint(rightOnlyNS + 1, rightOnlyNS + rightStraightNS + allNS + straightOnlyNS + leftStraightNS)), file=routes)
                vehicleCount += 1
                print("", file=routes)
            if random.uniform(0, 1) < demandS:
                random_direction = random.uniform(0, sum(demandProbNS))
                if random_direction < demandProbNS[0]:
                    direction = "left"
                elif random_direction < demandProbNS[0] + demandProbNS[1]:
                    direction = "straight"
                elif random_direction < demandProbNS[0] + demandProbNS[1] + demandProbNS[2]:
                    direction = "right"
                else:
                    direction = "uturn"
                print("""   <vType id="vehicleS_%i" length="%f" accel="%f" decel="%f" sigma="0.5" minGap="%f" maxSpeed="%f" guiShape="passenger" />"""
                      % (vehicleCount, round(random.uniform(minLength, maxLength), 3), round(random.uniform(minAccel, maxAccel), 3),
                         round(random.uniform(minDecel, maxDecel), 3), minGap, maxSpeed), file=routes)
                if direction == "left":
                    print("""   <vehicle id="%sS_%i" type="vehicleS_%i" route="edgeS_edgeW" depart="%i" departLane="%i" />""" % (
                        direction, vehicleCount, vehicleCount, i, random.randint(lanesNS - leftOnlyNS - leftStraightNS - allNS, lanesNS - 1)), file=routes)
                elif direction == "right":
                    print("""   <vehicle id="%sS_%i" type="vehicleS_%i" route="edgeS_edgeE" depart="%i" departLane="%i" />""" % (
                        direction, vehicleCount, vehicleCount, i, random.randint(1, rightOnlyNS + rightStraightNS + allNS)), file=routes)
                elif direction == "uturn":
                    print("""   <vehicle id="%sS_%i" type="vehicleS_%i" route="edgeS_edgeS" depart="%i" departLane="%i" />""" % (
                            direction, vehicleCount, vehicleCount, i, lanesNS - 1), file=routes)
                else:
                    print("""   <vehicle id="%sS_%i" type="vehicleS_%i" route="edgeS_edgeN" depart="%i" departLane="%i" />""" % (
                        direction, vehicleCount, vehicleCount, i, random.randint(rightOnlyNS + 1, rightOnlyNS + rightStraightNS + allNS + straightOnlyNS + leftStraightNS)), file=routes)
                vehicleCount += 1
                print("", file=routes)
            if random.uniform(0, 1) < demandW:
                random_direction = random.uniform(0, sum(demandProbWE))
                if random_direction < demandProbWE[0]:
                    direction = "left"
                elif random_direction < demandProbWE[0] + demandProbWE[1]:
                    direction = "straight"
                elif random_direction < demandProbWE[0] + demandProbWE[1] + demandProbWE[2]:
                    direction = "right"
                else:
                    direction = "uturn"
                print("""   <vType id="vehicleW_%i" length="%f" accel="%f" decel="%f" sigma="0.5" minGap="%f" maxSpeed="%f" guiShape="passenger" />"""
                      % (vehicleCount, round(random.uniform(minLength, maxLength), 3), round(random.uniform(minAccel, maxAccel), 3),
                         round(random.uniform(minDecel, maxDecel), 3), minGap, maxSpeed), file=routes)
                if direction == "left":
                    print("""   <vehicle id="%sW_%i" type="vehicleW_%i" route="edgeW_edgeN" depart="%i" departLane="%i" />""" % (
                        direction, vehicleCount, vehicleCount, i, random.randint(lanesWE - leftOnlyWE - leftStraightWE - allWE, lanesWE - 1)), file=routes)
                elif direction == "right":
                    print("""   <vehicle id="%sW_%i" type="vehicleW_%i" route="edgeW_edgeS" depart="%i" departLane="%i" />""" % (
                        direction, vehicleCount, vehicleCount, i, random.randint(1, rightOnlyWE + rightStraightWE + allWE)), file=routes)
                elif direction == "uturn":
                    print("""   <vehicle id="%sW_%i" type="vehicleW_%i" route="edgeW_edgeW" depart="%i" departLane="%i" />""" % (
                            direction, vehicleCount, vehicleCount, i, lanesWE - 1), file=routes)
                else:
                    print("""   <vehicle id="%sW_%i" type="vehicleW_%i" route="edgeW_edgeE" depart="%i" departLane="%i" />""" % (
                            direction, vehicleCount, vehicleCount, i, random.randint(rightOnlyWE + 1, rightOnlyWE + rightStraightWE + allWE + straightOnlyWE + leftStraightWE)), file=routes)
                vehicleCount += 1
                print("", file=routes)
            if random.uniform(0, 1) < demandE:
                random_direction = random.uniform(0, sum(demandProbWE))
                if random_direction < demandProbWE[0]:
                    direction = "left"
                elif random_direction < demandProbWE[0] + demandProbWE[1]:
                    direction = "straight"
                elif random_direction < demandProbWE[0] + demandProbWE[1] + demandProbWE[2]:
                    direction = "right"
                else:
                    direction = "uturn"
                print("""   <vType id="vehicleE_%i" length="%f" accel="%f" decel="%f" sigma="0.5" minGap="%f" maxSpeed="%f" guiShape="passenger" />"""
                      % (vehicleCount, round(random.uniform(minLength, maxLength), 3), round(random.uniform(minAccel, maxAccel), 3),
                         round(random.uniform(minDecel, maxDecel), 3), minGap, maxSpeed), file=routes)
                if direction == "left":
                    print("""   <vehicle id="%sE_%i" type="vehicleE_%i" route="edgeE_edgeS" depart="%i" departLane="%i" />""" % (
                        direction, vehicleCount, vehicleCount, i, random.randint(lanesWE - leftOnlyWE - leftStraightWE - allWE, lanesWE - 1)), file=routes)
                elif direction == "right":
                    print("""   <vehicle id="%sE_%i" type="vehicleE_%i" route="edgeE_edgeN" depart="%i" departLane="%i" />""" % (
                        direction, vehicleCount, vehicleCount, i, random.randint(1, rightOnlyWE + rightStraightWE + allWE)), file=routes)
                elif direction == "uturn":
                    print("""   <vehicle id="%sE_%i" type="vehicleE_%i" route="edgeE_edgeE" depart="%i" departLane="%i" />""" % (
                            direction, vehicleCount, vehicleCount, i, lanesWE - 1), file=routes)
                else:
                    print("""   <vehicle id="%sE_%i" type="vehicleE_%i" route="edgeE_edgeW" depart="%i" departLane="%i" />""" % (
                            direction, vehicleCount, vehicleCount, i, random.randint(rightOnlyWE + 1, rightOnlyWE + rightStraightWE + allWE + straightOnlyWE + leftStraightWE)), file=routes)
                vehicleCount += 1
                print("", file=routes)
        print("</routes>", file=routes)

def setDuration(folder_name, leftOnlyNS, leftStraightNS, straightOnlyNS, rightStraightNS, rightOnlyNS, allNS,
                leftOnlyWE, leftStraightWE, straightOnlyWE, rightStraightWE, rightOnlyWE, allWE,
                leftOutLanesNS, rightOutLanesNS, leftOutLanesWE, rightOutLanesWE,
                moveNS, moveWE, yellowNS, yellowWE, turnNS, turnWE):

    lanesNS = leftOnlyNS + leftStraightNS + straightOnlyNS + rightStraightNS + rightOnlyNS + allNS + 1
    lanesWE = leftOnlyWE + leftStraightWE + straightOnlyWE + rightStraightWE + rightOnlyWE + allWE + 1

    status = []
    for state in range(6):
        temp_string = ""
        if state == 0:
            for run in range(2):
                # North and South
                for lane in range(rightOnlyNS):
                    if lane == 0:
                        for i in range(rightOutLanesNS):
                            temp_string += "G"
                    else:
                        for i in range(rightOutLanesNS):
                            temp_string += "g"
                for lane in range(rightStraightNS):
                    for i in range(rightOutLanesNS):
                        temp_string += "g"
                    temp_string += "G"
                for lane in range(straightOnlyNS):
                    temp_string += "G"
                for lane in range(allNS):
                    for i in range(rightOutLanesNS):
                        temp_string += "g"
                    temp_string += "G"
                    for i in range(leftOutLanesNS):
                        temp_string += "g"
                for lane in range(leftStraightNS):
                    temp_string += "G"
                    for i in range(leftOutLanesNS):
                        temp_string += "g"
                for lane in range(leftOnlyNS):
                    for i in range(leftOutLanesNS):
                        temp_string += "g"
                if leftOnlyNS + leftStraightNS + allNS > 0:
                    temp_string += "g"
                # West and East
                for lane in range(rightOnlyWE):
                    for i in range(rightOutLanesWE):
                        temp_string += "r"
                for lane in range(rightStraightWE):
                    for i in range(rightOutLanesWE):
                        temp_string += "r"
                    temp_string += "r"
                for lane in range(straightOnlyWE):
                    temp_string += "r"
                for lane in range(allWE):
                    for i in range(rightOutLanesWE):
                        temp_string += "r"
                    temp_string += "r"
                    for i in range(leftOutLanesWE):
                        temp_string += "r"
                for lane in range(leftStraightWE):
                    temp_string += "r"
                    for i in range(leftOutLanesWE):
                        temp_string += "r"
                for lane in range(leftOnlyWE):
                    for i in range(leftOutLanesWE):
                        temp_string += "r"
                if leftOnlyWE + leftStraightWE + allWE > 0:
                    temp_string += "r"
            temp_string += "rGrG"
            status.append(temp_string)
        elif state == 1:
            for run in range(2):
                # North and South
                for lane in range(rightOnlyNS):
                    for i in range(rightOutLanesNS):
                        temp_string += "y"
                for lane in range(rightStraightNS):
                    for i in range(rightOutLanesNS):
                        temp_string += "y"
                    temp_string += "y"
                for lane in range(straightOnlyNS):
                    temp_string += "y"
                for lane in range(allNS):
                    for i in range(rightOutLanesNS):
                        temp_string += "y"
                    temp_string += "y"
                    for i in range(leftOutLanesNS):
                        temp_string += "y"
                for lane in range(leftStraightNS):
                    temp_string += "y"
                    for i in range(leftOutLanesNS):
                        temp_string += "y"
                for lane in range(leftOnlyNS):
                    for i in range(leftOutLanesNS):
                        temp_string += "y"
                if leftOnlyNS + leftStraightNS + allNS > 0:
                    temp_string += "y"
                # West and East
                for lane in range(rightOnlyWE):
                    for i in range(rightOutLanesWE):
                        temp_string += "r"
                for lane in range(rightStraightWE):
                    for i in range(rightOutLanesWE):
                        temp_string += "r"
                    temp_string += "r"
                for lane in range(straightOnlyWE):
                    temp_string += "r"
                for lane in range(allWE):
                    for i in range(rightOutLanesWE):
                        temp_string += "r"
                    temp_string += "r"
                    for i in range(leftOutLanesWE):
                        temp_string += "r"
                for lane in range(leftStraightWE):
                    temp_string += "r"
                    for i in range(leftOutLanesWE):
                        temp_string += "r"
                for lane in range(leftOnlyWE):
                    for i in range(leftOutLanesWE):
                        temp_string += "r"
                if leftOnlyWE + leftStraightWE + allWE > 0:
                    temp_string += "r"
            temp_string += "rGrG"
            status.append(temp_string)
        elif state == 2:
            for run in range(2):
                # North and South
                for lane in range(rightOnlyNS):
                    for i in range(rightOutLanesNS):
                        temp_string += "r"
                for lane in range(rightStraightNS):
                    for i in range(rightOutLanesNS):
                        temp_string += "r"
                    temp_string += "r"
                for lane in range(straightOnlyNS):
                    temp_string += "r"
                for lane in range(allNS):
                    for i in range(rightOutLanesNS):
                        temp_string += "r"
                    temp_string += "r"
                    for i in range(leftOutLanesNS):
                        temp_string += "r"
                for lane in range(leftStraightNS):
                    temp_string += "r"
                    for i in range(leftOutLanesNS):
                        temp_string += "r"
                for lane in range(leftOnlyNS):
                    for i in range(leftOutLanesNS):
                        temp_string += "r"
                if leftOnlyNS + leftStraightNS + allNS > 0:
                    temp_string += "r"
                # West and East
                for lane in range(rightOnlyWE):
                    for i in range(rightOutLanesWE):
                        temp_string += "r"
                for lane in range(rightStraightWE):
                    for i in range(rightOutLanesWE):
                        temp_string += "r"
                    temp_string += "r"
                for lane in range(straightOnlyWE):
                    temp_string += "r"
                for lane in range(allWE):
                    for i in range(rightOutLanesWE):
                        temp_string += "r"
                    temp_string += "r"
                    for i in range(leftOutLanesWE):
                        temp_string += "r"
                for lane in range(leftStraightWE):
                    temp_string += "r"
                    for i in range(leftOutLanesWE):
                        temp_string += "r"
                for lane in range(leftOnlyWE):
                    if lane == leftOnlyWE - 1:
                        for i in range(leftOutLanesWE):
                            temp_string += "G"
                    else:
                        for i in range(leftOutLanesWE):
                            temp_string += "g"
                if leftOnlyWE + leftStraightWE + allWE > 0:
                    temp_string += "G"
            temp_string += "rrrr"
            status.append(temp_string)
        elif state == 3:
            for run in range(2):
                # North and South
                for lane in range(rightOnlyNS):
                    for i in range(rightOutLanesNS):
                        temp_string += "r"
                for lane in range(rightStraightNS):
                    for i in range(rightOutLanesNS):
                        temp_string += "r"
                    temp_string += "r"
                for lane in range(straightOnlyNS):
                    temp_string += "r"
                for lane in range(allNS):
                    for i in range(rightOutLanesNS):
                        temp_string += "r"
                    temp_string += "r"
                    for i in range(leftOutLanesNS):
                        temp_string += "r"
                for lane in range(leftStraightNS):
                    temp_string += "r"
                    for i in range(leftOutLanesNS):
                        temp_string += "r"
                for lane in range(leftOnlyNS):
                    for i in range(leftOutLanesNS):
                        temp_string += "r"
                if leftOnlyNS + leftStraightNS + allNS > 0:
                    temp_string += "r"
                # West and East
                for lane in range(rightOnlyWE):
                    if lane == 0:
                        for i in range(rightOutLanesWE):
                            temp_string += "G"
                    else:
                        for i in range(rightOutLanesWE):
                            temp_string += "g"
                for lane in range(rightStraightWE):
                    for i in range(rightOutLanesWE):
                        temp_string += "g"
                    temp_string += "G"
                for lane in range(straightOnlyWE):
                    temp_string += "G"
                for lane in range(allWE):
                    for i in range(rightOutLanesWE):
                        temp_string += "g"
                    temp_string += "G"
                    for i in range(leftOutLanesWE):
                        temp_string += "g"
                for lane in range(leftStraightWE):
                    temp_string += "G"
                    for i in range(leftOutLanesWE):
                        temp_string += "g"
                for lane in range(leftOnlyWE):
                    for i in range(leftOutLanesWE):
                        temp_string += "g"
                if leftOnlyWE + leftStraightWE + allWE > 0:
                    temp_string += "g"
            temp_string += "GrGr"
            status.append(temp_string)
        elif state == 4:
            for run in range(2):
                # North and South
                for lane in range(rightOnlyNS):
                    for i in range(rightOutLanesNS):
                        temp_string += "r"
                for lane in range(rightStraightNS):
                    for i in range(rightOutLanesNS):
                        temp_string += "r"
                    temp_string += "r"
                for lane in range(straightOnlyNS):
                    temp_string += "r"
                for lane in range(allNS):
                    for i in range(rightOutLanesNS):
                        temp_string += "r"
                    temp_string += "r"
                    for i in range(leftOutLanesNS):
                        temp_string += "r"
                for lane in range(leftStraightNS):
                    temp_string += "r"
                    for i in range(leftOutLanesNS):
                        temp_string += "r"
                for lane in range(leftOnlyNS):
                    for i in range(leftOutLanesNS):
                        temp_string += "r"
                if leftOnlyNS + leftStraightNS + allNS > 0:
                    temp_string += "r"
                # West and East
                for lane in range(rightOnlyWE):
                    for i in range(rightOutLanesWE):
                        temp_string += "y"
                for lane in range(rightStraightWE):
                    for i in range(rightOutLanesWE):
                        temp_string += "y"
                    temp_string += "y"
                for lane in range(straightOnlyWE):
                    temp_string += "y"
                for lane in range(allWE):
                    for i in range(rightOutLanesWE):
                        temp_string += "y"
                    temp_string += "y"
                    for i in range(leftOutLanesWE):
                        temp_string += "y"
                for lane in range(leftStraightWE):
                    temp_string += "y"
                    for i in range(leftOutLanesWE):
                        temp_string += "y"
                for lane in range(leftOnlyWE):
                    for i in range(leftOutLanesWE):
                        temp_string += "y"
                if leftOnlyWE + leftStraightWE + allWE > 0:
                    temp_string += "y"
            temp_string += "GrGr"
            status.append(temp_string)
        elif state == 5:
            for run in range(2):
                # North and South
                for lane in range(rightOnlyNS):
                    for i in range(rightOutLanesNS):
                        temp_string += "r"
                for lane in range(rightStraightNS):
                    for i in range(rightOutLanesNS):
                        temp_string += "r"
                    temp_string += "r"
                for lane in range(straightOnlyNS):
                    temp_string += "r"
                for lane in range(allNS):
                    for i in range(rightOutLanesNS):
                        temp_string += "r"
                    temp_string += "r"
                    for i in range(leftOutLanesNS):
                        temp_string += "r"
                for lane in range(leftStraightNS):
                    temp_string += "r"
                    for i in range(leftOutLanesNS):
                        temp_string += "r"
                for lane in range(leftOnlyNS):
                    if lane == leftOnlyNS - 1:
                        for i in range(leftOutLanesNS):
                            temp_string += "G"
                    else:
                        for i in range(leftOutLanesNS):
                            temp_string += "g"
                if leftOnlyNS + leftStraightNS + allNS > 0:
                    temp_string += "G"
                # West and East
                for lane in range(rightOnlyWE):
                    for i in range(rightOutLanesWE):
                        temp_string += "r"
                for lane in range(rightStraightWE):
                    for i in range(rightOutLanesWE):
                        temp_string += "r"
                    temp_string += "r"
                for lane in range(straightOnlyWE):
                    temp_string += "r"
                for lane in range(allWE):
                    for i in range(rightOutLanesWE):
                        temp_string += "r"
                    temp_string += "r"
                    for i in range(leftOutLanesWE):
                        temp_string += "r"
                for lane in range(leftStraightWE):
                    temp_string += "r"
                    for i in range(leftOutLanesWE):
                        temp_string += "r"
                for lane in range(leftOnlyWE):
                    for i in range(leftOutLanesWE):
                        temp_string += "r"
                if leftOnlyWE + leftStraightWE + allWE > 0:
                    temp_string += "r"
            temp_string += "rrrr"
            status.append(temp_string)

    with open(str(folder_name) + "/cross.tls.xml", "w") as tls:
        print("<additional>", file=tls)
        print("""   <tlLogic id="juncMain" type="static" programID="1" offset="0">""", file=tls)
        if moveNS != 0 and lanesNS != 0:
            print("""       <phase duration="%f" state="%s"/>""" % (moveNS, status[0]), file=tls)
        if yellowNS != 0 and lanesNS != 0:
            print("""       <phase duration="%f" state="%s"/>""" % (yellowNS, status[1]), file=tls)
        if turnWE != 0 and leftOnlyWE != 0:
            print("""       <phase duration="%f" state="%s"/>""" % (turnWE, status[2]), file=tls)
        if moveWE != 0 and lanesWE != 0:
            print("""       <phase duration="%f" state="%s"/>""" % (moveWE, status[3]), file=tls)
        if yellowWE != 0 and lanesWE != 0:
            print("""       <phase duration="%f" state="%s"/>""" % (yellowWE, status[4]), file=tls)
        if turnNS != 0 and leftOnlyNS != 0:
            print("""       <phase duration="%f" state="%s"/>""" % (turnNS, status[5]), file=tls)
        print("""   </tlLogic>""", file=tls)
        print("</additional>", file=tls)

def buildConnections(folder_name, leftOnlyNS, leftStraightNS, straightOnlyNS, rightStraightNS, rightOnlyNS, allNS,
                     leftOnlyWE, leftStraightWE, straightOnlyWE, rightStraightWE, rightOnlyWE, allWE,
                     leftOutLanesNS, rightOutLanesNS, leftOutLanesWE, rightOutLanesWE):

    lanesNS = leftOnlyNS + leftStraightNS + straightOnlyNS + rightStraightNS + rightOnlyNS + allNS + 1
    lanesWE = leftOnlyWE + leftStraightWE + straightOnlyWE + rightStraightWE + rightOnlyWE + allWE + 1

    with open(str(folder_name) + "/cross.con.xml", "w") as connections:
        print("""<connections>""", file=connections)
        print("""   <crossing width="4.00" priority="1" edges="edgeN_I edgeN_O" node="juncMain"/>
    <crossing width="4.00" edges="edgeE_I edgeE_O" node="juncMain"/>
    <crossing width="4.00" edges="edgeS_I edgeS_O" node="juncMain"/>
    <crossing width="4.00" edges="edgeW_I edgeW_O" node="juncMain"/>""", file=connections)
        # North
        print("""   <!-- North -->""", file=connections)
        lane_count = 1
        for i in range(rightOnlyNS):
            for lane in range(rightOutLanesNS):
                print("""   <connection from="edgeN_O" to="edgeW_I" fromLane="%i" toLane="%i"/>"""
                      % (lane_count, lane + 1), file=connections)
            lane_count += 1
        if rightOnlyNS > 0:
            print("", file=connections)
        for i in range(rightStraightNS):
            for lane in range(rightOutLanesNS):
                print("""   <connection from="edgeN_O" to="edgeW_I" fromLane="%i" toLane="%i"/>"""
                      % (lane_count, lane + 1), file=connections)
            print("""   <connection from="edgeN_O" to="edgeS_I" fromLane="%i" toLane="%i"/>"""
                  % (lane_count, lane_count), file=connections)
            lane_count += 1
        if rightStraightNS > 0:
            print("", file=connections)
        for i in range(straightOnlyNS):
            print("""   <connection from="edgeN_O" to="edgeS_I" fromLane="%i" toLane="%i"/>"""
                  % (lane_count, lane_count), file=connections)
            lane_count += 1
        if straightOnlyNS > 0:
            print("", file=connections)
        for i in range(allNS):
            for lane in range(rightOutLanesNS):
                print("""   <connection from="edgeN_O" to="edgeW_I" fromLane="%i" toLane="%i"/>"""
                      % (lane_count, lane + 1), file=connections)
            print("""   <connection from="edgeN_O" to="edgeS_I" fromLane="%i" toLane="%i"/>"""
                  % (lane_count, lane_count), file=connections)
            for lane in range(leftOutLanesNS):
                print("""   <connection from="edgeN_O" to="edgeE_I" fromLane="%i" toLane="%i"/>"""
                      % (lane_count, lanesWE - 1 - lane), file=connections)
            lane_count += 1
        if allNS > 0:
            print("", file=connections)
        for i in range(leftStraightNS):
            for lane in range(leftOutLanesNS):
                print("""   <connection from="edgeN_O" to="edgeE_I" fromLane="%i" toLane="%i"/>"""
                      % (lane_count, lanesWE - 1 - lane), file=connections)
            print("""   <connection from="edgeN_O" to="edgeS_I" fromLane="%i" toLane="%i"/>"""
                  % (lane_count, lane_count), file=connections)
            lane_count += 1
        if leftStraightNS > 0:
            print("", file=connections)
        for i in range(leftOnlyNS):
            for lane in range(leftOutLanesNS):
                print("""   <connection from="edgeN_O" to="edgeE_I" fromLane="%i" toLane="%i"/>"""
                      % (lane_count, lanesWE - 1 - lane), file=connections)
            lane_count += 1
        if leftOnlyNS > 0:
            print("", file=connections)
        if leftOnlyNS > 0 or leftStraightNS > 0 or allNS > 0:
            print("""   <connection from="edgeN_O" to="edgeN_I" fromLane="%i" toLane="%i"/>"""
                  % (lane_count - 1, lanesNS - 1), file=connections)
            print("", file=connections)

        # South
        print("""   <!-- South -->""", file=connections)
        lane_count = 1
        for i in range(rightOnlyNS):
            for lane in range(rightOutLanesNS):
                print("""   <connection from="edgeS_O" to="edgeE_I" fromLane="%i" toLane="%i"/>"""
                      % (lane_count, lane + 1), file=connections)
            lane_count += 1
        if rightOnlyNS > 0:
            print("", file=connections)
        for i in range(rightStraightNS):
            for lane in range(rightOutLanesNS):
                print("""   <connection from="edgeS_O" to="edgeE_I" fromLane="%i" toLane="%i"/>"""
                      % (lane_count, lane + 1), file=connections)
            print("""   <connection from="edgeS_O" to="edgeN_I" fromLane="%i" toLane="%i"/>"""
                  % (lane_count, lane_count), file=connections)
            lane_count += 1
        if rightStraightNS > 0:
            print("", file=connections)
        for i in range(straightOnlyNS):
            print("""   <connection from="edgeS_O" to="edgeN_I" fromLane="%i" toLane="%i"/>"""
                  % (lane_count, lane_count), file=connections)
            lane_count += 1
        if straightOnlyNS > 0:
            print("", file=connections)
        for i in range(allNS):
            for lane in range(rightOutLanesNS):
                print("""   <connection from="edgeS_O" to="edgeE_I" fromLane="%i" toLane="%i"/>"""
                      % (lane_count, lane + 1), file=connections)
            print("""   <connection from="edgeS_O" to="edgeN_I" fromLane="%i" toLane="%i"/>"""
                  % (lane_count, lane_count), file=connections)
            for lane in range(leftOutLanesNS):
                print("""   <connection from="edgeS_O" to="edgeW_I" fromLane="%i" toLane="%i"/>"""
                      % (lane_count, lanesWE - 1 - lane), file=connections)
            lane_count += 1
        if allNS > 0:
            print("", file=connections)
        for i in range(leftStraightNS):
            for lane in range(leftOutLanesNS):
                print("""   <connection from="edgeS_O" to="edgeW_I" fromLane="%i" toLane="%i"/>"""
                      % (lane_count, lanesWE - 1 - lane), file=connections)
            print("""   <connection from="edgeS_O" to="edgeN_I" fromLane="%i" toLane="%i"/>"""
                  % (lane_count, lane_count), file=connections)
            lane_count += 1
        if leftStraightNS > 0:
            print("", file=connections)
        for i in range(leftOnlyNS):
            for lane in range(leftOutLanesNS):
                print("""   <connection from="edgeS_O" to="edgeW_I" fromLane="%i" toLane="%i"/>"""
                      % (lane_count, lanesWE - 1 - lane), file=connections)
            lane_count += 1
        if leftOnlyNS > 0:
            print("", file=connections)
        if leftOnlyNS > 0 or leftStraightNS > 0 or allNS > 0:
            print("""   <connection from="edgeS_O" to="edgeS_I" fromLane="%i" toLane="%i"/>"""
                  % (lane_count - 1, lanesNS - 1), file=connections)
            print("", file=connections)

        # West
        print("""   <!-- West -->""", file=connections)
        lane_count = 1
        for i in range(rightOnlyWE):
            for lane in range(rightOutLanesWE):
                print("""   <connection from="edgeW_O" to="edgeS_I" fromLane="%i" toLane="%i"/>"""
                      % (lane_count, lane + 1), file=connections)
            lane_count += 1
        if rightOnlyWE > 0:
            print("", file=connections)
        for i in range(rightStraightWE):
            for lane in range(rightOutLanesWE):
                print("""   <connection from="edgeW_O" to="edgeS_I" fromLane="%i" toLane="%i"/>"""
                      % (lane_count, lane + 1), file=connections)
            print("""   <connection from="edgeW_O" to="edgeE_I" fromLane="%i" toLane="%i"/>"""
                  % (lane_count, lane_count), file=connections)
            lane_count += 1
        if rightStraightWE > 0:
            print("", file=connections)
        for i in range(straightOnlyWE):
            print("""   <connection from="edgeW_O" to="edgeE_I" fromLane="%i" toLane="%i"/>"""
                  % (lane_count, lane_count), file=connections)
            lane_count += 1
        if straightOnlyWE > 0:
            print("", file=connections)
        for i in range(allWE):
            for lane in range(rightOutLanesWE):
                print("""   <connection from="edgeW_O" to="edgeS_I" fromLane="%i" toLane="%i"/>"""
                      % (lane_count, lane + 1), file=connections)
            print("""   <connection from="edgeW_O" to="edgeE_I" fromLane="%i" toLane="%i"/>"""
                  % (lane_count, lane_count), file=connections)
            for lane in range(leftOutLanesWE):
                print("""   <connection from="edgeW_O" to="edgeN_I" fromLane="%i" toLane="%i"/>"""
                      % (lane_count, lanesNS - 1 - lane), file=connections)
            lane_count += 1
        if allWE > 0:
            print("", file=connections)
        for i in range(leftStraightWE):
            for lane in range(leftOutLanesWE):
                print("""   <connection from="edgeW_O" to="edgeN_I" fromLane="%i" toLane="%i"/>"""
                      % (lane_count, lanesNS - 1 - lane), file=connections)
            print("""   <connection from="edgeW_O" to="edgeE_I" fromLane="%i" toLane="%i"/>"""
                  % (lane_count, lane_count), file=connections)
            lane_count += 1
        if leftStraightWE > 0:
            print("", file=connections)
        for i in range(leftOnlyWE):
            for lane in range(leftOutLanesWE):
                print("""   <connection from="edgeW_O" to="edgeN_I" fromLane="%i" toLane="%i"/>"""
                      % (lane_count, lanesNS - 1 - lane), file=connections)
            lane_count += 1
        if leftOnlyWE > 0:
            print("", file=connections)
        if leftOnlyWE > 0 or leftStraightWE > 0 or allWE > 0:
            print("""   <connection from="edgeW_O" to="edgeW_I" fromLane="%i" toLane="%i"/>"""
                  % (lane_count - 1, lanesWE - 1), file=connections)
            print("", file=connections)

        # East
        print("""   <!-- East -->""", file=connections)
        lane_count = 1
        for i in range(rightOnlyWE):
            for lane in range(rightOutLanesWE):
                print("""   <connection from="edgeE_O" to="edgeN_I" fromLane="%i" toLane="%i"/>"""
                      % (lane_count, lane + 1), file=connections)
            lane_count += 1
        if rightOnlyWE > 0:
            print("", file=connections)
        for i in range(rightStraightWE):
            for lane in range(rightOutLanesWE):
                print("""   <connection from="edgeE_O" to="edgeN_I" fromLane="%i" toLane="%i"/>"""
                      % (lane_count, lane + 1), file=connections)
            print("""   <connection from="edgeE_O" to="edgeW_I" fromLane="%i" toLane="%i"/>"""
                  % (lane_count, lane_count), file=connections)
            lane_count += 1
        if rightStraightWE > 0:
            print("", file=connections)
        for i in range(straightOnlyWE):
            print("""   <connection from="edgeE_O" to="edgeW_I" fromLane="%i" toLane="%i"/>"""
                  % (lane_count, lane_count), file=connections)
            lane_count += 1
        if straightOnlyWE > 0:
            print("", file=connections)
        for i in range(allWE):
            for lane in range(rightOutLanesWE):
                print("""   <connection from="edgeE_O" to="edgeN_I" fromLane="%i" toLane="%i"/>"""
                      % (lane_count, lane + 1), file=connections)
            print("""   <connection from="edgeE_O" to="edgeW_I" fromLane="%i" toLane="%i"/>"""
                  % (lane_count, lane_count), file=connections)
            for lane in range(leftOutLanesWE):
                print("""   <connection from="edgeE_O" to="edgeS_I" fromLane="%i" toLane="%i"/>"""
                      % (lane_count, lanesNS - 1 - lane), file=connections)
            lane_count += 1
        if allWE > 0:
            print("", file=connections)
        for i in range(leftStraightWE):
            for lane in range(leftOutLanesWE):
                print("""   <connection from="edgeE_O" to="edgeS_I" fromLane="%i" toLane="%i"/>"""
                      % (lane_count, lanesNS - 1 - lane), file=connections)
            print("""   <connection from="edgeE_O" to="edgeW_I" fromLane="%i" toLane="%i"/>"""
                  % (lane_count, lane_count), file=connections)
            lane_count += 1
        if leftStraightWE > 0:
            print("", file=connections)
        for i in range(leftOnlyWE):
            for lane in range(leftOutLanesWE):
                print("""   <connection from="edgeE_O" to="edgeS_I" fromLane="%i" toLane="%i"/>"""
                      % (lane_count, lanesNS - 1 - lane), file=connections)
            lane_count += 1
        if leftOnlyWE > 0:
            print("", file=connections)
        if leftOnlyWE > 0 or leftStraightWE > 0 or allWE > 0:
            print("""   <connection from="edgeE_O" to="edgeE_I" fromLane="%i" toLane="%i"/>"""
                  % (lane_count - 1, lanesWE - 1), file=connections)
        print("</connections>", file=connections)

def createNetwork(folder_name, leftOnlyNS, leftStraightNS, straightOnlyNS, rightStraightNS, rightOnlyNS, allNS,
                  leftOnlyWE, leftStraightWE, straightOnlyWE, rightStraightWE, rightOnlyWE, allWE,
                  outspeedNS, inspeedNS, outspeedWE, inspeedWE):
    lanesNS = leftOnlyNS + leftStraightNS + straightOnlyNS + rightStraightNS + rightOnlyNS + allNS
    lanesWE = leftOnlyWE + leftStraightWE + straightOnlyWE + rightStraightWE + rightOnlyWE + allWE

    tree = ET.parse(str(folder_name) + "/cross.edg.xml")

    tl = tree.find(".//edge[@id='edgeN_O']")
    tl.set("numLanes", str(lanesNS + 1))
    tl.set("speed", str(outspeedNS))
    tl = tree.find(".//edge[@id='edgeN_I']")
    tl.set("numLanes", str(lanesNS + 1))
    tl.set("speed", str(inspeedNS))

    tl = tree.find(".//edge[@id='edgeS_O']")
    tl.set("numLanes", str(lanesNS + 1))
    tl.set("speed", str(outspeedNS))
    tl = tree.find(".//edge[@id='edgeS_I']")
    tl.set("numLanes", str(lanesNS + 1))
    tl.set("speed", str(inspeedNS))

    tl = tree.find(".//edge[@id='edgeW_O']")
    tl.set("numLanes", str(lanesWE + 1))
    tl.set("speed", str(outspeedWE))
    tl = tree.find(".//edge[@id='edgeW_I']")
    tl.set("numLanes", str(lanesWE + 1))
    tl.set("speed", str(inspeedWE))

    tl = tree.find(".//edge[@id='edgeE_O']")
    tl.set("numLanes", str(lanesWE + 1))
    tl.set("speed", str(outspeedWE))
    tl = tree.find(".//edge[@id='edgeE_I']")
    tl.set("numLanes", str(lanesWE + 1))
    tl.set("speed", str(inspeedWE))

    tree.write(str(folder_name) + "/cross.edg.xml")

    os.system("netconvert --node-files=%s/cross.nod.xml --edge-files=%s/cross.edg.xml --connection-files=%s/cross.con.xml --output-file=%s/cross.net.xml --no-turnarounds.except-turnlane=true" % (folder_name, folder_name, folder_name, folder_name))

def runSim(time_steps):
    step = 0
    while step <= time_steps:
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
        # total += (duration / (duration - loss))
        total += ((duration - loss) / duration)
    return total / len(all_trips)

def setup(csv_path):
    dataframe = pd.read_csv(csv_path, sep='\t',
                            names=["leftOnlyNS", "leftStraightNS", "straightOnlyNS", "rightStraightNS", "rightOnlyNS", "allNS",
                                   "leftOnlyWE", "leftStraightWE", "straightOnlyWE", "rightStraightWE", "rightOnlyWE", "allWE",
                                   "moveDurationNS", "moveDurationWE", "yellowDurationNS", "yellowDurationWE",
                                   "turnDurationNS", "turnDurationWE", "demandN", "demandS", "demandW", "demandE",
                                   "demandProbNS_Straight", "demandProbNS_Left", "demandProbNS_Right",
                                   "demandProbNS_UTurn", "demandProbWE_Straight", "demandProbWE_Left", "demandProbWE_Right",
                                   "demandProbWE_UTurn", "outSpeedNS", "outSpeedWE", "inSpeedNS", "inSpeedWE", "vehicleMaxSpeed",
                                   "vehicleMinAccel", "vehicleMaxAccel", "vehicleMinDecel", "vehicleMaxDecel", "vehicleMinLength",
                                   "vehicleMaxLength", "minGap"])
    if dataframe.empty:
        dataframe.to_csv(csv_path)


def main(csv_path, folder_name, time_steps,
        leftOnlyNS=1, leftStraightNS=1, straightOnlyNS=1, rightStraightNS=1, rightOnlyNS=0, allNS=0,
        leftOnlyWE=1, leftStraightWE=1, straightOnlyWE=1, rightStraightWE=1, rightOnlyWE=0, allWE=0,
        leftOutLanesNS=2, rightOutLanesNS=2, leftOutLanesWE=2, rightOutLanesWE=2,
        moveDurationNS=60, moveDurationWE=60,
        yellowDurationNS=5, yellowDurationWE=5,
        turnDurationNS=20, turnDurationWE=20,
        demandN=0.20, demandS=0.20, demandW=0.20, demandE=0.20,
        demandProbNS=None, demandProbWE=None,
        outSpeedNS=19.0, outSpeedWE=19.0, inSpeedNS=11.0, inSpeedWE=11.0,
        vehicleMaxSpeed=25.0, vehicleMinAccel=0.8, vehicleMaxAccel=0.8, vehicleMinDecel=4.5,
        vehicleMaxDecel=4.5, vehicleMinLength=5, vehicleMaxLength=5, minGap=2.5):

    if demandProbNS is None:
        # left, straight, right, uturn
        demandProbNS = [1, 1, 1, 1]
    if demandProbWE is None:
        # left, straight, right, uturn
        demandProbWE = [1, 1, 1, 1]

    if straightOnlyNS != 0 and allNS != 0:
        allNS = 0
    if straightOnlyWE != 0 and allWE != 0:
        allWE = 0

    lanesNS = leftOnlyNS + leftStraightNS + straightOnlyNS + rightStraightNS + rightOnlyNS + allNS
    lanesWE = leftOnlyWE + leftStraightWE + straightOnlyWE + rightStraightWE + rightOnlyWE + allWE

    if lanesNS == 0 or lanesWE == 0:
        return None

    if leftOutLanesNS > lanesWE:
        leftOutLanesNS = lanesWE
    if rightOutLanesNS > lanesWE:
        rightOutLanesNS = lanesWE
    if leftOutLanesWE > lanesNS:
        leftOutLanesWE = lanesNS
    if rightOutLanesWE > lanesNS:
        rightOutLanesWE = lanesNS

    if leftOnlyNS + leftStraightNS + allNS == 0:
        demandProbNS[0] = 0
        demandProbNS[3] = 0
    if rightOnlyNS + rightStraightNS + allNS == 0:
        demandProbNS[2] = 0
    if leftStraightNS + rightStraightNS + straightOnlyNS + allNS == 0:
        demandProbNS[1] = 0
    if leftOnlyWE + leftStraightWE + allWE == 0:
        demandProbWE[0] = 0
        demandProbWE[3] = 0
    if rightOnlyWE + rightStraightWE + allWE == 0:
        demandProbWE[2] = 0
    if leftStraightWE + rightStraightWE + straightOnlyWE + allWE == 0:
        demandProbWE[1] = 0

    setDuration(folder_name, leftOnlyNS, leftStraightNS, straightOnlyNS, rightStraightNS, rightOnlyNS, allNS,
                leftOnlyWE, leftStraightWE, straightOnlyWE, rightStraightWE, rightOnlyWE, allWE,
                leftOutLanesNS, rightOutLanesNS, leftOutLanesWE, rightOutLanesWE,
                moveDurationNS, moveDurationWE, yellowDurationNS, yellowDurationWE, turnDurationNS, turnDurationWE)
    buildConnections(folder_name, leftOnlyNS, leftStraightNS, straightOnlyNS, rightStraightNS, rightOnlyNS, allNS,
                     leftOnlyWE, leftStraightWE, straightOnlyWE, rightStraightWE, rightOnlyWE, allWE,
                     leftOutLanesNS, rightOutLanesNS, leftOutLanesWE, rightOutLanesWE)
    createNetwork(folder_name, leftOnlyNS, leftStraightNS, straightOnlyNS, rightStraightNS, rightOnlyNS, allNS,
                  leftOnlyWE, leftStraightWE, straightOnlyWE, rightStraightWE, rightOnlyWE, allWE,
                  outSpeedNS, inSpeedNS, outSpeedWE, inSpeedWE)
    generateRoute(folder_name, leftOnlyNS, leftStraightNS, straightOnlyNS, rightStraightNS, rightOnlyNS, allNS,
                  leftOnlyWE, leftStraightWE, straightOnlyWE, rightStraightWE, rightOnlyWE, allWE,
                  time_steps, demandN, demandS, demandW, demandE, vehicleMinAccel, vehicleMaxAccel,
                  vehicleMinDecel, vehicleMaxDecel, vehicleMinLength, vehicleMaxLength, minGap,
                  vehicleMaxSpeed, demandProbNS, demandProbWE)
    traci.start([checkBinary('sumo'), "-c", str(folder_name) + "/cross.sumocfg",
             "--tripinfo-output", str(folder_name) + "/tripinfo.xml", "--statistic-output", "statistics.xml", "--tripinfo-output.write-unfinished"])
    runSim(time_steps)
    rates = findRate(str(folder_name) + "/tripinfo.xml")
    print(rates)

    dataframe = pd.DataFrame([[rates]])
    dataframe.to_csv(csv_path, mode='a', header=False)

def fixIndex(csv_path):
    dataframe = pd.read_csv(csv_path, index_col=0)
    dataframe = dataframe.reset_index(drop=True)
    dataframe.to_csv(csv_path)

if __name__ == "__main__":
    for i in range(1):
        start_time = time.time()
        setup("record.csv")
        instance = mp.cpu_count()
        for p_num in range(instance):
            os.mkdir(r"C:\Users\Thomas Tseng\Documents\GitHub\Traffic-Light-Project\data%i" % (p_num))
            copy_tree(r"C:\Users\Thomas Tseng\Documents\GitHub\Traffic-Light-Project\data", r"C:\Users\Thomas Tseng\Documents\GitHub\Traffic-Light-Project\data%i" % (p_num))
        processes = []
        for p_num in range(instance):
            p = mp.Process(target=main, args=("record.csv", "data" + str(p_num), 3000, 0, 0, random.randint(50, 100), 0, 0, 0, 0, 0, random.randint(50, 100), 0, 0, 0, 2, 2, 2, 2, 3000, 0, 0, 0, 0, 0, 0, 0.0005, 0, 0))
            p.start()
            processes.append(p)
        for process in processes:
            process.join()
        fixIndex("record.csv")
        for p_num in range(instance):
            shutil.rmtree(r"C:\Users\Thomas Tseng\Documents\GitHub\Traffic-Light-Project\data%i" % (p_num))
        print("")
        print("Instance: " + str(instance))
        print("Time: " + str(time.time() - start_time) + "s")

    # main(time_steps=3000, csv_path="record.csv", folder_name="data")
