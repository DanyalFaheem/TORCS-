import msgParser
import carState
import carControl


class Driver(object):
    '''
    A driver object for the SCRC
    '''

    def __init__(self, stage):
        '''Constructor'''
        self.WARM_UP = 0
        self.QUALIFYING = 1
        self.RACE = 2
        self.UNKNOWN = 3
        self.stage = stage

        self.parser = msgParser.MsgParser()

        self.state = carState.CarState()
        self.forward = True
        self.control = carControl.CarControl()

        self.steer_lock = 0.785398
        self.max_speed = 300
        self.prev_rpm = None

        from pynput.keyboard import Controller, Listener, Key, KeyCode
        Controller()
        self.keymap = {Key.up: 'up', 'w': 'up', Key.left: 'left', Key.right: 'right', Key.down: 'down',
            Key.space: 'space', Key.shift_r: 'gearup', Key.shift_l: 'geardown', Key.alt_l: 'reverse'}
        self.keys = self.keymap.keys()
        self.thread = Listener(on_press=self.press, on_release=self.release)
        self.running = True
        self.thread.start()
        # self.thread.join()

    def init(self):
        '''Return init string with rangefinder angles'''
        self.angles = [0 for x in range(19)]

        for i in range(5):
            self.angles[i] = -90 + i * 15
            self.angles[18 - i] = 90 - i * 15

        for i in range(5, 9):
            self.angles[i] = -20 + (i-5) * 5
            self.angles[18 - i] = 20 - (i-5) * 5

        return self.parser.stringify({'init': self.angles})

    def drive(self, msg):
        self.state.setFromMsg(msg)
        # self.speed()
        #
        # self.steer()
        #
        self.gear()
        #

        return self.control.toMsg()

    def steer(self):
        angle = self.state.angle
        dist = self.state.trackPos

        self.control.setSteer((angle - dist*0.5)/self.steer_lock)

    def gear(self):
        rpm = self.state.getRpm()
        gear = self.state.getGear()
        speed = self.state.getSpeedX()
        maxgear = 6
        # if self.prev_rpm == None:
        #     up = True
        # else:
        #     if (self.prev_rpm - rpm) < 0:
        #         up = True
        #     else:
        #         up = False
        # if gear == 1 and rpm > 7000:
        #     gear += 1
        # if speed + 1 != 0 and gear != 0:
        #     if rpm > 7000 and (speed + 1 / gear) > 30 and gear < maxgear:
        #         gear += 1
            
        if self.forward==True:
            if rpm > 8000:
                gear+=1
            elif rpm <=3000 and speed<60:
                gear=1
            elif gear==2 and rpm<=3000 and speed>=0 and speed<60:
                gear-=1
            elif gear==3 and rpm<=4980 and speed >=60 and speed<90:
                gear-=1
            elif gear==4 and rpm<=5108 and speed>=90 and speed <130:
                gear-=1
            elif gear==5 and rpm<=5300 and speed>=130 and speed <170:
                gear-=1
            elif gear>=6 and rpm<=5500 :
                gear-=1
        else:
            gear=-1
            # if rpm < 3000 and (speed + 1 / gear) < 30 and gear > 1:
            #     gear -= 1

        # if rpm>8000:
        #     gear+=1

        # if rpm<3000 and gear>1 and speed<50:
        #     gear=1
        self.control.setGear(gear)
    
    def speed(self):
        speed = self.state.getSpeedX()
        accel = self.control.getAccel()
        
        if speed < self.max_speed:
            accel += 0.1
            if accel > 1:
                accel = 1.0
        else:
            accel -= 0.1
            if accel < 0:
                accel = 0.0
        
        self.control.setAccel(accel)



    def onShutDown(self):
        pass
    
    def onRestart(self):
        pass


    def press(self, key):
        if key in self.keymap and (self.keymap[key] == 'up'):
            self.control.setAccel(1)
        if key in self.keymap and self.keymap[key] == 'down':
            self.control.setBrake(1)
        if key in self.keymap and self.keymap[key] == 'left':
            self.control.setSteer(self.steer_lock)
        if key in self.keymap and self.keymap[key] == 'right':
            self.control.setSteer(-1*self.steer_lock)
        if key in self.keymap and self.keymap[key] == 'space':
            self.forward=not self.forward

    def release(self, key):
        if key in self.keymap and  (self.keymap[key] == 'up' or self.keymap[key]=='w'):
            self.control.setAccel(0)
        if key in self.keymap and self.keymap[key] == 'down':
            self.control.setBrake(0)
        if key in self.keymap and self.keymap[key] == 'space':
            self.control.setBrake(0)
        if key in self.keymap and self.keymap[key] == 'left':
            self.control.setSteer(0)
        if key in self.keymap and self.keymap[key] == 'right':
            self.control.setSteer(0)



