#http://docs.python.org/2/library/unittest.html#unittest.TestCase.assertEqual

import unittest
import os
import gevent

from hamcrest import *
from longtang.actors import testutils,actors,domain, messages
from longtang.system import system, domain as sys_domain

class TestActorSystem(unittest.TestCase):

    def test_actor_creation_by_type(self):

        actor_system = system.ActorSystem()
        dummy_actor_ref = actor_system.from_type(DummyActor,'dummy-actor')

        self.assertIsNotNone(dummy_actor_ref, 'Actor has not been created')
        self.assertIsNotNone(dummy_actor_ref.context(), 'System reference does not exist within actor instance')
        self.assertNotEqual(dummy_actor_ref.context(), actor_system, 'System reference is directly passed to the actor!')
        self.assertTrue(isinstance(dummy_actor_ref, sys_domain.ActorRef), 'Actor reference is not of the expected type')
        self.assertTrue(isinstance(dummy_actor_ref.parent(), sys_domain.ActorRef), 'Parent actor reference is not of the expected type')
        self.assertTrue(isinstance(dummy_actor_ref.context(),domain.SystemRefWrapper), 'System information within actor is not of the right type')        
        self.assertIsNotNone(dummy_actor_ref.context().get_by_id('dummy-actor'), 'Actor does not exist within context')
        self.assertIsNotNone(actor_system.find_by_id('dummy-actor'), 'Actor does not exist within context')

        actor_system.shutdown()

    def test_actor_creation_with_factory(self):

        actor_system = system.ActorSystem()
        dummy_actor_ref = actor_system.with_factory(DummyFactory(),'dummy-factory-actor')

        self.assertIsNotNone(dummy_actor_ref, 'Actor has not been created')
        self.assertIsNotNone(dummy_actor_ref.context(), 'System reference does not exist within actor instance')
        self.assertNotEqual(dummy_actor_ref.context(), actor_system, 'System reference is directly passed to the actor!')
        self.assertTrue(isinstance(dummy_actor_ref.context(),domain.SystemRefWrapper), 'System information within actor is not of the right type')
        self.assertTrue(isinstance(dummy_actor_ref, sys_domain.ActorRef), 'Actor reference is not of the expected type')
        self.assertTrue(isinstance(dummy_actor_ref.parent(), sys_domain.ActorRef), 'Parent actor reference is not of the expected type')        
        self.assertIsNotNone(dummy_actor_ref.context().get_by_id('dummy-factory-actor'), 'Actor does not exist within context')
        self.assertIsNotNone(actor_system.find_by_id('dummy-factory-actor'), 'Actor does not exist within context')

        actor_system.shutdown()

    def test_child_creation(self):

        actor_system = system.ActorSystem()
        main_actor = actor_system.from_type(DummyActor,'main-actor')

        assert_that(actor_system.find_by_id('main-actor'), is_not(None), 'Main actor does not exist within system')
        assert_that(actor_system.find_by_id('dummy-child-actor'), is_not(None), 'Child actor does not exist within system')
        assert_that(actor_system.find_by_id('dummy-child-actor'), is_(instance_of(sys_domain.ActorRef)), 'Child actor is not of the right type')
        assert_that(actor_system.find_by_id('dummy-child-actor')._instance(), is_(instance_of(DummyChildActor)), 'Child actor is not of the right type')
        assert_that(actor_system.find_by_id('dummy-child-actor').parent(), is_(equal_to(actor_system.find_by_id('main-actor'))),'Parent actor is not correctly assigned')

        #TODO Add test related to child methods

        actor_system.shutdown()

    def test_child_management(self):

        actor_system = system.ActorSystem()
        main_actor = actor_system.from_type(DummyActor,'main-actor')

        assert_that(actor_system.find_by_id('main-actor').status(), is_(equal_to(domain.ActorStatus.READY)), 'Main actor status has not been initialized as expected')
        assert_that(actor_system.find_by_id('dummy-child-actor').status(), is_(equal_to(domain.ActorStatus.READY)), 'Child actor status has not been initialized as expected')

        main_actor.tell(TerminateYourself())

        actor_system.wait_for(main_actor)

        assert_that(main_actor.context().child('dummy-child-actor').status(), is_(equal_to(domain.ActorStatus.TERMINATED)), 'Child actor has not been terminated as expected')
        assert_that(main_actor.status(), is_(equal_to(domain.ActorStatus.TERMINATED)), 'Child actor has not been terminated as expected')
        assert_that(actor_system.find_by_id('main-actor').status(), is_(equal_to(domain.ActorStatus.TERMINATED)), 'Child actor has not been terminated as expected')
        assert_that(actor_system.find_by_id('dummy-child-actor').status(), is_(equal_to(domain.ActorStatus.TERMINATED)), 'Child actor has not been terminated as expected')

        actor_system.shutdown()

    def test_marooned_messages(self):

        actor_system = system.ActorSystem()
        main_actor = actor_system.from_type(MaroonedMessageActor,'main-actor')

        main_actor.tell(MaroonedMessage())
        main_actor.tell(TerminateYourself())

        actor_system.wait_for(main_actor)

        assert_that(actor_system.marooned_messages().reported_by('main-actor'), is_(not_none()),'Main actor marooned messages list is none')
        assert_that(actor_system.marooned_messages().reported_by('main-actor').size(), is_(equal_to(1)),'Main actor marooned messages list has no elements')
        assert_that(actor_system.marooned_messages().reported_by('main-actor').get(0), is_(instance_of(MaroonedMessage)),'Main actor marooned message is not the expected one')
        assert_that(actor_system.marooned_messages().all(), is_(not_none()),'Global marooned messages list is none')
        assert_that(actor_system.marooned_messages().all().size(), is_(equal_to(1)),'Global marooned messages list is empty')

        actor_system.shutdown()


class DummyActor(actors.Actor):

    def pre_setup(self):
        
        self.__dummy_child_ref = self.context().from_type(DummyChildActor,'dummy-child-actor')

    def receive(self, message):
        if isinstance(message, TerminateYourself):
            gevent.sleep(0.5)
            self.myself().tell(messages.PoisonPill())

class DummyChildActor(actors.Actor):

    def receive(self, message):
        pass

class DummyFactoryActor(actors.Actor):

    def receive(self, message):
        pass

class DummyFactory(sys_domain.ActorFactory):

    def create(self, unique_id, system_ref):
        return DummyFactoryActor(system_ref,unique_id)

class MaroonedMessageActor(actors.Actor):

    def receive(self, message):
        if isinstance(message, TerminateYourself):
            gevent.sleep(0.5)
            self.myself().tell(messages.PoisonPill())
        else:        
            self.notify_marooned_message(message) 


class MaroonedMessage(messages.ActorMessage):
    pass

class TerminateYourself(messages.ActorMessage):
    pass

if __name__ == '__main__':
    unittest.main()