#https://github.com/hamcrest/PyHamcrest
#http://packages.python.org/PyHamcrest/

import gevent
import unittest
import os

from hamcrest import *
from longtang.actors.tracking import tracking, messages
from longtang.system import system
from longtang.actors import testutils
from longtang.common import interactions, mediatracking

class TestMediaTrackingActor(unittest.TestCase):

	def test_creation(self):
		actor_system = system.ActorSystem()
		tracking_actor = actor_system.from_type(tracking.TrackingActor,'tracking-actor')

		try:
			assert_that(actor_system.find_by_id('tracking-actor'), is_not(None), 'Tracking actor does not exist within system')
		except exceptions.ActorNotFound as e:
			self.fail(str(e))
						
		actor_system.shutdown()

	def test_add_single_tracking(self):
		actor_system = system.ActorSystem()
		tracking_actor = actor_system.from_type(tracking.TrackingActor,'tracking-actor')

		response = interactions.InteractionPatterns.ask(actor_system,tracking_actor, messages.CreateTrackingEntry('/dummy.mp3'))

		assert_that(response, is_(not_none()),'Tracking identifier message is empty')
		assert_that(response, is_(instance_of(messages.TrackingEntryCreated)),'Tracking response message is not of the right type')
		assert_that(response.tracking_id(), is_(not_none()),'Tracking identifier is missing')

		actor_system.shutdown()

	def test_retrieve_single_tracking(self):
		actor_system = system.ActorSystem()
		tracking_actor = actor_system.from_type(tracking.TrackingActor,'tracking-actor')		

		tracking_id = interactions.InteractionPatterns.ask(actor_system,tracking_actor, messages.CreateTrackingEntry('/dummy-2.mp3')).tracking_id()

		response = interactions.InteractionPatterns.ask(actor_system,tracking_actor, messages.LookupTrackingEntry(tracking_id))

		assert_that(response, is_(not_none()),'Tracking information message is empty')
		assert_that(response, is_(instance_of(messages.TrackingEntryFound)),'Tracking information message is not of the right type')
		assert_that(response.tracking_info().mediafile.sourcepath, is_(equal_to('/dummy-2.mp3')),'Tracking identifier is missing')

		actor_system.shutdown()

	def test_retrieve_single_tracking_notfound(self):
		actor_system = system.ActorSystem()
		tracking_actor = actor_system.from_type(tracking.TrackingActor,'tracking-actor')		

		tracking_id = interactions.InteractionPatterns.ask(actor_system,tracking_actor, messages.CreateTrackingEntry('/dummy-2.mp3')).tracking_id()

		response = interactions.InteractionPatterns.ask(actor_system,tracking_actor, messages.LookupTrackingEntry('nonexistingid'))

		assert_that(response, is_(not_none()),'Tracking information message is empty')
		assert_that(response, is_(instance_of(messages.TrackingEntryNotFound)),'Tracking information message is not of the right type')
		assert_that(response.tracking_id(), is_(equal_to('nonexistingid')),'Tracking identifier is missing')		

		actor_system.shutdown()

	def test_notify_non_altering_tracking_event(self):
		actor_system = system.ActorSystem()
		tracking_actor = actor_system.from_type(tracking.TrackingActor,'tracking-actor')		

		tracking_id = interactions.InteractionPatterns.ask(actor_system,tracking_actor, messages.CreateTrackingEntry('/dummy-non-tracking.mp3')).tracking_id()

		event = mediatracking.MediaFileTrackingEvent('NONALTERING', 'This is a non-altering event')

		response = interactions.InteractionPatterns.ask(actor_system,tracking_actor, messages.RegisterTrackingEvent(tracking_id,event))

		assert_that(response, is_(not_none()),'Tracking information message is empty')
		assert_that(response, is_(instance_of(messages.TrackingEventSuccessfullyRegistered)),'Tracking event response is not of the right type')

		response = interactions.InteractionPatterns.ask(actor_system,tracking_actor, messages.LookupTrackingEntry(tracking_id))

		assert_that(response.tracking_info().tracking_events.of_type('NONALTERING').is_empty(), is_(False),'Tracking events of type NONALTERING are empty')
		assert_that(response.tracking_info().tracking_events.of_type('NONALTERING').get(0), is_(not_none()),'Tracked events does not exist')

		actor_system.shutdown()

	def test_notify_altering_tracking_event(self):
		actor_system = system.ActorSystem()
		tracking_actor = actor_system.from_type(tracking.TrackingActor,'tracking-actor')		

		tracking_id = interactions.InteractionPatterns.ask(actor_system,tracking_actor, messages.CreateTrackingEntry('/dummy-non-tracking.mp3')).tracking_id()

		event = DestinationUpdateTrackingEvent('DESTINATION', 'This is an altering event', '/target/path/dummy.mp3')

		response = interactions.InteractionPatterns.ask(actor_system,tracking_actor, messages.RegisterTrackingEvent(tracking_id,event))

		assert_that(response, is_(not_none()),'Tracking information message is empty')
		assert_that(response, is_(instance_of(messages.TrackingEventSuccessfullyRegistered)),'Tracking event response is not of the right type')

		response = interactions.InteractionPatterns.ask(actor_system,tracking_actor, messages.LookupTrackingEntry(tracking_id))

		assert_that(response.tracking_info().tracking_events.of_type('DESTINATION').is_empty(), is_(False),'Tracking events of type NONALTERING are empty')
		assert_that(response.tracking_info().tracking_events.of_type('DESTINATION').get(0), is_(not_none()),'Tracked events does not exist')
		assert_that(response.tracking_info().mediafile.destinationpath, is_(equal_to('/target/path/dummy.mp3')),'Mediafile information has not been updated')

		actor_system.shutdown()
		
class DestinationUpdateTrackingEvent(mediatracking.MediaFileTrackingEvent):
	def __init__(self, entry_type, description, destination):
		mediatracking.MediaFileTrackingEvent.__init__(self, entry_type, description,{"destination": destination})

	def process(self, file_descriptor):
		file_descriptor.destinationpath=self.context_information()["destination"]
		return file_descriptor