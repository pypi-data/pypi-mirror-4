# -*- coding: utf-8 -*-
'''
Created on Mar 18, 2013

@author: vahid
'''

import abc 

__version__ = "0.2a"
__all__ = ['StateMachine','State','Event','__version__']

class StateMachine(object):
    
    def __init__(self,initialState = None):
        self.state = None
        self.initialState = initialState
        self.states = {}
    
    def appendStates(self,*states):
        for state in states:
            self.appendState(state)
    
    def appendState(self,state):
        assert isinstance(state,State), "Invalid state object"
        state.register(self)
        self.states[state.name] = state
    
    def transition(self,state):
        assert isinstance(state,basestring)
        self.state = self.states[state]
        self.state.doJob()
    
    def start(self,initialState=None):
        if initialState:
            self.initialState = initialState
        elif self.initialState==None:
            assert len(self.states), 'At least one state must be added to machine.'
            self.initialState = self.states[0]
        self.transition(self.initialState)

class Event(object):
    __metaclass__ = abc.ABCMeta
    
    def __init__(self,name):
        self._name = name
    
    @property
    def name(self):
        return self._name
      

class State(object):
    __metaclass__ = abc.ABCMeta
    machine = None
    
    def __init__(self):
        self.events = []

    def register(self,machine):
        self.machine = machine
       
    def raiseEvent(self,e):
        if isinstance(e,basestring):
            e = Event(e)
            
        if hasattr(self, 'on_%s' % e.name):
            getattr(self,'on_%s' % e.name)(e)

    def transition(self,state):
        if hasattr(self,'nextState'):
            raise Exception("Transition has been already applied") 
        self.nextState = state
    
    def doJob(self):
        if hasattr(self,'nextState'):
            del self.nextState
        self.raiseEvent("start")
        self.eval()
        self.raiseEvent("finish")
        assert hasattr(self,'nextState'), "state: %s" % self.name 
        self.machine.transition(self.nextState)
        
    @property
    def context(self,state):
        return self.machine.context

    @abc.abstractmethod
    def eval(self):
        raise NotImplementedError()
    
    @property
    def name(self):
        return self.__class__.__name__
        

# Test cases
if __name__ == '__main__':
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
    m.appendStates(Starting(),Listening(),Negotiation(),Connected())
    m.start()

