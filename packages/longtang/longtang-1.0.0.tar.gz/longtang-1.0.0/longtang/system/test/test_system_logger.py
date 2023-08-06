#http://docs.python.org/2/library/unittest.html#unittest.TestCase.assertEqual

import unittest
import os
import gevent

from hamcrest import *
from longtang.actors import testutils,actors,domain, messages
from longtang.system import system, domain as sys_domain

class TestSystemLogger(unittest.TestCase):

    def test_simple_event_message(self):

        sniffer = testutils.StdoutSniffer()

        actor_system = system.ActorSystem()
        logger_actor = actor_system.from_type(TestLoggerActor,'test-logger-actor')

        sniffer.start()

        logger_actor.tell(GenerateSimpleLogMessages('This is an INFO-LOG-TEST message', 'INFO'))
        logger_actor.tell(GenerateSimpleLogMessages('This is an ERROR-LOG-TEST message', 'ERROR'))
        logger_actor.tell(TerminateYourself())

        actor_system.wait_for(logger_actor)

        sniffer.stop()

        #TODO Logger output is not captured, as long as we implement the message sniffer, we should redefine this test
        #assert_that(sniffer.value(), contains_string('This is an INFO-LOG-TEST message'),'INFO message was not found')
        #assert_that(sniffer.value(), contains_string('This is an ERROR-LOG-TEST message'),'ERROR message was not found')

    def test_file_event_message(self):
        pass



class TestLoggerActor(actors.Actor):
    def receive(self, message):
        if isinstance(message, TerminateYourself):
            gevent.sleep(0.5)
            self.myself().tell(messages.PoisonPill())
        elif isinstance(message, GenerateSimpleLogMessages):
            if message.type() is 'INFO':
                self.logger().info(message.text())
            else:
                self.logger().error(message.text())
        else:        
            self.notify_marooned_message(message)   


class TerminateYourself(messages.ActorMessage):
    pass

class GenerateSimpleLogMessages(messages.ActorMessage):
    def __init__(self, message, type):
        self.__message=message
        self.__type=type
    def text(self):
        return self.__message
    def type(self):
        return self.__type

if __name__ == '__main__':
    unittest.main()