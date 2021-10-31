from __future__ import absolute_import
from __future__ import print_function
from bs4 import BeautifulSoup
from sumolib import checkBinary
from random import randint, uniform, randrange
from email.utils import formataddr
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import traceback
import traci
import pandas as pd
import os
import sys
import psutil
import xml.etree.ElementTree as ET
import random
import multiprocessing as mp
import datetime
import time
import math
import smtplib

# we need to import python modules from the $SUMO_HOME/tools directory
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

def adjustNodes(folder_name, lengthN, lengthS, lengthW, lengthE):
    tree = ET.parse(str(folder_name) + "/cross.nod.xml")

    tl = tree.find(".//node[@id='juncN']")
    tl.set("y", "+" + str(lengthN))

    tl = tree.find(".//node[@id='juncS']")
    tl.set("y", "-" + str(lengthS))

    tl = tree.find(".//node[@id='juncW']")
    tl.set("x", "-" + str(lengthW))

    tl = tree.find(".//node[@id='juncE']")
    tl.set("x", "+" + str(lengthE))

    tree.write(str(folder_name) + "/cross.nod.xml")

def generateRoute(folder_name, time_steps, leftOnlyNS, leftStraightNS, straightOnlyNS, rightStraightNS, rightOnlyNS, allNS,
                  leftOnlyWE, leftStraightWE, straightOnlyWE, rightStraightWE, rightOnlyWE, allWE,
                  lengthN, lengthS, lengthW, lengthE,
                  demandN, demandS, demandW, demandE,
                  minAccel, maxAccel, minDecel, maxDecel,
                  minLength, maxLength, minGap, maxSpeed, demandProbNS, demandProbWE,
                  pDemandRegN, pDemandRegS, pDemandRegW, pDemandRegE, pDemandOppN, pDemandOppS, pDemandOppW, pDemandOppE,
                  pSpeedRegN, pSpeedRegS, pSpeedRegW, pSpeedRegE, pSpeedOppN, pSpeedOppS, pSpeedOppW, pSpeedOppE):
    lanesNS = leftOnlyNS + leftStraightNS + straightOnlyNS + rightStraightNS + rightOnlyNS + allNS + 1
    lanesWE = leftOnlyWE + leftStraightWE + straightOnlyWE + rightStraightWE + rightOnlyWE + allWE + 1
    random.seed(42)

    with open(str(folder_name) + "/cross.rou.xml", "w") as routes:
        print("""<routes>""", file=routes)
        print("""   <personFlow id="pRegN" begin="0" end="%i" personsPerHour="%f">
        <walk edges="edgeN_O edgeS_I" speed="%f"/>
    </personFlow>""" % (time_steps, pDemandRegN * 3600, pSpeedRegN), file=routes)
        print("""   <personFlow id="pRegS" begin="0" end="%i" personsPerHour="%f">
        <walk edges="edgeS_O edgeN_I" speed="%f"/>
    </personFlow>""" % (time_steps, pDemandRegS * 3600, pSpeedRegS), file=routes)
        print("""   <personFlow id="pRegW" begin="0" end="%i" personsPerHour="%f">
        <walk edges="edgeW_O edgeE_I" speed="%f"/>
    </personFlow>""" % (time_steps, pDemandRegW * 3600, pSpeedRegW), file=routes)
        print("""   <personFlow id="pRegE" begin="0" end="%i" personsPerHour="%f">
        <walk edges="edgeE_O edgeW_I" speed="%f"/>
    </personFlow>""" % (time_steps, pDemandRegE * 3600, pSpeedRegE), file=routes)
        print("""   <personFlow id="pOppN" begin="0" end="%i" personsPerHour="%f" departPos="%f">
        <walk edges="edgeN_I edgeS_O" speed="%f"/>
    </personFlow>""" % (time_steps, pDemandOppN * 3600, lengthN, pSpeedOppN), file=routes)
        print("""   <personFlow id="pOppS" begin="0" end="%i" personsPerHour="%f" departPos="%f">
        <walk edges="edgeS_I edgeN_O" speed="%f"/>
    </personFlow>""" % (time_steps, pDemandOppS * 3600, lengthS, pSpeedOppS), file=routes)
        print("""   <personFlow id="pOppW" begin="0" end="%i" personsPerHour="%f" departPos="%f">
        <walk edges="edgeW_I edgeE_O" speed="%f"/>
    </personFlow>""" % (time_steps, pDemandOppW * 3600, lengthW, pSpeedOppW), file=routes)
        print("""   <personFlow id="pOppE" begin="0" end="%i" personsPerHour="%f" departPos="%f">
        <walk edges="edgeE_I edgeW_O" speed="%f"/>
    </personFlow>""" % (time_steps, pDemandOppE * 3600, lengthE, pSpeedOppE), file=routes)

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
        for i in range(time_steps):
            for demand in range(math.floor(demandN)):
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
            if random.uniform(0, 1) < demandN - math.floor(demandN):
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
            for demand in range(math.floor(demandS)):
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
            if random.uniform(0, 1) < demandS - math.floor(demandS):
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
            for demand in range(math.floor(demandW)):
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
            if random.uniform(0, 1) < demandW - math.floor(demandW):
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
            for demand in range(math.floor(demandE)):
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
            if random.uniform(0, 1) < demandE - math.floor(demandE):
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
                moveNS, moveWE, yellowNS, yellowWE, turnNS, turnWE, waitNS, waitWE,
                pDemandRegN, pDemandRegS, pDemandRegW, pDemandRegE, pDemandOppN, pDemandOppS, pDemandOppW, pDemandOppE):

    lanesNS = leftOnlyNS + leftStraightNS + straightOnlyNS + rightStraightNS + rightOnlyNS + allNS + 1
    lanesWE = leftOnlyWE + leftStraightWE + straightOnlyWE + rightStraightWE + rightOnlyWE + allWE + 1

    status = []
    for state in range(8):
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
                    for i in range(leftOutLanesWE):
                        temp_string += "r"
                if leftOnlyWE + leftStraightWE + allWE > 0:
                    temp_string += "r"
            temp_string += "rGrG"
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
        elif state == 6:
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
                    for i in range(leftOutLanesWE):
                        temp_string += "r"
                if leftOnlyWE + leftStraightWE + allWE > 0:
                    temp_string += "r"
            temp_string += "GrGr"
            status.append(temp_string)
        elif state == 7:
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
        if waitNS != 0 and (pDemandRegN > 0 or pDemandOppN > 0 or pDemandRegS > 0 or pDemandOppS > 0):
            print("""       <phase duration="%f" state="%s"/>""" % (waitNS, status[2]), file=tls)
        if turnWE != 0 and leftOnlyWE != 0:
            print("""       <phase duration="%f" state="%s"/>""" % (turnWE, status[3]), file=tls)
        if moveWE != 0 and lanesWE != 0:
            print("""       <phase duration="%f" state="%s"/>""" % (moveWE, status[4]), file=tls)
        if yellowWE != 0 and lanesWE != 0:
            print("""       <phase duration="%f" state="%s"/>""" % (yellowWE, status[5]), file=tls)
        if waitWE != 0 and (pDemandRegW > 0 or pDemandOppW > 0 or pDemandRegE > 0 or pDemandOppE > 0):
            print("""       <phase duration="%f" state="%s"/>""" % (waitWE, status[6]), file=tls)
        if turnNS != 0 and leftOnlyNS != 0:
            print("""       <phase duration="%f" state="%s"/>""" % (turnNS, status[7]), file=tls)
        print("""   </tlLogic>""", file=tls)
        print("</additional>", file=tls)

