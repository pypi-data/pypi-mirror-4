#https://github.com/hamcrest/PyHamcrest
#http://packages.python.org/PyHamcrest/

import gevent
import unittest
import os

from hamcrest import *
from longtang.actors.supervisors.id3taghandler import id3taghandler, messages, factory, configuration
from longtang.system import system
from longtang.actors import testutils
from longtang.common import domain as common_domain
from longtang.actors.tracking import tracking, facade

class TestId3TagHandlerSupervisor(unittest.TestCase):

	def test_creation(self):

		actor_system = system.ActorSystem()

		config = configuration.Id3TagHandlerConfigurationBuilder().override_tags(False)\
																  .offline_mode(False)\
																  .build()

		filepackaging_actor = actor_system.with_factory(factory.Id3TagSupervisorFactory(config),'id3tag-supervisor')

		try:
			assert_that(actor_system.find_by_id('id3tag-supervisor'), is_not(None), 'Id3 tag supervisor does not exist within system')
			assert_that(actor_system.find_by_id('id3tag-reader-actor'), is_not(None), 'Id3 reader actor does not exist within system')
			assert_that(actor_system.find_by_id('musicbrainz-actor'), is_not(None), 'Musicbrainz actor does not exist within system')

			assert_that(actor_system.find_by_id('id3tag-reader-actor').parent(), is_(equal_to(actor_system.find_by_id('id3tag-supervisor'))),'Parent actor is not correctly assigned')
			assert_that(actor_system.find_by_id('musicbrainz-actor').parent(), is_(equal_to(actor_system.find_by_id('id3tag-supervisor'))),'Parent actor is not correctly assigned')
			
		except exceptions.ActorNotFound as e:
			self.fail(str(e))

		actor_system.shutdown()

	def test_full_metadata_from_file(self):

		data_dir = os.path.join(testutils.current_dirpath(__file__), 'data')
		source_file = os.path.join(data_dir, 'with_id3taginfo.mp3')

		config = configuration.Id3TagHandlerConfigurationBuilder().override_tags(False)\
																  .offline_mode(False)\
																  .build()

		id3taghandler_actor = testutils.TestActorBuilder().withFactory(factory.Id3TagSupervisorFactory(config))\
															.withId('test-id3taghandler')\
															.terminationMoratorium(2)\
															.terminate_system(False)\
															.terminationType(messages.FileMetadataAvailable).build()

		tracking_facade = facade.MediaTrackingFacade.create_within(id3taghandler_actor.system())
		tracking_id = tracking_facade.create_tracking(source_file)

		id3taghandler_actor.tell(messages.InspectFileMetadata(source_file, tracking_id))

		assert_that(id3taghandler_actor.inspector().num_instances(messages.FileMetadataAvailable), is_(equal_to(1)), 'Total amount of FileMetadataAvailable messages received is wrong')

		message = id3taghandler_actor.inspector().get_first(messages.FileMetadataAvailable)

		assert_that(message.metadata().artist, is_(not_none()), 'Artist information is empty')
		assert_that(message.metadata().artist, is_(equal_to('Bon Jovi')), 'Artist information content is not as expected')

		assert_that(message.metadata().album, is_(not_none()), 'Album information is empty')
		assert_that(message.metadata().album, is_(equal_to('New Jersey')), 'Album information content is not as expected')

		assert_that(message.metadata().title, is_(not_none()), 'Title information is empty')
		assert_that(message.metadata().title, is_(equal_to('Ride Cowboy Ride')), 'Title information content is not as expected')

		assert_that(message.metadata().track_number, is_(not_none()), 'Track number information is empty')
		assert_that(message.metadata().track_number, is_(equal_to(8)), 'Track number information is not as expected')

		#Tracking information
		assert_that(message.tracking(), is_(equal_to(tracking_id)), 'Tracking id does not match')

		tracking_info = tracking_facade.lookup(tracking_id)

		assert_that(tracking_info.tracking_events.of_type('METADATA_AVAILABLE').is_empty(), is_(False),'Tracking events of type METADATA_AVAILABLE is empty')

	def test_partial_metadata_from_file(self):

		data_dir = os.path.join(testutils.current_dirpath(__file__), 'data')
		source_file = os.path.join(data_dir, 'partial_id3taginfo.mp3')

		config = configuration.Id3TagHandlerConfigurationBuilder().override_tags(False)\
																  .offline_mode(False)\
																  .build()

		id3taghandler_actor = testutils.TestActorBuilder().withFactory(factory.Id3TagSupervisorFactory(config))\
															.withId('test-id3taghandler')\
															.terminationMoratorium(20)\
															.terminate_system(False)\
															.terminationType(messages.FileMetadataAvailable).build()

		tracking_facade = facade.MediaTrackingFacade.create_within(id3taghandler_actor.system())
		tracking_id = tracking_facade.create_tracking(source_file)

		id3taghandler_actor.tell(messages.InspectFileMetadata(source_file, tracking_id))

		assert_that(id3taghandler_actor.inspector().num_instances(messages.FileMetadataAvailable), is_(equal_to(1)), 'Total amount of FileMetadataAvailable messages received is wrong')

		message = id3taghandler_actor.inspector().get_first(messages.FileMetadataAvailable)

		assert_that(message.metadata().artist, is_(not_none()), 'Artist information is empty')
		assert_that(message.metadata().artist, is_(equal_to('Bon Jovi')), 'Artist information content is not as expected')

		assert_that(message.metadata().album, is_(not_none()), 'Album information is empty')
		assert_that(message.metadata().album, is_(equal_to('New Jersey')), 'Album information content is not as expected')

		assert_that(message.metadata().title, is_(not_none()), 'Title information is empty')
		assert_that(message.metadata().title, is_(equal_to('Ride Cowboy Ride')), 'Title information content is not as expected')

		assert_that(message.metadata().track_number, is_(not_none()), 'Track number information is empty')
		assert_that(message.metadata().track_number, is_(equal_to(8)), 'Track number information is not as expected')

		assert_that(message.tracking(), is_(equal_to(tracking_id)), 'Tracking id does not match')

		tracking_info = tracking_facade.lookup(tracking_id)

		assert_that(tracking_info.tracking_events.of_type('METADATA_AVAILABLE').is_empty(), is_(False),'Tracking events of type METADATA_AVAILABLE is empty')		

	def test_empty_metadata_from_file(self):

		data_dir = os.path.join(testutils.current_dirpath(__file__), 'data')
		source_file = os.path.join(data_dir, 'emptytaginfo.mp3')

		config = configuration.Id3TagHandlerConfigurationBuilder().override_tags(False)\
																  .offline_mode(False)\
																  .build()

		id3taghandler_actor = testutils.TestActorBuilder().withFactory(factory.Id3TagSupervisorFactory(config))\
															.withId('test-id3taghandler')\
															.terminationMoratorium(20)\
															.terminate_system(False)\
															.terminationType(messages.FileMetadataNotFullyAvailable).build()

		tracking_facade = facade.MediaTrackingFacade.create_within(id3taghandler_actor.system())
		tracking_id = tracking_facade.create_tracking(source_file)

		id3taghandler_actor.tell(messages.InspectFileMetadata(source_file, tracking_id))

		assert_that(id3taghandler_actor.inspector().num_instances(messages.FileMetadataNotFullyAvailable), is_(equal_to(1)), 'Total amount of FileMetadataNotFullyAvailable messages received is wrong')

		message = id3taghandler_actor.inspector().get_first(messages.FileMetadataNotFullyAvailable)

		assert_that(message.source_file(), is_(not_none()), 'Source file information is empty')
		assert_that(message.tracking(), is_(equal_to(tracking_id)), 'Tracking id does not match')

		tracking_info = tracking_facade.lookup(tracking_id)

		assert_that(tracking_info.tracking_events.of_type('METADATA_NOT_AVAILABLE_FAILURE').is_empty(), is_(False),'Tracking events of type METADATA_NOT_AVAILABLE is empty')		

	def test_non_resolvable_metadata_from_file(self):

		data_dir = os.path.join(testutils.current_dirpath(__file__), 'data')
		source_file = os.path.join(data_dir, 'nonresolvable_id3taginfo.mp3')

		config = configuration.Id3TagHandlerConfigurationBuilder().override_tags(False)\
																  .offline_mode(False)\
																  .build()

		id3taghandler_actor = testutils.TestActorBuilder().withFactory(factory.Id3TagSupervisorFactory(config))\
															.withId('test-id3taghandler')\
															.terminationMoratorium(20)\
															.terminate_system(False)\
															.terminationType(messages.FileMetadataNotFullyAvailable).build()

		tracking_facade = facade.MediaTrackingFacade.create_within(id3taghandler_actor.system())
		tracking_id = tracking_facade.create_tracking(source_file)

		id3taghandler_actor.tell(messages.InspectFileMetadata(source_file, tracking_id))

		assert_that(id3taghandler_actor.inspector().num_instances(messages.FileMetadataNotFullyAvailable), is_(equal_to(1)), 'Total amount of FileMetadataNotFullyAvailable messages received is wrong')

		message = id3taghandler_actor.inspector().get_first(messages.FileMetadataNotFullyAvailable)

		assert_that(message.source_file(), is_(not_none()), 'Source file information is empty')
		assert_that(message.tracking(), is_(equal_to(tracking_id)), 'Tracking id does not match')

		tracking_info = tracking_facade.lookup(tracking_id)

		assert_that(tracking_info.tracking_events.of_type('METADATA_NOT_AVAILABLE_FAILURE').is_empty(), is_(False),'Tracking events of type METADATA_NOT_AVAILABLE is empty')

	def test_wrong_filepath(self):

		data_dir = os.path.join(testutils.current_dirpath(__file__), 'data')
		source_file = os.path.join(data_dir, 'mpty_id3taginfo.mp3')

		config = configuration.Id3TagHandlerConfigurationBuilder().override_tags(False)\
																  .offline_mode(False)\
																  .build()

		id3taghandler_actor = testutils.TestActorBuilder().withFactory(factory.Id3TagSupervisorFactory(config))\
															.withId('test-id3taghandler')\
															.terminationMoratorium(20)\
															.terminate_system(False)\
															.terminationType(messages.FileMetadataCouldNotBeEvaluated).build()

		tracking_facade = facade.MediaTrackingFacade.create_within(id3taghandler_actor.system())
		tracking_id = tracking_facade.create_tracking(source_file)

		id3taghandler_actor.tell(messages.InspectFileMetadata(source_file, tracking_id))

		assert_that(id3taghandler_actor.inspector().num_instances(messages.FileMetadataCouldNotBeEvaluated), is_(equal_to(1)), 'Total amount of FileMetadataCouldNotBeEvaluated messages received is wrong')

		message = id3taghandler_actor.inspector().get_first(messages.FileMetadataCouldNotBeEvaluated)

		assert_that(message.source_file(), is_(not_none()), 'Source file information is empty')
		assert_that(message.tracking(), is_(equal_to(tracking_id)), 'Tracking id does not match')

		tracking_info = tracking_facade.lookup(tracking_id)

		assert_that(tracking_info.tracking_events.of_type('METADATA_EVALUATION_FAILURE').is_empty(), is_(False),'Tracking events of type METADATA_EVALUATION_FAILED is empty')

	def test_override_metadata_from_file(self):

		data_dir = os.path.join(testutils.current_dirpath(__file__), 'data')
		source_file = os.path.join(data_dir, '09-override_id3taginfo.mp3')

		config = configuration.Id3TagHandlerConfigurationBuilder().override_tags(True)\
																  .offline_mode(False)\
																  .build()

		id3taghandler_actor = testutils.TestActorBuilder().withFactory(factory.Id3TagSupervisorFactory(config))\
															.withId('test-id3taghandler')\
															.terminationMoratorium(20)\
															.terminate_system(False)\
															.terminationType(messages.FileMetadataAvailable).build()

		tracking_facade = facade.MediaTrackingFacade.create_within(id3taghandler_actor.system())
		tracking_id = tracking_facade.create_tracking(source_file)

		id3taghandler_actor.tell(messages.InspectFileMetadata(source_file, tracking_id))

		assert_that(id3taghandler_actor.inspector().num_instances(messages.FileMetadataAvailable), is_(equal_to(1)), 'Total amount of FileMetadataAvailable messages received is wrong')

		message = id3taghandler_actor.inspector().get_first(messages.FileMetadataAvailable)

		assert_that(message.metadata().artist, is_(not_none()), 'Artist information is empty')
		assert_that(message.metadata().artist, is_(equal_to('Bon Jovi')), 'Artist information content is not as expected')

		assert_that(message.metadata().album, is_(not_none()), 'Album information is empty')
		assert_that(message.metadata().album, is_(equal_to('New Jersey')), 'Album information content is not as expected')

		assert_that(message.metadata().title, is_(not_none()), 'Title information is empty')
		assert_that(message.metadata().title, is_(equal_to('Ride Cowboy Ride')), 'Title information content is not as expected')

		assert_that(message.metadata().track_number, is_(not_none()), 'Track number information is empty')
		assert_that(message.metadata().track_number, is_(equal_to(9)), 'Track number information is not as expected')

		assert_that(message.tracking(), is_(equal_to(tracking_id)), 'Tracking id does not match')

		tracking_info = tracking_facade.lookup(tracking_id)

		assert_that(tracking_info.tracking_events.of_type('METADATA_AVAILABLE').is_empty(), is_(False),'Tracking events of type METADATA_AVAILABLE is empty')

	def test_offline_mode(self):

		data_dir = os.path.join(testutils.current_dirpath(__file__), 'data')
		source_file = os.path.join(data_dir, '09-offline_mode.mp3')

		config = configuration.Id3TagHandlerConfigurationBuilder().override_tags(False)\
																  .offline_mode(True)\
																  .build()

		id3taghandler_actor = testutils.TestActorBuilder().withFactory(factory.Id3TagSupervisorFactory(config))\
															.withId('test-id3taghandler')\
															.terminationMoratorium(20)\
															.terminate_system(False)\
															.terminationType(messages.FileMetadataNotFullyAvailable).build()

		tracking_facade = facade.MediaTrackingFacade.create_within(id3taghandler_actor.system())
		tracking_id = tracking_facade.create_tracking(source_file)

		id3taghandler_actor.tell(messages.InspectFileMetadata(source_file, tracking_id))

		assert_that(id3taghandler_actor.inspector().num_instances(messages.FileMetadataNotFullyAvailable), is_(equal_to(1)), 'Total amount of FileMetadataNotFullyAvailable messages received is wrong')

		message = id3taghandler_actor.inspector().get_first(messages.FileMetadataNotFullyAvailable)

		assert_that(message.tracking(), is_(equal_to(tracking_id)), 'Tracking id does not match')

		tracking_info = tracking_facade.lookup(tracking_id)

		assert_that(tracking_info.tracking_events.of_type('METADATA_NOT_AVAILABLE_FAILURE').is_empty(), is_(False),'Tracking events of type METADATA_NOT_AVAILABLE_FAILURE is empty')		
