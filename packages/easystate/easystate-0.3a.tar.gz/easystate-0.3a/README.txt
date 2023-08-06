
easystate
=========

Easy State-Machine for python

from easystate import *
import time
SPEED = 1

class Starting(State):
    def eval(self):
        print 'Starting'
        time.sleep(SPEED)
    
    def on_start(self,e):
        print "Hello"
    
    def on_finish(self,e):
        self.transition("Listening")
        
        
class Listening(State):
    
    def eval(self):
        print 'Listening'
        time.sleep(SPEED)
        self.raiseEvent("connect")

    def on_start(self,e):
        print "Preparing for listening"
    
    def on_connect(self,e):
        self.transition('Negotiation')

class Negotiation(State):
    def eval(self):
        print 'checking validity'
        time.sleep(SPEED)
        print 'authenticating'
        time.sleep(SPEED)
        print 'registering'
        self.transition("Connected")
        
    def on_start(self,e):
        print 'Negotiating'
        
class Connected(State):
    def eval(self):
        print 'Connected'
        
    def on_finish(self,e):
        self.transition("Listening")
        

m = StateMachine(initialState="Starting")
m.appendState(Starting())
m.appendState(Listening())
m.appendState(Negotiation())
m.appendState(Connected())
m.start()