def buildConnections(folder_name, leftOnlyNS, leftStraightNS, straightOnlyNS, rightStraightNS, rightOnlyNS, allNS,
                     leftOnlyWE, leftStraightWE, straightOnlyWE, rightStraightWE, rightOnlyWE, allWE,
                     leftOutLanesNS, rightOutLanesNS, leftOutLanesWE, rightOutLanesWE):

    lanesNS = leftOnlyNS + leftStraightNS + straightOnlyNS + rightStraightNS + rightOnlyNS + allNS + 1
    lanesWE = leftOnlyWE + leftStraightWE + straightOnlyWE + rightStraightWE + rightOnlyWE + allWE + 1

    with open(str(folder_name) + "/cross.con.xml", "w") as connections:
        print("""<connections>""", file=connections)
        print("""   <crossing width="4.50" edges="edgeN_I edgeN_O" node="juncMain" priority="1"/>
    <crossing width="4.50" edges="edgeE_I edgeE_O" node="juncMain" priority="1"/>
    <crossing width="4.50" edges="edgeS_I edgeS_O" node="juncMain" priority="1"/>
    <crossing width="4.50" edges="edgeW_I edgeW_O" node="juncMain" priority="1"/>""", file=connections)
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
    traci.simulationStep(time_steps)
    traci.close()
    sys.stdout.flush()

