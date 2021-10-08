random.seed(42)  # make tests reproducible
vtypes = []
# demand per second from different directions
if demandProbNS is None:
    # left, straight, right
    demandProbNS = [1, 1, 1, 1]
if demandProbWE is None:
    # left, straight, right
    demandProbWE = [1, 1, 1, 1]
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
