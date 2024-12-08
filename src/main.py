# ---------------------------------------------------------------------------- #
#                                                                              #
# 	Module:       main.py                                                      #
# 	Author:       krizz                                                        #
# 	Created:      12/4/2024, 5:08:37 PM                                        #
# 	Description:  V5 project                                                   #
#                                                                              #
# ---------------------------------------------------------------------------- #

# Library imports
from vex import *

#States
IDLE = 0
LINE = 1
SEARCHING = 2
APPROACHING = 3
COLLECTING = 4
RETURNING = 5

currentState = IDLE

#Counter 
i = 0

#Initialization
brain=Brain()

controller = Controller()

ultraSonic = Sonar(brain.three_wire_port.g)

leftLine = Line(brain.three_wire_port.f)
rightLine = Line(brain.three_wire_port.e)

leftMotor = Motor(Ports.PORT11, GearSetting.RATIO_18_1, True)
rightMotor = Motor(Ports.PORT8, GearSetting.RATIO_18_1, True)

armMotor = Motor(Ports.PORT7, GearSetting.RATIO_18_1, False)
forkMotor = Motor(Ports.PORT6, GearSetting.RATIO_18_1, False)       


leftMotor.reset_position()
rightMotor.reset_position()
armMotor.reset_position()
forkMotor.reset_position()

forkMotor.set_stopping(HOLD)

#Vision
Vision3_LIME = Signature (1, -6429, -5309, -5869, -3997, -3303, -3650, 2.5, 0)

Vision3 = Vision (Ports.PORT20, 50, Vision3_LIME)

targetX = 0

#Line
lowerBound = 60
upperBound = 100

#Constants
wheelCircumference = 314.159265

#Vision Function
def detect():
    obj = Vision3.take_snapshot(Vision3_LIME)
    if obj:
        largest = Vision3.largest_object()
        cx, cy, width, height = largest.centerX, largest.centerY, largest.width, largest.height
        return cx, cy, width, height
    else:
        return None, None, 0, 0

def lineFollow():
        if lowerBound  <= leftLine.reflectivity() <= upperBound and lowerBound <= rightLine.reflectivity() <= upperBound:
                #print("left", leftPos)
                #print("right", rightPos)
            leftMotor.spin(FORWARD, 200)
            rightMotor.spin(FORWARD, -200)
                
        elif leftLine.reflectivity() > rightLine.reflectivity():
            print("LEFT")
            leftMotor.spin(FORWARD, 170)
            rightMotor.spin(FORWARD, -90)
           
        elif rightLine.reflectivity() > leftLine.reflectivity():
            print('RIGHT')
            leftMotor.spin(FORWARD, 90)
            rightMotor.spin(FORWARD, -170)

        elif leftLine.reflectivity() < lowerBound and rightLine.reflectivity() < lowerBound or leftLine.reflectivity() > upperBound or rightLine.reflectivity() > upperBound:                    
            if leftLine.reflectivity() < rightLine.reflectivity():
                print("LEFT 2")
                leftMotor.spin(FORWARD, 225)
                rightMotor.spin(FORWARD, -150)
            else:
                print("RIGHT 2")
                leftMotor.spin(FORWARD, 150)
                rightMotor.spin(FORWARD, -225)

def collect(height):
        forkMotor.spin_to_position(0)
        forkMotor.reset_position()
        print(forkMotor.position())
        forkMotor.spin_to_position(-height)
        print(forkMotor.position())

        leftMotor.spin_for(FORWARD, 720, DEGREES, 100, RPM, False)
        rightMotor.spin_for(FORWARD, -720, DEGREES, 100, RPM, True)


        forkMotor.spin_to_position(0)
        #forkMotor.spin_for(FORWARD, height, DEGREES, 300, RPM, True)
        wait(1, SECONDS)
        print(forkMotor.position())

        leftMotor.spin_for(FORWARD, -720, DEGREES, 100, RPM, False)
        rightMotor.spin_for(FORWARD, 720, DEGREES, 100, RPM, True)

