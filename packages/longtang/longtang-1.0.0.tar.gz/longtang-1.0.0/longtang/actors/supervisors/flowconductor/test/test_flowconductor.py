#https://github.com/hamcrest/PyHamcrest
#http://packages.python.org/PyHamcrest/

import gevent
import unittest
import os

from hamcrest import *
from longtang.actors.supervisors.flowconductor import flowconductor, messages, factory
from longtang.actors import testutils
from longtang.system import system, exceptions
from longtang.config import configuration
from longtang.actors.tracking import tracking, facade
from longtang.actors.media.id3tag import domain

class TestFlowConductorActor(unittest.TestCase):

	def setUp(cls):
		global base_from_test_dir
		global base_to_test_dir

		base_from_test_dir = testutils.create_tmp_dir(suffix='flowconductor_test_from')
		base_to_test_dir = testutils.create_tmp_dir(suffix='flowconductor_test_to')

	def tearDown(cls):
		testutils.remove_tmp_dir(base_from_test_dir)
		testutils.remove_tmp_dir(base_to_test_dir)

	def test_creation(self):

		data_dir = os.path.join(testutils.current_dirpath(__file__), 'data')

		config_builder = configuration.LongTangConfigurationBuilder()
		config = config_builder.read_from(base_from_test_dir).generate_at(base_to_test_dir).build()

		actor_system = system.ActorSystem()
		main_actor = actor_system.with_factory(factory.FlowConductorSupervisorFactory(config),'flowconductor-test-actor')
		
		try:		
			assert_that(actor_system.find_by_id('flowconductor-test-actor'), is_not(None), 'Main actor does not exist within system')

			assert_that(actor_system.find_by_id('id3taghandler-actor'), is_not(None), 'Id3tag handler poller actor does not exist within system')
			assert_that(actor_system.find_by_id('filepackaging-actor'), is_not(None), 'File packaging poller actor does not exist within system')

			assert_that(actor_system.find_by_id('id3taghandler-actor').parent(), is_(equal_to(actor_system.find_by_id('flowconductor-test-actor'))),'Parent actor is not correctly assigned')
			assert_that(actor_system.find_by_id('filepackaging-actor').parent(), is_(equal_to(actor_system.find_by_id('flowconductor-test-actor'))),'Parent actor is not correctly assigned')

		except exceptions.ActorNotFound as e:
			self.fail(str(e))

		actor_system.shutdown()

	def test_single_file_processing_with_tags(self):
		
		data_dir = os.path.join(testutils.current_dirpath(__file__), 'data')

		source_file_with_id3tag = testutils.copy_to_tmp(source=os.path.join(data_dir, 'with_id3taginfo.mp3'),suffix='.tmp.mp3',dir=base_from_test_dir)

		config_builder = configuration.LongTangConfigurationBuilder()
		config = config_builder.read_from(base_from_test_dir).generate_at(base_to_test_dir).build()

		flowconductor_actor = testutils.TestActorBuilder().withFactory(factory.FlowConductorSupervisorFactory(config))\
															.withId('flowconductor-test-actor')\
															.terminationMoratorium(10)\
															.terminate_system(False)\
															.terminationType(messages.MediaFileHasBeenProcessed).build()

		tracking_facade = facade.MediaTrackingFacade.create_within(flowconductor_actor.system())
		tracking_id = tracking_facade.create_tracking(source_file_with_id3tag)

		flowconductor_actor.tell(messages.MediaFileAvailable(source_file_with_id3tag, tracking_id))

		assert_that(flowconductor_actor.inspector().num_instances(messages.MediaFileHasBeenProcessed), is_(equal_to(1)), 'Total amount of MediaFileHasBeenProcessed messages received is wrong')

		message = flowconductor_actor.inspector().get_first(messages.MediaFileHasBeenProcessed)		

		#location
		full_dir_path=os.path.join(base_to_test_dir, 'Bon Jovi', 'New Jersey')
		full_file_path=os.path.join(full_dir_path,'08 - Ride Cowboy Ride.mp3')

		assert_that(os.path.isdir(full_dir_path), is_(equal_to(True)), 'Artist or album directory does not exist or full name is not right')
		assert_that(os.path.isfile(full_file_path), is_(equal_to(True)),'Media file in target path does not exist')

		#Tracking information
		assert_that(message.tracking(), is_(equal_to(tracking_id)), 'Tracking id does not match')

		tracking_info = tracking_facade.lookup(tracking_id)

		assert_that(tracking_info.mediafile.destinationpath, is_(equal_to(full_file_path)),'Filepath information on received message is wrong')

		#id3tag
		reader = domain.ID3TagReaderFactory.createFromType(full_file_path)

		assert_that(reader.artist(), is_(equal_to('Bon Jovi')), 'id3tag content for artist does not match')
		assert_that(reader.title(), is_(equal_to('Ride Cowboy Ride')), 'id3tag content for title does not match')
		assert_that(reader.album(), is_(equal_to('New Jersey')), 'id3tag content for album does not match')
		assert_that(reader.track_number(), is_(equal_to('8')), 'id3tag content for track number does not match')

	def test_single_file_processing_invalid_metadata(self):
		data_dir = os.path.join(testutils.current_dirpath(__file__), 'data')

		source_file_with_id3tag = testutils.copy_to_tmp(source=os.path.join(data_dir, 'invalid_metadata.mp3'),suffix='.tmp.mp3',dir=base_from_test_dir)		

		config_builder = configuration.LongTangConfigurationBuilder()
		config = config_builder.read_from(base_from_test_dir).generate_at(base_to_test_dir).build()

		flowconductor_actor = testutils.TestActorBuilder().withFactory(factory.FlowConductorSupervisorFactory(config))\
															.withId('flowconductor-test-actor')\
															.terminationMoratorium(10)\
															.terminate_system(True)\
															.terminationType(messages.MediaFileProcessingFailed).build()

		tracking_facade = facade.MediaTrackingFacade.create_within(flowconductor_actor.system())
		tracking_id = tracking_facade.create_tracking(source_file_with_id3tag)

		flowconductor_actor.tell(messages.MediaFileAvailable(source_file_with_id3tag, tracking_id))

		assert_that(flowconductor_actor.inspector().num_instances(messages.MediaFileProcessingFailed), is_(equal_to(1)), 'Total amount of MediaFileProcessingFailed messages received is wrong')

		message = flowconductor_actor.inspector().get_first(messages.MediaFileProcessingFailed)

		assert_that(message.tracking(), is_(equal_to(tracking_id)), 'Tracking id does not match')

	def test_single_file_processing_nonexisting_path(self):

		config_builder = configuration.LongTangConfigurationBuilder()
		config = config_builder.read_from(base_from_test_dir).generate_at(base_to_test_dir).build()

		flowconductor_actor = testutils.TestActorBuilder().withFactory(factory.FlowConductorSupervisorFactory(config))\
															.withId('flowconductor-test-actor')\
															.terminationMoratorium(10)\
															.terminate_system(True)\
															.terminationType(messages.MediaFileProcessingFailed).build()

		tracking_facade = facade.MediaTrackingFacade.create_within(flowconductor_actor.system())
		tracking_id = tracking_facade.create_tracking('/dummy.mp3')

		flowconductor_actor.tell(messages.MediaFileAvailable('/dummy.mp3', tracking_id))

		assert_that(flowconductor_actor.inspector().num_instances(messages.MediaFileProcessingFailed), is_(equal_to(1)), 'Total amount of MediaFileProcessingFailed messages received is wrong')

		message = flowconductor_actor.inspector().get_first(messages.MediaFileProcessingFailed)

		assert_that(message.tracking(), is_(equal_to(tracking_id)), 'Tracking id does not match')

	def test_single_file_processing_nonexisting_destinationpath(self):

		data_dir = os.path.join(testutils.current_dirpath(__file__), 'data')

		source_file_with_id3tag = testutils.copy_to_tmp(source=os.path.join(data_dir, 'with_id3taginfo.mp3'),suffix='.tmp.mp3',dir=base_from_test_dir)

		config_builder = configuration.LongTangConfigurationBuilder()
		config = config_builder.read_from(base_from_test_dir).generate_at('/dummy').build()

		flowconductor_actor = testutils.TestActorBuilder().withFactory(factory.FlowConductorSupervisorFactory(config))\
															.withId('flowconductor-test-actor')\
															.terminationMoratorium(10)\
															.terminate_system(False)\
															.terminationType(messages.MediaFileProcessingFailed).build()

		tracking_facade = facade.MediaTrackingFacade.create_within(flowconductor_actor.system())
		tracking_id = tracking_facade.create_tracking(source_file_with_id3tag)

		flowconductor_actor.tell(messages.MediaFileAvailable(source_file_with_id3tag, tracking_id))

		assert_that(flowconductor_actor.inspector().num_instances(messages.MediaFileProcessingFailed), is_(equal_to(1)), 'Total amount of MediaFileProcessingFailed messages received is wrong')

		message = flowconductor_actor.inspector().get_first(messages.MediaFileProcessingFailed)

		assert_that(message.tracking(), is_(equal_to(tracking_id)), 'Tracking id does not match')	

if __name__ == '__main__':
	unittest.main()    