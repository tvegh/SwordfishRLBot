import math
import time
from util import *
from states import *

from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket

global ALL_PLAYERS
global ALL_BOOST_PADS

class Swordfish(BaseAgent):

    def initialize_agent(self):
        self.me = obj()
        self.ball = obj()
        self.start = time.time()

        self.state = calcShot()
        self.controller = calcController

    def checkState(self):
        if self.state.expired:
            if calcShot().available(self) == True:
                self.state = calcShot()
            elif quickShot().available(self) == True:
                self.state = quickShot()
            elif goForBoost().available(self) == True:
                self.state = goForBoost()
            else:
                self.state = quickShot()
                #self.state = goForBoost()


    def get_output(self, game: GameTickPacket) -> SimpleControllerState:
        self.preprocess(game)
        self.checkState()
        return self.state.execute(self)

    def preprocess(self,game):
        global ALL_PLAYERS
        global ALL_BOOST_PADS
        self.me.location.data = [game.game_cars[self.index].physics.location.x,game.game_cars[self.index].physics.location.y,game.game_cars[self.index].physics.location.z]
        self.me.velocity.data = [game.game_cars[self.index].physics.velocity.x,game.game_cars[self.index].physics.velocity.y,game.game_cars[self.index].physics.velocity.z]
        self.me.rotation.data = [game.game_cars[self.index].physics.rotation.pitch,game.game_cars[self.index].physics.rotation.yaw,game.game_cars[self.index].physics.rotation.roll]
        self.me.rvelocity.data = [game.game_cars[self.index].physics.angular_velocity.x,game.game_cars[self.index].physics.angular_velocity.y,game.game_cars[self.index].physics.angular_velocity.z]
        self.me.matrix = rotator_to_matrix(self.me)
        self.me.boost = game.game_cars[self.index].boost

        self.ball.location.data = [game.game_ball.physics.location.x,game.game_ball.physics.location.y,game.game_ball.physics.location.z]
        self.ball.velocity.data = [game.game_ball.physics.velocity.x,game.game_ball.physics.velocity.y,game.game_ball.physics.velocity.z]
        self.ball.rotation.data = [game.game_ball.physics.rotation.pitch,game.game_ball.physics.rotation.yaw,game.game_ball.physics.rotation.roll]
        self.ball.rvelocity.data = [game.game_ball.physics.angular_velocity.x,game.game_ball.physics.angular_velocity.y,game.game_ball.physics.angular_velocity.z]

        self.ball.local_location = to_local(self.ball,self.me)
        ALL_PLAYERS = game.game_cars
        ALL_BOOST_PADS = []
        pads = self.get_field_info().boost_pads
        #print("____________________________________________")
        for pad in pads:
            if pad.is_full_boost:
                ALL_BOOST_PADS.append(pad)
            #    print(pad.location.x, pad.location.y,pad.location.z)
    #    print("____________________________________________")