def mainFunction():
    global currentState
    global targetX
    global i

    if currentState == IDLE:
        print(forkMotor.position())
        if(controller.buttonA.pressing()):
            print("IDLE -> DRIVE")
            currentState = LINE
        if(controller.buttonB.pressing()):
            #forkMotor.spin_for(FORWARD, 42, DEGREES, 15, RPM)
            forkMotor.spin(FORWARD, -2, RPM)
            print(forkMotor.position())

        if(controller.buttonX.pressing()):
            forkMotor.spin_for(FORWARD, -42, DEGREES, 15, RPM)


        elif currentState == LINE:
            leftPos = leftMotor.position()
            rightPos = rightMotor.position()
           
            if i == 0:
                rotations = (2000 / wheelCircumference) * 360
                

            while (leftPos < rotations and rightPos < rotations or ultraSonic.distance(MM)) < 50:
                leftPos = leftMotor.position()
                rightPos = rightMotor.position()         
                lineFollow()   

            else:
                leftMotor.stop() 
                rightMotor.stop()
                print("DRIVE -> SEARCHING")
                currentState = SEARCHING
        
    elif currentState == SEARCHING:
        if leftMotor.is_done() and rightMotor.is_done():
            leftMotor.spin(FORWARD, -100)
            rightMotor.spin(FORWARD, -100)
            cx, cy, width, height = detect()
            if cx is not None:
                leftMotor.stop()
                rightMotor.stop()
                leftMotor.reset_position()
                rightMotor.reset_position()  
                print("SEARCHING -> APPROACHING")
                currentState = APPROACHING
            else:
                width, height = 0, 0

    elif currentState == APPROACHING:
        cx, cy, width, height = detect()

        if cx is None:
            print('OBJECT LOST' )
            print("APPROACHING -> SEARCHING")
            currentState = APPROACHING
    
        else:
            error = 255 - cx
            if height < 120:
                if error < -15:
                    leftMotor.spin(FORWARD, 90)
                    rightMotor.spin(FORWARD, -20)
                elif error > 15:
                    leftMotor.spin(FORWARD, 20)
                    rightMotor.spin(FORWARD, -90)
                else:
                    leftMotor.spin(FORWARD, 30)
                    rightMotor.spin(FORWARD, -30)
            else:
                print('APPROACHING -> COLLECTING')

                leftMotor.stop()
                rightMotor.stop()
                currentState = COLLECTING

    elif currentState == COLLECTING:
        print("test")
        '''
        forkMotor.spin_for(FORWARD, -42, DEGREES, 15, RPM, True)
        
        leftMotor.spin_for(FORWARD, 720, DEGREES, 100, RPM, False)
        rightMotor.spin_for(FORWARD, -720, DEGREES, 100, RPM, True)

        forkMotor.spin_for(FORWARD, 42, DEGREES, 169, RPM, True)
        wait(1, SECONDS)
        
        leftMotor.spin_for(FORWARD, -720, DEGREES, 100, RPM, False)
        rightMotor.spin_for(FORWARD, 720, DEGREES, 100, RPM, True)
        '''

        collect(45)


        if leftMotor.is_done() and rightMotor.is_done():
            print("COLLECTION -> RETURN")
            currentState = RETURNING

    elif currentState == RETURNING:
        leftPos = leftMotor.position()
        rightPos = rightMotor.position()


        leftMotor.spin_for(FORWARD, -600, DEGREES, 50, RPM, False)
        rightMotor.spin_for(FORWARD, 600, DEGREES, 50  , RPM, True)

        while leftLine.reflectivity() < 50 or rightLine.reflectivity() < 50:
            print("yep")
            leftMotor.spin(FORWARD, 30)
            rightMotor.spin(FORWARD, 30)
            break
        else:
            i += 1
            print("RETURN -> LINE")
            currentState = LINE

while True:
    mainFunction()
    pass