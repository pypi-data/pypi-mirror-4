import unittest
import os

from longtang.actors import testutils
from longtang.actors.media.id3tag import id3tagwriter, messages, domain
from longtang.common import domain as common_domain
from hamcrest import *


class TestID3TagWriterActor(unittest.TestCase):

	def setUp(self):

		global source_file

		data_dir = os.path.join(testutils.current_dirpath(__file__), 'data')
		source_file = testutils.copy_to_tmp(source=os.path.join(data_dir, 'emptytaginfo.mp3'),suffix='.tmp.mp3')

	def tearDown(self):
		os.remove(source_file)

	def test_write_id3taginfo(self):

		id3tag_tester = testutils.TestActorBuilder().withType(id3tagwriter.ID3TagWriterActor).build()

		metadata_builder = common_domain.FileMetadataBuilder()
		metadata = metadata_builder.artist('My Test Artist').title('My Test Title').album('My Test Album').track_number('7').build()

		id3tag_tester.tell(messages.WriteFileMetadata(source_file, metadata,'tracking-id'))

		assert_that(id3tag_tester.inspector().num_instances(messages.FileMetadataUpdated), is_(equal_to(1)), 'Total amount of FileMetadataUpdated messages received is wrong')		

		message = id3tag_tester.inspector().get_first(messages.FileMetadataUpdated)

		assert_that(message.source(), is_(not_none()), 'Source file is empty')
		assert_that(message.source(), is_(equal_to(source_file)), 'Source file is not the expected value')
		assert_that(message.metadata(), is_(not_none()), 'Metadata information is empty')
		assert_that(message.metadata(), is_(instance_of(common_domain.FileMetadata)), 'Metadata information is not the right type')
		assert_that(message.tracking(), is_(equal_to('tracking-id')), 'Tracking id is missing')


	def test_written_file_id3taginfo(self):

		id3tag_tester = testutils.TestActorBuilder().withType(id3tagwriter.ID3TagWriterActor).build()

		metadata_builder = common_domain.FileMetadataBuilder()
		metadata = metadata_builder.artist('Artist#1').title('Title#1').album('Album#1').track_number('15').build()

		id3tag_tester.tell(messages.WriteFileMetadata(source_file, metadata, 'tracking-id'))

		assert_that(id3tag_tester.inspector().num_instances(messages.FileMetadataUpdated), is_(equal_to(1)), 'Total amount of FileMetadataUpdated messages received is wrong')		

		message = id3tag_tester.inspector().get_first(messages.FileMetadataUpdated)

		reader = domain.ID3TagReaderFactory.createFromType(message.source())

		assert_that(reader.artist(), is_(equal_to('Artist#1')), 'id3tag content for artist does not match')
		assert_that(reader.title(), is_(equal_to('Title#1')), 'id3tag content for title does not match')
		assert_that(reader.album(), is_(equal_to('Album#1')), 'id3tag content for album does not match')
		assert_that(reader.track_number(), is_(equal_to('15')), 'id3tag content for track number does not match')
		assert_that(message.tracking(), is_(equal_to('tracking-id')), 'Tracking id is missing')

	def test_write_id3taginfo_not_existing_file_failure(self):

		id3tag_tester = testutils.TestActorBuilder().withType(id3tagwriter.ID3TagWriterActor).build()

		metadata_builder = common_domain.FileMetadataBuilder()
		metadata = metadata_builder.artist('My Test Artist').title('My Test Title').album('My Test Album').track_number('7').build()

		id3tag_tester.tell(messages.WriteFileMetadata('dummy.mp3', metadata, 'tracking-id'))

		assert_that(id3tag_tester.inspector().num_instances(messages.WriteFileMetadataFailed), is_(equal_to(1)), 'Total amount of WriteFileMetadataFailed messages received is wrong')		

		message = id3tag_tester.inspector().get_first(messages.WriteFileMetadataFailed)

		assert_that(message.source(), is_(not_none()), 'Source file is empty')
		assert_that(message.metadata(), is_(not_none()), 'Metadata information is empty')
		assert_that(message.reason(), is_(not_none()), 'Reason information is empty')
		assert_that(message.source_message(), is_(not_none()), 'Source message information is empty')
		assert_that(message.tracking(), is_(equal_to('tracking-id')), 'Tracking id is missing')

	def test_write_id3taginfo_missing_metadata_failure(self):

		id3tag_tester = testutils.TestActorBuilder().withType(id3tagwriter.ID3TagWriterActor).build()

		metadata_builder = common_domain.FileMetadataBuilder()
		metadata = metadata_builder.artist('My Test Artist').title('My Test Title').album(None).track_number('7').build()

		id3tag_tester.tell(messages.WriteFileMetadata(source_file, metadata, 'tracking-id'))

		assert_that(id3tag_tester.inspector().num_instances(messages.WriteFileMetadataFailed), is_(equal_to(1)), 'Total amount of WriteFileMetadataFailed messages received is wrong')		

		message = id3tag_tester.inspector().get_first(messages.WriteFileMetadataFailed)

		assert_that(message.source(), is_(not_none()), 'Source file is empty')
		assert_that(message.metadata(), is_(not_none()), 'Metadata information is empty')
		assert_that(message.reason(), is_(not_none()), 'Reason information is empty')
		assert_that(message.source_message(), is_(not_none()), 'Source message information is empty')
		assert_that(message.tracking(), is_(equal_to('tracking-id')), 'Tracking id is missing')		
