#https://github.com/hamcrest/PyHamcrest
#http://packages.python.org/PyHamcrest/

import gevent
import unittest
from longtang.common import interactions

from hamcrest import *
from longtang.system import system
from longtang.actors import testutils, actors, messages

class TestInteractions(unittest.TestCase):

	def test_ask_method(self):
		actor_system = system.ActorSystem()
		tracking_actor = actor_system.from_type(InteractionTestActor,'interactions-test-actor')

		response = interactions.InteractionPatterns.ask(actor_system,tracking_actor, SimpleRequest())

		assert_that(response, is_(not_none()),'Response received is empty')
		assert_that(response, is_(instance_of(SimpleResponse)),'Response object type is not the expected one')

		actor_system.shutdown()


class InteractionTestActor(actors.Actor):

    def receive(self, message):
        gevent.sleep(1)
        self.sender().tell(SimpleResponse('This is my test response'), self.myself())

class SimpleRequest(messages.ActorMessage):
	pass

class SimpleResponse(messages.ActorMessage):
	def __init__(self, value):
		self.__value=value

	def value(self):
		return self.__value