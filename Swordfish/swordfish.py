import math
import time
from util import *
from states import *

from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket

global ALL_PLAYERS
global ALL_BOOST_PADS
global KICKOFF

class Swordfish(BaseAgent):

    def initialize_agent(self):
        self.me = obj()
        self.ball = obj()
        self.start = time.time()

        self.state = kickoffShot()
        self.controller = kickoffController

    def checkState(self):
        if KICKOFF == True:
            self.state.expired = True
        if self.state.expired:
            if kickoffShot().available(self) == True:
                self.state = kickoffShot()
            elif calcShot().available(self) == True:
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
        print(self.state)
        return self.state.execute(self)


        # self.renderer.begin_rendering()
        # self.renderer.draw_line_3d([0,0,10],[0,100,10],self.renderer.white())
        # self.renderer.end_rendering()


        # #MAKE BOT NOT MOVE
        # controller_state = SimpleControllerState()
        # controller_state.throttle = 0
        # return controller_state
        # #MAKE BOT NOT MOVE

    def preprocess(self,game):
        global ALL_PLAYERS
        global ALL_BOOST_PADS
        global KICKOFF
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
        KICKOFF = game.game_info.is_kickoff_pause
        ALL_PLAYERS = game.game_cars
        ALL_BOOST_PADS = []
        pads = self.get_field_info().boost_pads
        for pad in pads:
            if pad.is_full_boost:
                ALL_BOOST_PADS.append(pad)
