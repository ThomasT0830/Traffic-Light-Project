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
import time
import csv

# we need to import python modules from the $SUMO_HOME/tools directory
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

def generateRoute(leftOnlyNS, leftStraightNS, straightOnlyNS, rightStraightNS, rightOnlyNS, allNS,
                  leftOnlyWE, leftStraightWE, straightOnlyWE, rightStraightWE, rightOnlyWE, allWE,
                  steps, demandN, demandS, demandW, demandE, accel, decel, minLength, maxLength,
                  minGap, maxSpeed, demandProbNS, demandProbWE):
    lanesNS = leftOnlyNS + leftStraightNS + straightOnlyNS + rightStraightNS + rightOnlyNS + allNS
    lanesWE = leftOnlyWE + leftStraightWE + straightOnlyWE + rightStraightWE + rightOnlyWE + allWE
    random.seed(42)  # make tests reproducible
    vtypes = []
    # demand per second from different directions
    chanceNS = []
    chanceWE = []
    draw_count = 0
    for draw in demandProbNS:
        for i in range(draw):
            if draw_count == 0:
                chanceNS.append("left")
            elif draw_count == 1:
                chanceNS.append("straight")
            elif draw_count == 2:
                chanceNS.append("right")
            else:
                chanceNS.append("uturn")
        draw_count += 1
    draw_count = 0
    for draw in demandProbWE:
        for i in range(draw):
            if draw_count == 0:
                chanceWE.append("left")
            elif draw_count == 1:
                chanceWE.append("straight")
            elif draw_count == 2:
                chanceWE.append("right")
            else:
                chanceWE.append("uturn")
        draw_count += 1
    with open("data/cross.rou.xml", "w") as routes:
        print("""<routes>""", file=routes)
        for length in range(minLength, maxLength + 1):
            print("""
    <vType id="length_%s" length="%i" accel="%f" decel="%f" sigma="0.5" minGap="%f" maxSpeed="%f" guiShape="passenger" />"""
            % (str(length), length, accel, decel, minGap, maxSpeed), file=routes)
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
    <route id="edgeE_edgeE" edges="edgeE_O edgeE_I" />
    """, file=routes)
        vehicleCount = 0
        for i in range(steps):
            if random.uniform(0, 1) < demandN:
                direction = random.choice(chanceNS)
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
                direction = random.choice(chanceNS)
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
                direction = random.choice(chanceWE)
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
                    print('    <vehicle id="%sW_%i" type="%s" route="edgeW_edgeE" depart="%i" departLane="random" />' % (
                            direction, vehicleCount, vehicleType, i), file=routes)
                vehicleCount += 1
            if random.uniform(0, 1) < demandE:
                direction = random.choice(chanceWE)
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

def setDuration(leftOnlyNS, leftStraightNS, straightOnlyNS, rightStraightNS, rightOnlyNS, allNS,
                leftOnlyWE, leftStraightWE, straightOnlyWE, rightStraightWE, rightOnlyWE, allWE,
                moveNS, moveWE, yellowNS, yellowWE, turnNS, turnWE):
    status = []
    for state in range(6):
        temp_string = ""
        if state == 0:
            # North
            temp_string += "GG"
            for i in range(lanesNS):
                temp_string += "G"
            temp_string += "ggg"
            # East
            temp_string += "rr"
            for i in range(lanesWE):
                temp_string += "r"
            temp_string += "rrr"
            # South
            temp_string += "GG"
            for i in range(lanesNS):
                temp_string += "G"
            temp_string += "ggg"
            #West
            temp_string += "rr"
            for i in range(lanesWE):
                temp_string += "r"
            temp_string += "rrr"
        elif state == 1:
            # North
            temp_string += "yy"
            for i in range(lanesNS):
                temp_string += "y"
            temp_string += "yyy"
            # East
            temp_string += "rr"
            for i in range(lanesWE):
                temp_string += "r"
            temp_string += "rrr"
            # South
            temp_string += "yy"
            for i in range(lanesNS):
                temp_string += "y"
            temp_string += "yyy"
            # West
            temp_string += "rr"
            for i in range(lanesWE):
                temp_string += "r"
            temp_string += "rrr"
        elif state == 2:
            # North
            temp_string += "rr"
            for i in range(lanesNS):
                temp_string += "r"
            temp_string += "rrr"
            # East
            temp_string += "rr"
            for i in range(lanesWE):
                temp_string += "r"
            temp_string += "GGG"
            # South
            temp_string += "rr"
            for i in range(lanesNS):
                temp_string += "r"
            temp_string += "rrr"
            # West
            temp_string += "rr"
            for i in range(lanesWE):
                temp_string += "r"
            temp_string += "GGG"
        elif state == 3:
            # North
            temp_string += "rr"
            for i in range(lanesNS):
                temp_string += "r"
            temp_string += "rrr"
            # East
            temp_string += "GG"
            for i in range(lanesWE):
                temp_string += "G"
            temp_string += "ggg"
            # South
            temp_string += "rr"
            for i in range(lanesNS):
                temp_string += "r"
            temp_string += "rrr"
            # West
            temp_string += "GG"
            for i in range(lanesWE):
                temp_string += "G"
            temp_string += "ggg"
        elif state == 4:
            # North
            temp_string += "rr"
            for i in range(lanesNS):
                temp_string += "r"
            temp_string += "rrr"
            # East
            temp_string += "yy"
            for i in range(lanesWE):
                temp_string += "y"
            temp_string += "yyy"
            # South
            temp_string += "rr"
            for i in range(lanesNS):
                temp_string += "r"
            temp_string += "rrr"
            # West
            temp_string += "yy"
            for i in range(lanesWE):
                temp_string += "y"
            temp_string += "yyy"
        else:
            # North
            temp_string += "rr"
            for i in range(lanesNS):
                temp_string += "r"
            temp_string += "GGG"
            # East
            temp_string += "rr"
            for i in range(lanesWE):
                temp_string += "r"
            temp_string += "rrr"
            # South
            temp_string += "rr"
            for i in range(lanesNS):
                temp_string += "r"
            temp_string += "GGG"
            # West
            temp_string += "rr"
            for i in range(lanesWE):
                temp_string += "r"
            temp_string += "rrr"
        status.append(temp_string)

    with open("data/cross.tls.xml", "w") as tls:
        print("<additional>", file=tls)
        print("""   <tlLogic id="juncMain" type="static" programID="1" offset="0">""", file=tls)
        if moveNS != 0:
            print("""       <phase duration="%i" state="%s"/>""" % (moveNS, status[0]), file=tls)
        if yellowNS != 0:
            print("""       <phase duration="%i" state="%s"/>""" % (yellowNS, status[1]), file=tls)
        if turnWE != 0:
            print("""       <phase duration="%i" state="%s"/>""" % (turnWE, status[2]), file=tls)
        if moveWE != 0:
            print("""       <phase duration="%i" state="%s"/>""" % (moveWE, status[3]), file=tls)
        if yellowWE != 0:
            print("""       <phase duration="%i" state="%s"/>""" % (yellowWE, status[4]), file=tls)
        if turnNS != 0:
            print("""       <phase duration="%i" state="%s"/>""" % (turnNS, status[5]), file=tls)
        print("""   </tlLogic>""", file=tls)
        print("</additional>", file=tls)

def buildConnections(leftOnlyNS, leftStraightNS, straightOnlyNS, rightStraightNS, rightOnlyNS, allNS,
                     leftOnlyWE, leftStraightWE, straightOnlyWE, rightStraightWE, rightOnlyWE, allWE,
                     leftOutLanesNS, rightOutLanesNS, leftOutLanesWE, rightOutLanesWE):

    lanesNS = leftOnlyNS + leftStraightNS + straightOnlyNS + rightStraightNS + rightOnlyNS + allNS
    lanesWE = leftOnlyWE + leftStraightWE + straightOnlyWE + rightStraightWE + rightOnlyWE + allWE

    with open("data/cross.con.xml", "w") as connections:
        print("""<connections>""", file=connections)

        # North
        print("""   <!-- North -->""", file=connections)
        lane_count = 0
        for i in range(rightOnlyNS):
            for lane in range(rightOutLanesNS):
                print("""   <connection from="edgeN_O" to="edgeW_I" fromLane="%i" toLane="%i"/>"""
                      % (lane_count, lane), file=connections)
            lane_count += 1
        if rightOnlyNS > 0:
            print("", file=connections)
        for i in range(rightStraightNS):
            for lane in range(rightOutLanesNS):
                print("""   <connection from="edgeN_O" to="edgeW_I" fromLane="%i" toLane="%i"/>"""
                      % (lane_count, lane), file=connections)
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
                      % (lane_count, lane), file=connections)
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
        lane_count = 0
        for i in range(rightOnlyNS):
            for lane in range(rightOutLanesNS):
                print("""   <connection from="edgeS_O" to="edgeE_I" fromLane="%i" toLane="%i"/>"""
                      % (lane_count, lane), file=connections)
            lane_count += 1
        if rightOnlyNS > 0:
            print("", file=connections)
        for i in range(rightStraightNS):
            for lane in range(rightOutLanesNS):
                print("""   <connection from="edgeS_O" to="edgeE_I" fromLane="%i" toLane="%i"/>"""
                      % (lane_count, lane), file=connections)
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
                      % (lane_count, lane), file=connections)
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
        lane_count = 0
        for i in range(rightOnlyWE):
            for lane in range(rightOutLanesWE):
                print("""   <connection from="edgeW_O" to="edgeS_I" fromLane="%i" toLane="%i"/>"""
                      % (lane_count, lane), file=connections)
            lane_count += 1
        if rightOnlyWE > 0:
            print("", file=connections)
        for i in range(rightStraightWE):
            for lane in range(rightOutLanesWE):
                print("""   <connection from="edgeW_O" to="edgeS_I" fromLane="%i" toLane="%i"/>"""
                      % (lane_count, lane), file=connections)
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
                      % (lane_count, lane), file=connections)
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
        lane_count = 0
        for i in range(rightOnlyWE):
            for lane in range(rightOutLanesWE):
                print("""   <connection from="edgeE_O" to="edgeN_I" fromLane="%i" toLane="%i"/>"""
                      % (lane_count, lane), file=connections)
            lane_count += 1
        if rightOnlyWE > 0:
            print("", file=connections)
        for i in range(rightStraightWE):
            for lane in range(rightOutLanesWE):
                print("""   <connection from="edgeE_O" to="edgeN_I" fromLane="%i" toLane="%i"/>"""
                      % (lane_count, lane), file=connections)
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
                      % (lane_count, lane), file=connections)
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

def createNetwork(leftOnlyNS, leftStraightNS, straightOnlyNS, rightStraightNS, rightOnlyNS, allNS,
                  leftOnlyWE, leftStraightWE, straightOnlyWE, rightStraightWE, rightOnlyWE, allWE,
                  outspeedNS, inspeedNS, outspeedWE, inspeedWE):
    lanesNS = leftOnlyNS + leftStraightNS + straightOnlyNS + rightStraightNS + rightOnlyNS + allNS
    lanesWE = leftOnlyWE + leftStraightWE + straightOnlyWE + rightStraightWE + rightOnlyWE + allWE

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

    os.system("netconvert --node-files=data/cross.nod.xml --edge-files=data/cross.edg.xml --connection-files=data/cross.con.xml --output-file=data/cross.net.xml")

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

def setup(csv_path):
    dataframe = pd.read_csv(csv_path, sep='\t',
                            names=["leftOnlyNS", "leftStraightNS", "straightOnlyNS", "rightStraightNS", "rightOnlyNS",
                                   "allNS",
                                   "leftOnlyWE", "leftStraightWE", "straightOnlyWE", "rightStraightWE", "rightOnlyWE",
                                   "allWE",
                                   "moveDurationNS", "moveDurationWE", "yellowDurationNS", "yellowDurationWE",
                                   "turnDurationNS", "turnDurationWE", "demandN", "demandS", "demandW", "demandE",
                                   "demandProbNS_Straight", "demandProbNS_Left", "demandProbNS_Right",
                                   "demandProbNS_UTurn",
                                   "demandProbWE_Straight", "demandProbWE_Left", "demandProbWE_Right",
                                   "demandProbWE_UTurn",
                                   "outSpeedNS", "outSpeedWE", "inSpeedNS", "inSpeedWE", "vehicleMaxSpeed",
                                   "vehicleAccel",
                                   "vehicleDecel", "vehicleMinLength", "vehicleMaxLength", "minGap"])
    if dataframe.empty:
        dataframe.to_csv(csv_path)


def main(csv_path, time_steps,
        leftOnlyNS=0, leftStraightNS=1, straightOnlyNS=1, rightStraightNS=1, rightOnlyNS=0, allNS=0,
        leftOnlyWE=0, leftStraightWE=1, straightOnlyWE=1, rightStraightWE=1, rightOnlyWE=0, allWE=0,
        leftOutLanesNS=2, rightOutLanesNS=2, leftOutLanesWE=2, rightOutLanesWE=2,
        moveDurationNS=60, moveDurationWE=60,
        yellowDurationNS=5, yellowDurationWE=5,
        turnDurationNS=0, turnDurationWE=0,
        demandN=0.20, demandS=0.20, demandW=0.20, demandE=0.20,
        demandProbNS=None, demandProbWE=None,
        outSpeedNS=19.0, outSpeedWE=19.0, inSpeedNS=11.0, inSpeedWE=11.0,
        vehicleMaxSpeed=25.0, vehicleAccel=0.8, vehicleDecel=4.5,
        vehicleMinLength=5, vehicleMaxLength=5, minGap=2.5):

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

    # setDuration(leftOnlyNS, leftStraightNS, straightOnlyNS, rightStraightNS, rightOnlyNS, allNS,
    #             leftOnlyWE, leftStraightWE, straightOnlyWE, rightStraightWE, rightOnlyWE, allWE,
    #             moveDurationNS, moveDurationWE, yellowDurationNS, yellowDurationWE, turnDurationNS, turnDurationWE)
    buildConnections(leftOnlyNS, leftStraightNS, straightOnlyNS, rightStraightNS, rightOnlyNS, allNS,
                     leftOnlyWE, leftStraightWE, straightOnlyWE, rightStraightWE, rightOnlyWE, allWE,
                     leftOutLanesNS, rightOutLanesNS, leftOutLanesWE, rightOutLanesWE)
    createNetwork(leftOnlyNS, leftStraightNS, straightOnlyNS, rightStraightNS, rightOnlyNS, allNS,
                  leftOnlyWE, leftStraightWE, straightOnlyWE, rightStraightWE, rightOnlyWE, allWE,
                  outSpeedNS, inSpeedNS, outSpeedWE, inSpeedWE)
    # generateRoute(leftOnlyNS, leftStraightNS, straightOnlyNS, rightStraightNS, rightOnlyNS, allNS,
    #               leftOnlyWE, leftStraightWE, straightOnlyWE, rightStraightWE, rightOnlyWE, allWE,
    #               time_steps, demandN, demandS, demandW, demandE, vehicleAccel, vehicleDecel, vehicleMinLength,
    #               vehicleMaxLength, minGap, vehicleMaxSpeed, demandProbNS, demandProbWE)
    traci.start([checkBinary('sumo'), "-c", "data/cross.sumocfg",
                 "--tripinfo-output", "tripinfo.xml"])
    runSim()
    rates = findRate("tripinfo.xml")

    dataframe = pd.DataFrame([[i for i in range(40)]])
    dataframe.to_csv(csv_path, mode='a', header=False)

def fixIndex(csv_path):
    dataframe = pd.read_csv(csv_path, index_col=0)
    dataframe = dataframe.reset_index(drop=True)
    dataframe.to_csv(csv_path)

if __name__ == "__main__":
    start_time = time.time()
    setup("record.csv")
    main(time_steps=3000, csv_path="record.csv",
         leftOnlyNS=0, leftStraightNS=5, straightOnlyNS=0, rightStraightNS=1, rightOnlyNS=1, allNS=0,
         leftOnlyWE=0, leftStraightWE=5, straightOnlyWE=0, rightStraightWE=1, rightOnlyWE=1, allWE=0)
    fixIndex("record.csv")
    print(time.time() - start_time)