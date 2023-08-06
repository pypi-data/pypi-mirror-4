# -*- coding: utf-8 -*-

import gevent
import unittest
import os

from hamcrest import *
from longtang.actors.supervisors.main import main, messages, factory
from longtang.actors.supervisors.flowconductor import flowconductor
from longtang.actors.inbound import filepoller
from longtang.actors import testutils
from longtang.system import system, exceptions
from longtang.config import configuration
from longtang.common import interactions
from longtang.actors.media.id3tag import domain

class TestMainActor(unittest.TestCase):

	def setUp(cls):
		global base_from_test_dir
		global base_to_test_dir

		base_from_test_dir = testutils.create_tmp_dir(suffix='maintest_from')
		base_to_test_dir = testutils.create_tmp_dir(suffix='maintest_to')

	def tearDown(cls):
		testutils.remove_tmp_dir(base_from_test_dir) 
		testutils.remove_tmp_dir(base_to_test_dir)

	def test_creation(self):

		data_dir = os.path.join(testutils.current_dirpath(__file__), 'data')

		config_builder = configuration.LongTangConfigurationBuilder()
		config = config_builder.read_from(base_from_test_dir).generate_at(base_to_test_dir).build()

		actor_system = system.ActorSystem()
		main_actor = actor_system.with_factory(factory.MainSupervisorFactory(config),'main-actor')
		
		try:		
			assert_that(actor_system.find_by_id('main-actor'), is_not(None), 'Main actor does not exist within system')

			assert_that(actor_system.find_by_id('file-poller-actor'), is_not(None), 'File poller actor does not exist within system')
			assert_that(actor_system.find_by_id('flowconductor-actor'), is_not(None), 'Flowconductor actor actor does not exist within system')

			assert_that(actor_system.find_by_id('file-poller-actor').parent(), is_(equal_to(actor_system.find_by_id('main-actor'))),'Parent actor is not correctly assigned')
			assert_that(actor_system.find_by_id('flowconductor-actor').parent(), is_(equal_to(actor_system.find_by_id('main-actor'))),'Parent actor is not correctly assigned')

			assert_that(actor_system.find_by_id('file-poller-actor')._instance(), is_(instance_of(filepoller.FilePoller)), 'File poller actor is not of the right type')
			assert_that(actor_system.find_by_id('flowconductor-actor')._instance(), is_(instance_of(flowconductor.FlowConductorSupervisor)), 'Flow conductor actor is not of the right type')

		except exceptions.ActorNotFound as e:
			self.fail(str(e))

		actor_system.shutdown()

	def test_single_file_processing_with_tags(self):
		
		data_dir = os.path.join(testutils.current_dirpath(__file__), 'data')

		source_file_with_id3tag = testutils.copy_to_tmp(source=os.path.join(data_dir, 'with_id3taginfo.mp3'),suffix='.tmp.mp3',dir=base_from_test_dir)

		config_builder = configuration.LongTangConfigurationBuilder()
		config = config_builder.read_from(base_from_test_dir).generate_at(base_to_test_dir).build()

		actor_system = system.ActorSystem()
		main_ref = actor_system.with_factory(factory.MainSupervisorFactory(config),'main-actor')

		interactions.InteractionPatterns.ask(actor_system, main_ref, messages.KickOffMediaProcessing())		

		full_dir_path=os.path.join(base_to_test_dir, 'Bon Jovi', 'New Jersey')
		full_file_path=os.path.join(full_dir_path,'08 - Ride Cowboy Ride.mp3')

		assert_that(os.path.isdir(full_dir_path), is_(equal_to(True)), 'Artist or album directory does not exist or full name is not right')
		assert_that(os.path.isfile(full_file_path), is_(equal_to(True)),'Media file in target path does not exist')

		#id3tag
		reader = domain.ID3TagReaderFactory.createFromType(full_file_path)

		assert_that(reader.artist(), is_(equal_to('Bon Jovi')), 'id3tag content for artist does not match')
		assert_that(reader.title(), is_(equal_to('Ride Cowboy Ride')), 'id3tag content for title does not match')
		assert_that(reader.album(), is_(equal_to('New Jersey')), 'id3tag content for album does not match')
		assert_that(reader.track_number(), is_(equal_to('8')), 'id3tag content for track number does not match')

	def test_multiple_file_encoding_processing_with_tags(self):
		
		data_dir = os.path.join(testutils.current_dirpath(__file__), 'data','multiple_encodings')

		#source_file_with_id3tag = testutils.copy_to_tmp(source=os.path.join(data_dir, 'with_id3taginfo.mp3'),suffix='.tmp.mp3',dir=base_from_test_dir)

		config_builder = configuration.LongTangConfigurationBuilder()
		config = config_builder.read_from(data_dir).generate_at(base_to_test_dir).build()

		actor_system = system.ActorSystem()
		main_ref = actor_system.with_factory(factory.MainSupervisorFactory(config),'main-actor')

		interactions.InteractionPatterns.ask(actor_system, main_ref, messages.KickOffMediaProcessing())	

		#full_dir_path=os.path.join(base_to_test_dir, 'Bon Jovi', 'New Jersey')
		#full_file_path=os.path.join(full_dir_path,'08 - Ride Cowboy Ride.mp3')

		#assert_that(os.path.isdir(full_dir_path), is_(equal_to(True)), 'Artist or album directory does not exist or full name is not right')
		#assert_that(os.path.isfile(full_file_path), is_(equal_to(True)),'Media file in target path does not exist')

		#id3tag
		#reader = domain.ID3TagReaderFactory.createFromType(full_file_path)

		#assert_that(reader.artist(), is_(equal_to('Bon Jovi')), 'id3tag content for artist does not match')
		#assert_that(reader.title(), is_(equal_to('Ride Cowboy Ride')), 'id3tag content for title does not match')
		#assert_that(reader.album(), is_(equal_to('New Jersey')), 'id3tag content for album does not match')
		#assert_that(reader.track_number(), is_(equal_to('8')), 'id3tag content for track number does not match')		

	def test_multiple_file_processing_with_tags(self): 
		
		data_dir = os.path.join(testutils.current_dirpath(__file__), 'data', 'multiple')

		config_builder = configuration.LongTangConfigurationBuilder()
		config = config_builder.read_from(data_dir).generate_at(base_to_test_dir).build()

		actor_system = system.ActorSystem()
		main_ref = actor_system.with_factory(factory.MainSupervisorFactory(config),'main-actor')

		interactions.InteractionPatterns.ask(actor_system, main_ref, messages.KickOffMediaProcessing()) 

		full_dir_path_source1=os.path.join(base_to_test_dir, 'The Aristocrats', 'Boing, We\'ll Do It Live!')
		full_file_path_source1=os.path.join(full_dir_path_source1,'08 - A Very Metal Introduction.mp3')

		assert_that(os.path.isdir(full_dir_path_source1), is_(equal_to(True)), 'Artist or album directory does not exist or full name is not right')
		assert_that(os.path.isfile(full_file_path_source1), is_(equal_to(True)),'Media file in target path does not exist')

		reader = domain.ID3TagReaderFactory.createFromType(full_file_path_source1)

		assert_that(reader.artist(), is_(equal_to('The Aristocrats')), 'id3tag content for artist does not match')
		assert_that(reader.title(), is_(equal_to('A Very Metal Introduction')), 'id3tag content for title does not match')
		assert_that(reader.album(), is_(equal_to('Boing, We\'ll Do It Live!')), 'id3tag content for album does not match')
		assert_that(reader.track_number(), is_(equal_to('8')), 'id3tag content for track number does not match')

		full_dir_path_source2=os.path.join(base_to_test_dir, 'Carla Bruni', 'Quelqu\'un M\'a Dit')
		full_file_path_source2=os.path.join(full_dir_path_source2,'02 - La Dernière Minute.mp3')

		assert_that(os.path.isdir(full_dir_path_source2), is_(equal_to(True)), 'Artist or album directory does not exist or full name is not right')
		assert_that(os.path.isfile(full_file_path_source2), is_(equal_to(True)),'Media file in target path does not exist')			

		reader = domain.ID3TagReaderFactory.createFromType(full_file_path_source2)

		assert_that(reader.artist(), is_(equal_to(u'Carla Bruni')), 'id3tag content for artist does not match')
		assert_that(reader.title(), is_(equal_to(u'La Dernière Minute')), 'id3tag content for title does not match')
		assert_that(reader.album(), is_(equal_to(u'Quelqu\'un M\'a Dit')), 'id3tag content for album does not match')
		assert_that(reader.track_number(), is_(equal_to('2')), 'id3tag content for track number does not match')

		full_dir_path_source3=os.path.join(base_to_test_dir, 'Big Cock', 'Year Of The Cock')
		full_file_path_source3=os.path.join(full_dir_path_source3,'13 - Thank You, Good Night.mp3')

		assert_that(os.path.isdir(full_dir_path_source3), is_(equal_to(True)), 'Artist or album directory does not exist or full name is not right')
		assert_that(os.path.isfile(full_file_path_source3), is_(equal_to(True)),'Media file in target path does not exist')	

		reader = domain.ID3TagReaderFactory.createFromType(full_file_path_source3)

		assert_that(reader.artist(), is_(equal_to('Big Cock')), 'id3tag content for artist does not match')
		assert_that(reader.title(), is_(equal_to('Thank You, Good Night')), 'id3tag content for title does not match')
		assert_that(reader.album(), is_(equal_to('Year Of The Cock')), 'id3tag content for album does not match')
		assert_that(reader.track_number(), is_(equal_to('13')), 'id3tag content for track number does not match') 

	def test_summary_success(self):
		data_dir = os.path.join(testutils.current_dirpath(__file__), 'data', 'multiple')

		config_builder = configuration.LongTangConfigurationBuilder()
		config = config_builder.read_from(data_dir).generate_at(base_to_test_dir).build()

		actor_system = system.ActorSystem()
		main_ref = actor_system.with_factory(factory.MainSupervisorFactory(config),'main-actor')

		summary = interactions.InteractionPatterns.ask(actor_system, main_ref, messages.KickOffMediaProcessing()).summary() 

		assert_that(summary.total(), equal_to(3), 'Amount of processed files is wrong')
		assert_that(summary.total_failures(), equal_to(0), 'Amount of failed files is wrong')
		assert_that(summary.total_successes(), equal_to(3), 'Amount of successed files is wrong')

	def test_summary_failure(self):

		data_dir = os.path.join(testutils.current_dirpath(__file__), 'data')

		source_file_with_id3tag = testutils.copy_to_tmp(source=os.path.join(data_dir, 'withouttaginfo.mp3'),suffix='.tmp.mp3',dir=base_from_test_dir)

		config_builder = configuration.LongTangConfigurationBuilder()
		config = config_builder.read_from(base_from_test_dir).generate_at(base_to_test_dir).build()

		actor_system = system.ActorSystem()
		main_ref = actor_system.with_factory(factory.MainSupervisorFactory(config),'main-actor')

		summary = interactions.InteractionPatterns.ask(actor_system, main_ref, messages.KickOffMediaProcessing()).summary() 

		assert_that(summary.total(), equal_to(1), 'Amount of processed files is wrong')
		assert_that(summary.total_failures(), equal_to(1), 'Amount of failed files is wrong')
		assert_that(summary.total_successes(), equal_to(0), 'Amount of successed files is wrong')

if __name__ == '__main__':
	unittest.main()    
