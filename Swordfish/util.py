import math
from rlbot.agents.base_agent import BaseAgent, SimpleControllerState

GOAL_WIDTH = 1900
FIELD_LENGTH = 10280
FIELD_WIDTH = 8240

class Vector3:
    def __init__(self, data):
        self.data = data
    def __add__(self,value):
        return Vector3([self.data[0]+value.data[0],self.data[1]+value.data[1],self.data[2]+value.data[2]])
    def __sub__(self,value):
        return Vector3([self.data[0]-value.data[0],self.data[1]-value.data[1],self.data[2]-value.data[2]])
    def __mul__(self,value):
        return (self.data[0]*value.data[0] + self.data[1]*value.data[1] + self.data[2]*value.data[2])
    def normalize(self):
        if abs(self.data[0]) > abs(self.data[1]) and abs(self.data[0]) > abs(self.data[2]):
            self.data[1] /= abs(self.data[0])
            self.data[2] /= abs(self.data[0])
            self.data[0] = sign(self.data[0])
        elif abs(self.data[1]) > abs(self.data[0]) and abs(self.data[1]) > abs(self.data[2]):
            self.data[0] /= abs(self.data[1])
            self.data[2] /= abs(self.data[1])
            self.data[1] = sign(self.data[1])
        else:
            self.data[0] /= abs(self.data[2])
            self.data[1] /= abs(self.data[2])
            self.data[2] = sign(self.data[2])
        return self

class Matrix2():
    def __init__(self,data):
        self.data = data
    def __mul__(self,value):
        return Vector2([value.data[0]*self.data[0][0] + value.data[1]*self.data[1][0], value.data[0]*self.data[0][1] + value.data[1]*self.data[1][1]])

ROTATE = Matrix2([[0,-1],[1,0]])

class obj:
    def __init__(self):
        self.location = Vector3([0,0,0])
        self.velocity = Vector3([0,0,0])
        self.rotation = Vector3([0,0,0])
        self.rvelocity = Vector3([0,0,0])

        self.local_location = Vector3([0,0,0])
        self.boost = 0

def to_local(target_object,our_object):
    x = (toLocation(target_object) - our_object.location) * our_object.matrix[0]
    y = (toLocation(target_object) - our_object.location) * our_object.matrix[1]
    z = (toLocation(target_object) - our_object.location) * our_object.matrix[2]
    return Vector3([x,y,z])

def rotator_to_matrix(our_object):
    r = our_object.rotation.data
    CR = math.cos(r[2])
    SR = math.sin(r[2])
    CP = math.cos(r[0])
    SP = math.sin(r[0])
    CY = math.cos(r[1])
    SY = math.sin(r[1])

    matrix = []
    matrix.append(Vector3([CP*CY, CP*SY, SP]))
    matrix.append(Vector3([CY*SP*SR-CR*SY, SY*SP*SR+CR*CY, -CP * SR]))
    matrix.append(Vector3([-CR*CY*SP-SR*SY, -CR*SY*SP+SR*CY, CP*CR]))
    return matrix

def ballReady(agent):
    ball = agent.ball
    if abs(ball.velocity.data[2]) < 100 and ball.location.data[2] < 250:
        if abs(ball.location.data[1]) < 5000:
            return True
    return False

def ballProject(agent):
    goal = Vector3([0,-sign(agent.team)*FIELD_LENGTH/2,100])
    goal_to_ball = (agent.ball.location - goal).normalize()
    difference = agent.me.location - agent.ball.location
    return difference * goal_to_ball


def sign(x):
    if x <= 0:
        return -1
    else:
        return 1

def cap(x, low, high):
    if x < low:
        return low
    elif x > high:
        return high
    else:
        return x

def steer(angle, controller_state, target_object, agent):
    final = ((10 * angle+sign(angle))**3) / 20
    distance_to_ball = distance2D(target_object, agent.me)
    if abs(angle) > (math.pi/2) and abs(angle) < ((3*math.pi)/4) and distance_to_ball > 200:
        controller_state.handbrake = True
    else:
        controller_state.handbrake = False
    return cap(final,-1,1)

def angle2(target_location,object_location):
    difference = toLocation(target_location) - toLocation(object_location)
    return math.atan2(difference.data[1], difference.data[0])


def velocity2D(target_object):
    return math.sqrt(target_object.velocity.data[0]**2 + target_object.velocity.data[1]**2)

def toLocal(target,our_object):
    if isinstance(target,obj):
        return target.local_location
    else:
        return to_local(target,our_object)

def toLocation(target):
    if isinstance(target,Vector3):
        return target
    elif isinstance(target,list):
        return Vector3(target)
    else:
        return target.location

def distance2D(target_object, our_object):
    difference = toLocation(target_object) - toLocation(our_object)
    return math.sqrt(difference.data[0]**2 + difference.data[1]**2)


def closestBoost(agent):
    file = open("BigBoostLocs.txt", 'r+') #open file for big boost pads
    Locs = file.read()               #read file
    Coords = Locs.split('\n')        #split lines into list
    minDistance = 1000000
    boostCoordinates = [0.0, 0.0, 0.0]
    for c in Coords:
        string = c[1:len(c)-1]       #remove brackets
        string = string.split(',')   #separate x,y,z coordinates

        boostX = float(string[0])    #convert text strings
        boostY = float(string[1])    #to float
        boostZ = float(string[2])    #coordinate values

        thisDistance = distance2D([boostX, boostY, boostZ], agent.location.data)
        if thisDistance < minDistance:
            minDistance = thisDistance
            boostCoordinates = [boostX, boostY, boostZ]

    return Vector3(boostCoordinates)