def findRate(data):
    with open(data, "r", encoding="utf-8") as file:
        content = file.readlines()
        content = "".join(content)
        soup = BeautifulSoup(content, "lxml")
    all_trips = soup.findAll("tripinfo")
    total = 0
    total_trips = len(all_trips)
    for trip in all_trips:
        duration = float(trip["duration"])
        loss = float(trip["timeloss"])
        total += ((duration - loss) / duration)
    all_trips = soup.findAll("walk")
    total_trips += len(all_trips)
    for trip in all_trips:
        duration = float(trip["duration"])
        loss = float(trip["timeloss"])
        total += ((duration - loss) / duration)
    return total / total_trips

def setup(csv_path):
    dataframe = pd.read_csv(csv_path, sep='\t',
                            names=["rates", "leftOnlyNS", "leftStraightNS", "straightOnlyNS", "rightStraightNS", "rightOnlyNS", "allNS",
                            "leftOnlyWE", "leftStraightWE", "straightOnlyWE", "rightStraightWE", "rightOnlyWE", "allWE",
                            "leftOutLanesNS", "rightOutLanesNS", "leftOutLanesWE", "rightOutLanesWE",
                            "moveDurationNS", "moveDurationWE",
                            "yellowDurationNS", "yellowDurationWE",
                            "turnDurationNS", "turnDurationWE",
                            "waitDurationNS", "waitDurationWE",
                            "lengthN", "lengthS", "lengthW", "lengthE",
                            "demandN", "demandS", "demandW", "demandE",
                            "demandProbNS_Straight", "demandProbNS_Left", "demandProbNS_Right", "demandProbNS_UTurn",
                            "demandProbWE_Straight", "demandProbWE_Left", "demandProbWE_Right", "demandProbWE_UTurn",
                            "pDemandRegN", "pDemandRegS", "pDemandRegW", "pDemandRegE",
                            "pDemandOppN", "pDemandOppS", "pDemandOppW", "pDemandOppE",
                            "pSpeedRegN", "pSpeedRegS", "pSpeedRegW", "pSpeedRegE",
                            "pSpeedOppN", "pSpeedOppS", "pSpeedOppW", "pSpeedOppE",
                            "outSpeedNS", "outSpeedWE", "inSpeedNS", "inSpeedWE",
                            "vehicleMaxSpeed", "vehicleMinAccel", "vehicleMaxAccel", "vehicleMinDecel",
                            "vehicleMaxDecel", "vehicleMinLength", "vehicleMaxLength", "minGap"])
    if dataframe.empty:
        dataframe.to_csv(csv_path)

