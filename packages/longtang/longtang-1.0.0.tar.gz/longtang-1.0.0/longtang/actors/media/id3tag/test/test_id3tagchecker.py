import unittest
import os

from longtang.actors import testutils
from longtang.actors.media.id3tag import id3tagchecker, messages
from hamcrest import *


class TestID3TagCheckerActor(unittest.TestCase):

	def test_with_id3taginfo(self):
		data_dir = os.path.join(testutils.current_dirpath(__file__), 'data')

		id3tag_tester = testutils.TestActorBuilder().withType(id3tagchecker.ID3TagCheckerActor).build()

		source_file = os.path.join(data_dir, 'withtaginfo.mp3')

		id3tag_tester.tell(messages.CheckFileMetadata(source_file,'tracking-id'))

		assert_that(id3tag_tester.inspector().num_instances(messages.FileMetadataIsComplete), is_(equal_to(1)), 'Total amount of FileMetadataIsComplete messages received is wrong')

		message = id3tag_tester.inspector().get_first(messages.FileMetadataIsComplete)

		assert_that(message.source(), is_(equal_to(source_file)), 'Source file is not present in response')
		assert_that(message.metadata().artist, is_(equal_to('Bon Jovi')), 'Artist is not present within metadata')
		assert_that(message.metadata().album, is_(equal_to('New Jersey')), 'Album is not present within metadata')
		assert_that(message.metadata().title, is_(equal_to('Ride Cowboy Ride')), 'Title is not present within metadata')
		assert_that(message.metadata().track_number, is_(equal_to(8)), 'Track is not present within metadata')
		assert_that(message.metadata().track_number, is_(equal_to(8)), 'Track is not present within metadata')
		assert_that(message.tracking(), is_(equal_to('tracking-id')), 'Tracking id not present within message')

	def test_without_id3taginfo(self):
		data_dir = os.path.join(testutils.current_dirpath(__file__), 'data')

		id3tag_tester = testutils.TestActorBuilder().withType(id3tagchecker.ID3TagCheckerActor).build()

		source_file = os.path.join(data_dir, 'withouttaginfo.mp3')

		id3tag_tester.tell(messages.CheckFileMetadata(source_file, 'tracking-id'))

		assert_that(id3tag_tester.inspector().num_instances(messages.FileMetadataIsIncomplete), is_(equal_to(1)), 'Total amount of FileMetadataIsIncomplete messages received is wrong')

		message = id3tag_tester.inspector().get_first(messages.FileMetadataIsIncomplete)

		assert_that(message.source(), is_(equal_to(source_file)), 'Source file is not present in response')
		assert_that(message.metadata().artist, is_(none()), 'Artist is not present within metadata')
		assert_that(message.metadata().album, is_(none()), 'Album is not present within metadata')
		assert_that(message.metadata().title, is_(none()), 'Title is not present within metadata')
		assert_that(message.metadata().track_number, is_(none()), 'Track is not present within metadata')
		assert_that(message.tracking(), is_(equal_to('tracking-id')), 'Tracking id not present within message')

	def test_empty_id3taginfo(self):
		data_dir = os.path.join(testutils.current_dirpath(__file__), 'data')

		id3tag_tester = testutils.TestActorBuilder().withType(id3tagchecker.ID3TagCheckerActor).build()

		source_file = os.path.join(data_dir, 'emptytaginfo.mp3')

		id3tag_tester.tell(messages.CheckFileMetadata(source_file, 'tracking-id'))

		assert_that(id3tag_tester.inspector().num_instances(messages.FileMetadataIsIncomplete), is_(equal_to(1)), 'Total amount of FileMetadataIsIncomplete messages received is wrong')

		message = id3tag_tester.inspector().get_first(messages.FileMetadataIsIncomplete)

		assert_that(message.source(), is_(equal_to(source_file)), 'Source file is not present in response')
		assert_that(message.metadata().artist, is_(none()), 'Artist is not present within metadata')
		assert_that(message.metadata().album, is_(none()), 'Album is not present within metadata')
		assert_that(message.metadata().title, is_(none()), 'Title is not present within metadata')
		assert_that(message.metadata().track_number, is_(none()), 'Track is not present within metadata')
		assert_that(message.tracking(), is_(equal_to('tracking-id')), 'Tracking id not present within message')

	def test_wrong_file_path(self):
		data_dir = os.path.join(testutils.current_dirpath(__file__), 'data')

		id3tag_tester = testutils.TestActorBuilder().withType(id3tagchecker.ID3TagCheckerActor).build()

		source_file = os.path.join(data_dir, '_id3taginfo.mp3')

		id3tag_tester.tell(messages.CheckFileMetadata(source_file, 'tracking-id'))

		assert_that(id3tag_tester.inspector().num_instances(messages.FileMetadataCouldNotBeChecked), is_(equal_to(1)), 'Total amount of FileMetadataCouldNotBeChecked messages received is wrong')

		message = id3tag_tester.inspector().get_first(messages.FileMetadataCouldNotBeChecked)

		assert_that(message.source_file(), is_(not_none()), 'Source file is not present in response')
		assert_that(message.source_file(), is_(equal_to(source_file)), 'Source file is not present in response')
		assert_that(message.tracking(), is_(equal_to('tracking-id')), 'Tracking id is not present in response')

	def test_missing_track_number_1digits(self):
		data_dir = os.path.join(testutils.current_dirpath(__file__), 'data')

		id3tag_tester = testutils.TestActorBuilder().withType(id3tagchecker.ID3TagCheckerActor).build()

		source_file = os.path.join(data_dir, '8_id3taginfo.mp3')

		id3tag_tester.tell(messages.CheckFileMetadata(source_file,'tracking-id'))

		assert_that(id3tag_tester.inspector().num_instances(messages.FileMetadataIsComplete), is_(equal_to(1)), 'Total amount of FileMetadataIsComplete messages received is wrong')

		message = id3tag_tester.inspector().get_first(messages.FileMetadataIsComplete)

		assert_that(message.source(), is_(equal_to(source_file)), 'Source file is not present in response')
		assert_that(message.metadata().artist, is_(equal_to('Bon Jovi')), 'Artist is not present within metadata')
		assert_that(message.metadata().album, is_(equal_to('New Jersey')), 'Album is not present within metadata')
		assert_that(message.metadata().title, is_(equal_to('Ride Cowboy Ride')), 'Title is not present within metadata')
		assert_that(message.metadata().track_number, is_(equal_to(8)), 'Track is not present within metadata')
		assert_that(message.metadata().track_number, is_(equal_to(8)), 'Track is not present within metadata')
		assert_that(message.tracking(), is_(equal_to('tracking-id')), 'Tracking id not present within message')

	def test_missing_track_number_2digits(self):
		data_dir = os.path.join(testutils.current_dirpath(__file__), 'data')

		id3tag_tester = testutils.TestActorBuilder().withType(id3tagchecker.ID3TagCheckerActor).build()

		source_file = os.path.join(data_dir, '08_id3taginfo.mp3')

		id3tag_tester.tell(messages.CheckFileMetadata(source_file,'tracking-id'))

		assert_that(id3tag_tester.inspector().num_instances(messages.FileMetadataIsComplete), is_(equal_to(1)), 'Total amount of FileMetadataIsComplete messages received is wrong')

		message = id3tag_tester.inspector().get_first(messages.FileMetadataIsComplete)

		assert_that(message.source(), is_(equal_to(source_file)), 'Source file is not present in response')
		assert_that(message.metadata().artist, is_(equal_to('Bon Jovi')), 'Artist is not present within metadata')
		assert_that(message.metadata().album, is_(equal_to('New Jersey')), 'Album is not present within metadata')
		assert_that(message.metadata().title, is_(equal_to('Ride Cowboy Ride')), 'Title is not present within metadata')
		assert_that(message.metadata().track_number, is_(equal_to(8)), 'Track is not present within metadata')
		assert_that(message.metadata().track_number, is_(equal_to(8)), 'Track is not present within metadata')
		assert_that(message.tracking(), is_(equal_to('tracking-id')), 'Tracking id not present within message')

	def test_missing_track_number_3digits(self):
		data_dir = os.path.join(testutils.current_dirpath(__file__), 'data')

		id3tag_tester = testutils.TestActorBuilder().withType(id3tagchecker.ID3TagCheckerActor).build()

		source_file = os.path.join(data_dir, '010_id3taginfo.mp3') 

		id3tag_tester.tell(messages.CheckFileMetadata(source_file,'tracking-id'))

		assert_that(id3tag_tester.inspector().num_instances(messages.FileMetadataIsComplete), is_(equal_to(1)), 'Total amount of FileMetadataIsComplete messages received is wrong')

		message = id3tag_tester.inspector().get_first(messages.FileMetadataIsComplete)

		assert_that(message.source(), is_(equal_to(source_file)), 'Source file is not present in response')
		assert_that(message.metadata().artist, is_(equal_to('Bon Jovi')), 'Artist is not present within metadata')
		assert_that(message.metadata().album, is_(equal_to('New Jersey')), 'Album is not present within metadata')
		assert_that(message.metadata().title, is_(equal_to('Ride Cowboy Ride')), 'Title is not present within metadata')
		assert_that(message.metadata().track_number, is_(equal_to(10)), 'Track is not present within metadata')
		assert_that(message.metadata().track_number, is_(equal_to(10)), 'Track is not present within metadata')
		assert_that(message.tracking(), is_(equal_to('tracking-id')), 'Tracking id not present within message')			