def main(csv_path, folder_name, time_steps,
        leftOnlyNS=0, leftStraightNS=1, straightOnlyNS=1, rightStraightNS=1, rightOnlyNS=0, allNS=0,
        leftOnlyWE=0, leftStraightWE=1, straightOnlyWE=1, rightStraightWE=1, rightOnlyWE=0, allWE=0,
        leftOutLanesNS=2, rightOutLanesNS=2, leftOutLanesWE=2, rightOutLanesWE=2,
        moveDurationNS=60.0, moveDurationWE=60.0,
        yellowDurationNS=5.0, yellowDurationWE=5.0,
        turnDurationNS=20.0, turnDurationWE=20.0,
        waitDurationNS=10.0, waitDurationWE=10.0,
        lengthN=500, lengthS=500, lengthW=500, lengthE=500,
        demandN=0.20, demandS=0.20, demandW=0.20, demandE=0.20,
        demandProbNS=None, demandProbWE=None,
        pDemandRegN=0.1, pDemandRegS=0.1, pDemandRegW=0.1, pDemandRegE=0.1,
        pDemandOppN=0.1, pDemandOppS=0.1, pDemandOppW=0.1, pDemandOppE=0.1,
        pSpeedRegN=1.0, pSpeedRegS=1.0, pSpeedRegW=1.0, pSpeedRegE=1.0,
        pSpeedOppN=1.0, pSpeedOppS=1.0, pSpeedOppW=1.0, pSpeedOppE=1.0,
        outSpeedNS=19.0, outSpeedWE=19.0, inSpeedNS=11.0, inSpeedWE=11.0,
        vehicleMaxSpeed=25.0, vehicleMinAccel=0.8, vehicleMaxAccel=0.8, vehicleMinDecel=4.5,
        vehicleMaxDecel=4.5, vehicleMinLength=5.0, vehicleMaxLength=5.0, minGap=2.5):

    if lengthN <= 50:
        lengthN = 50
    if lengthS <= 50:
        lengthS = 50
    if lengthW <= 50:
        lengthW = 50
    if lengthE <= 50:
        lengthE = 50

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

    if lanesNS == 0 or lanesWE == 0 or lanesNS > 20 or lanesWE > 20:
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

    adjustNodes(folder_name, lengthN, lengthS, lengthW, lengthE)
    setDuration(folder_name, leftOnlyNS, leftStraightNS, straightOnlyNS, rightStraightNS, rightOnlyNS, allNS,
                leftOnlyWE, leftStraightWE, straightOnlyWE, rightStraightWE, rightOnlyWE, allWE,
                leftOutLanesNS, rightOutLanesNS, leftOutLanesWE, rightOutLanesWE,
                moveDurationNS, moveDurationWE, yellowDurationNS, yellowDurationWE,
                turnDurationNS, turnDurationWE, waitDurationNS, waitDurationWE,
                pDemandRegN, pDemandRegS, pDemandRegW, pDemandRegE,
                pDemandOppN, pDemandOppS, pDemandOppW, pDemandOppE)
    buildConnections(folder_name, leftOnlyNS, leftStraightNS, straightOnlyNS, rightStraightNS, rightOnlyNS, allNS,
                     leftOnlyWE, leftStraightWE, straightOnlyWE, rightStraightWE, rightOnlyWE, allWE,
                     leftOutLanesNS, rightOutLanesNS, leftOutLanesWE, rightOutLanesWE)
    createNetwork(folder_name, leftOnlyNS, leftStraightNS, straightOnlyNS, rightStraightNS, rightOnlyNS, allNS,
                  leftOnlyWE, leftStraightWE, straightOnlyWE, rightStraightWE, rightOnlyWE, allWE,
                  outSpeedNS, inSpeedNS, outSpeedWE, inSpeedWE)
    generateRoute(folder_name, time_steps, leftOnlyNS, leftStraightNS, straightOnlyNS, rightStraightNS, rightOnlyNS, allNS,
                  leftOnlyWE, leftStraightWE, straightOnlyWE, rightStraightWE, rightOnlyWE, allWE,
                  lengthN, lengthS, lengthW, lengthE, demandN, demandS, demandW, demandE, vehicleMinAccel, vehicleMaxAccel,
                  vehicleMinDecel, vehicleMaxDecel, vehicleMinLength, vehicleMaxLength, minGap,
                  vehicleMaxSpeed, demandProbNS, demandProbWE, pDemandRegN, pDemandRegS, pDemandRegW, pDemandRegE,
                  pDemandOppN, pDemandOppS, pDemandOppW, pDemandOppE, pSpeedRegN, pSpeedRegS, pSpeedRegW, pSpeedRegE,
                  pSpeedOppN, pSpeedOppS, pSpeedOppW, pSpeedOppE)

    traci.start([checkBinary('sumo-gui'), "-c", str(folder_name) + "/cross.sumocfg",
             "--tripinfo-output", str(folder_name) + "/tripinfo.xml", "--tripinfo-output.write-unfinished", "--no-warnings", "--quit-on-end"])
    runSim(time_steps)
    rates = findRate(str(folder_name) + "/tripinfo.xml")
    dataframe = pd.DataFrame([[rates, leftOnlyNS, leftStraightNS, straightOnlyNS, rightStraightNS, rightOnlyNS, allNS,
            leftOnlyWE, leftStraightWE, straightOnlyWE, rightStraightWE, rightOnlyWE, allWE,
            leftOutLanesNS, rightOutLanesNS, leftOutLanesWE, rightOutLanesWE,
            moveDurationNS, moveDurationWE,
            yellowDurationNS, yellowDurationWE,
            turnDurationNS, turnDurationWE,
            waitDurationNS, waitDurationWE,
            lengthN, lengthS, lengthW, lengthE,
            demandN, demandS, demandW, demandE,
            demandProbNS[1], demandProbNS[0], demandProbNS[2], demandProbNS[3],
            demandProbWE[1], demandProbWE[0], demandProbWE[2], demandProbWE[3],
            pDemandRegN, pDemandRegS, pDemandRegW, pDemandRegE,
            pDemandOppN, pDemandOppS, pDemandOppW, pDemandOppE,
            pSpeedRegN, pSpeedRegS, pSpeedRegW, pSpeedRegE,
            pSpeedOppN, pSpeedOppS, pSpeedOppW, pSpeedOppE,
            outSpeedNS, outSpeedWE, inSpeedNS, inSpeedWE,
            vehicleMaxSpeed, vehicleMinAccel, vehicleMaxAccel, vehicleMinDecel,
            vehicleMaxDecel, vehicleMinLength, vehicleMaxLength, minGap]])
    dataframe.to_csv(csv_path, mode='a', header=False, index=True)

def fixIndex(csv_path):
    dataframe = pd.read_csv(csv_path, index_col=0)
    dataframe = dataframe.reset_index(drop=True)
    dataframe.to_csv(csv_path)

def execute():
    leftOnlyNS = randint(0, 1)
    leftStraightNS = randint(0, 1)
    straightOnlyNS = randint(0, 3)
    rightStraightNS = randint(0, 1)
    rightOnlyNS = randint(0, 1)
    allNS = randint(0, 1)
    leftOnlyWE = randint(0, 1)
    leftStraightWE = randint(0, 1)
    straightOnlyWE = randint(0, 3)
    rightStraightWE = randint(0, 1)
    rightOnlyWE = randint(0, 1)
    allWE = randint(0, 1)
    leftOutLanesNS = randint(1, 2)
    rightOutLanesNS = randint(1, 2)
    leftOutLanesWE = randint(1, 2)
    rightOutLanesWE = randint(1, 2)
    moveDurationNS = uniform(15, 120)
    moveDurationWE = uniform(15, 120)
    yellowDurationNS = uniform(3, 6)
    yellowDurationWE = uniform(3, 6)
    turnDurationNS = uniform(10, 40)
    turnDurationWE = uniform(10, 40)
    waitDurationNS = uniform(3, 15)
    waitDurationWE = uniform(3, 15)
    lengthN = randrange(300, 1001, 100)
    lengthS = randrange(300, 1001, 100)
    lengthW = randrange(300, 1001, 100)
    lengthE = randrange(300, 1001, 100)
    lanesNS = leftOnlyNS + leftStraightNS + straightOnlyNS + rightStraightNS + rightOnlyNS + allNS
    lanesWE = leftOnlyWE + leftStraightWE + straightOnlyWE + rightStraightWE + rightOnlyWE + allWE
    if lanesNS <= 2 and leftOnlyNS + leftStraightNS + allNS == 0:
        demandN = uniform(0.01, 0.15)
        demandS = uniform(0.01, 0.15)
    elif lanesNS <= 2:
        demandN = uniform(0.15, 0.3)
        demandS = uniform(0.15, 0.3)
    elif lanesNS <= 4:
        demandN = uniform(0.15, 0.45)
        demandS = uniform(0.15, 0.45)
    else:
        demandN = uniform(0.15, 0.6)
        demandS = uniform(0.15, 0.6)
    if lanesWE <= 2 and leftOnlyWE + leftStraightWE + allWE == 0:
        demandW = uniform(0.01, 0.15)
        demandE = uniform(0.01, 0.15)
    elif lanesWE <= 2:
        demandW = uniform(0.15, 0.3)
        demandE = uniform(0.15, 0.3)
    elif lanesWE <= 4:
        demandW = uniform(0.15, 0.45)
        demandE = uniform(0.15, 0.45)
    else:
        demandW = uniform(0.15, 0.6)
        demandE = uniform(0.15, 0.6)
    demandProbNS = [0, 0, 0, 0]
    demandProbNS[0] = uniform(0, 0.3)
    demandProbNS[2] = uniform(0, 0.3)
    demandProbNS[3] = uniform(0, 0.1)
    demandProbNS[1] = 1 - demandProbNS[0] - demandProbNS[2] - demandProbNS[3]
    demandProbWE = [0, 0, 0, 0]
    demandProbWE[0] = uniform(0, 0.3)
    demandProbWE[2] = uniform(0, 0.3)
    demandProbWE[3] = uniform(0, 0.1)
    demandProbWE[1] = 1 - demandProbWE[0] - demandProbWE[2] - demandProbWE[3]
    pDemandRegN = uniform(0.01, 0.3)
    pDemandRegS = uniform(0.01, 0.3)
    pDemandRegW = uniform(0.01, 0.3)
    pDemandRegE = uniform(0.01, 0.3)
    pDemandOppN = uniform(0.01, 0.3)
    pDemandOppS = uniform(0.01, 0.3)
    pDemandOppW = uniform(0.01, 0.3)
    pDemandOppE = uniform(0.01, 0.3)
    pSpeedRegN = uniform(0.89, 2.24)
    pSpeedRegS = uniform(0.89, 2.24)
    pSpeedRegW = uniform(0.89, 2.24)
    pSpeedRegE = uniform(0.89, 2.24)
    pSpeedOppN = uniform(0.89, 2.24)
    pSpeedOppS = uniform(0.89, 2.24)
    pSpeedOppW = uniform(0.89, 2.24)
    pSpeedOppE = uniform(0.89, 2.24)
    outSpeedNS = uniform(11.2, 26.8)
    outSpeedWE = uniform(11.2, 26.8)
    inSpeedNS = uniform(11.2, 26.8)
    inSpeedWE = uniform(11.2, 26.8)
    vehicleMaxSpeed = uniform(120, 150)
    vehicleMinAccel = uniform(2, 2.5)
    vehicleMaxAccel = uniform(3.5, 4)
    vehicleMinDecel = uniform(2.5, 3.5)
    vehicleMaxDecel = uniform(5.5, 7)
    vehicleMinLength = uniform(3.8, 4.0)
    vehicleMaxLength = uniform(5.5, 5.7)
    minGap = uniform(2.3, 2.7)
    main("record.csv", "data", 3000, leftOnlyNS, leftStraightNS, straightOnlyNS, rightStraightNS, rightOnlyNS, allNS,
        leftOnlyWE, leftStraightWE, straightOnlyWE, rightStraightWE, rightOnlyWE, allWE,
        leftOutLanesNS, rightOutLanesNS, leftOutLanesWE, rightOutLanesWE,
        moveDurationNS, moveDurationWE,
        yellowDurationNS, yellowDurationWE,
        turnDurationNS, turnDurationWE,
        waitDurationNS, waitDurationWE,
        lengthN, lengthS, lengthW, lengthE,
        demandN, demandS, demandW, demandE,
        demandProbNS, demandProbWE,
        pDemandRegN, pDemandRegS, pDemandRegW, pDemandRegE,
        pDemandOppN, pDemandOppS, pDemandOppW, pDemandOppE,
        pSpeedRegN, pSpeedRegS, pSpeedRegW, pSpeedRegE,
        pSpeedOppN, pSpeedOppS, pSpeedOppW, pSpeedOppE,
        outSpeedNS, outSpeedWE, inSpeedNS, inSpeedWE,
        vehicleMaxSpeed, vehicleMinAccel, vehicleMaxAccel, vehicleMinDecel,
        vehicleMaxDecel, vehicleMinLength, vehicleMaxLength, minGap)

def kill_proc_tree(pid):
    parent = psutil.Process(pid)
    children = parent.children(recursive=True)
    for child in children:
        child.kill()

if __name__ == "__main__":
    process_name = str(randint(0, 9)) + str(randint(0, 9)) + str(randint(0, 9)) + str(randint(0, 9))
    setup("record.csv")
    cycle_length = 30 * 60
    total_run_time = 0
    total_records = 0
    total_errors = 0
    num_days = 1

    from_email = "thomasprogramtest2021@gmail.com"
    from_password = "thomastseng0830"
    to_email = "0830thomastseng@gmail.com"

    subject = "Process " + str(process_name) + " Has Begun Running"
    text = ""
    html = f"""
            <html>
                <head>
                    <meta charset="UTF-8">
                </head>
                <body style="">
                    <p>Process {str(process_name)} has successfully started! Reports will be sent at around {str(datetime.datetime.now().time())} each day.</p>
                </body>
            </html>
            """

    # try:
    #     message = MIMEMultipart("alternative")
    #     message["Subject"] = subject
    #     message["From"] = formataddr((str(Header('SUMO Simulation', 'utf-8')), from_email))
    #     message["To"] = to_email
    #
    #     part1 = MIMEText(text, "plain")
    #     part2 = MIMEText(html, "html")
    #
    #     message.attach(part1)
    #     message.attach(part2)
    #
    #     server = smtplib.SMTP("smtp.gmail.com", 587)
    #     server.starttls()
    #     server.login(from_email, from_password)
    #     server.sendmail(from_email, to_email, message.as_string())
    #     server.quit()
    # except Exception:
    #     traceback.print_exc()

    while True:
        try:
            set_time = time.time()
            daily_records = 0
            daily_errors = 0
            while time.time() - set_time < cycle_length:
                pid = os.getpid()
                try:
                    pool = mp.Pool(processes=1)
                    result = pool.apply_async(execute, args=())
                    result.get(timeout=300)
                    pool.close()
                    pool.join()
                    total_records += 1
                    daily_records += 1
                except Exception as e:
                    traceback.print_exc()
                    kill_proc_tree(pid)
                    total_errors += 1
                    daily_errors += 1
            fixIndex("record.csv")

            current_time = datetime.datetime.now()
            total_daily_time = time.time() - set_time
            total_run_time += total_daily_time
            formatted_run_time = datetime.timedelta(seconds=total_run_time)
            formatted_daily_time = datetime.timedelta(seconds=total_daily_time)

            if total_records == 0:
                average_run_time = "NaN"
                inverse_average_run_time = "NaN"
            else:
                average_run_time = total_run_time / total_records
            if daily_records == 0:
                average_daily_time = "NaN"
            else:
                average_daily_time = total_daily_time / daily_records
            if total_run_time == 0:
                inverse_average_run_time = "NaN"
                average_daily_records = "NaN"
                average_hourly_records = "NaN"
            else:
                inverse_average_run_time = total_records / total_run_time
                average_daily_records = total_records / (total_run_time / 86400)
                average_hourly_records = total_records / (total_run_time / 3600)
            if total_daily_time == 0:
                inverse_average_daily_time = "NaN"
            else:
                inverse_average_daily_time = daily_records / total_daily_time

            subject = "Process " + str(process_name) + " Report: Day " + str(num_days)
            text = ""
            html = f"""
                        <html>
                            <head>
                                <meta charset="UTF-8">
                            </head>
                            <body style="">
                                <h4>The following text is a report of the progress of Process {process_name}. The next report should be sent at around {str(datetime.datetime.now().time())} tomorrow.:</h4>
                                <p>Current Time: {str(current_time)}</p>
                                <p>Total Days: {str(num_days)} Days</p>
                                <p>Total Run Time: {str(formatted_run_time)}</p>
                                <p>Total Records: {str(total_records)} Records</p>
                                <p>Total Errors: {str(total_errors)} Errors</p>
                                <p>Day {str(num_days)} Run Time: {str(formatted_daily_time)}</p>
                                <p>Day {str(num_days)} Records: {str(daily_records)} Records</p>
                                <p>Day {str(num_days)} Errors: {str(daily_errors)} Errors</p>
                                <p>Average Rate: {str(average_run_time)} Seconds/Record</p>
                                <p>Day {str(num_days)} Rate: {str(average_daily_time)} Seconds/Record</p>
                                <p>Inverse Average Rate: {str(inverse_average_run_time)} Records/Second</p>
                                <p>Inverse Day {str(num_days)} Rate: {str(inverse_average_daily_time)} Records/Second</p>
                                <p>Daily Rate: {str(average_daily_records)} Records/Day</p>
                                <p>Hourly Rate: {str(average_hourly_records)} Records/Hour</p>
                            </body>
                        </html>
                        """

            num_days += 1

            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = formataddr((str(Header('SUMO Simulation', 'utf-8')), from_email))
            message["To"] = to_email

            part1 = MIMEText(text, "plain")
            part2 = MIMEText(html, "html")

            message.attach(part1)
            message.attach(part2)

            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(from_email, from_password)
            server.sendmail(from_email, to_email, message.as_string())
            server.quit()
            traceback.print_exc()

        except:
            traceback.print_exc()
    # fixIndex("record.csv")
    # main("record.csv", "data", 3000)
