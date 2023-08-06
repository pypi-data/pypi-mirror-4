import unittest
import os

from longtang.actors import testutils
from longtang.actors.outbound.musicbrainz import musicbrainz, messages
from longtang.common import domain as common_domain
from hamcrest import *


class TestMusicBrainzActor(unittest.TestCase):

	def test_single_file_found(self):

		data_dir = os.path.join(testutils.current_dirpath(__file__), 'data')

		accoustic_tester = testutils.TestActorBuilder().withType(musicbrainz.MusicMetadataActor).build()

		source_file = os.path.join(data_dir, 'sample.mp3')

		accoustic_tester.tell(messages.LookupFileMetadata(source_file, 'tracking-id'))

		assert_that(accoustic_tester.inspector().num_instances(messages.FileMetadataFound), is_(equal_to(1)), 'Total amount of FileMetadataFound messages received is wrong')

		message = accoustic_tester.inspector().get_first(messages.FileMetadataFound)

		assert_that(message.source(), is_(equal_to(source_file)), 'Source file is not present in response')
		assert_that(message.metadata().artist, is_(equal_to('Bon Jovi')), 'Artist is not present within metadata')
		assert_that(message.metadata().album, is_(equal_to('New Jersey')), 'Album is not present within metadata')
		assert_that(message.metadata().title, is_(equal_to('Ride Cowboy Ride')), 'Album is not present within metadata')
		assert_that(message.tracking(), is_(equal_to('tracking-id')), 'Tracking id is missing')

	def test_file_not_found(self):
		data_dir = os.path.join(testutils.current_dirpath(__file__), 'data')

		accoustic_tester = testutils.TestActorBuilder().withType(musicbrainz.MusicMetadataActor).build()

		source_file = os.path.join(data_dir, 'not_found.mp3')

		accoustic_tester.tell(messages.LookupFileMetadata(source_file, 'tracking-id'))

		assert_that(accoustic_tester.inspector().num_instances(messages.FileMetadataNotFound), is_(equal_to(1)), 'Total amount of FileMetadataNotFound messages received is wrong')

		message = accoustic_tester.inspector().get_first(messages.FileMetadataNotFound)

		assert_that(message.tracking(), is_(equal_to('tracking-id')), 'Tracking id is missing')

	def test_override_metadata(self):

		data_dir = os.path.join(testutils.current_dirpath(__file__), 'data')

		accoustic_tester = testutils.TestActorBuilder().withType(musicbrainz.MusicMetadataActor).build()

		source_file = os.path.join(data_dir, '09-override_id3taginfo.mp3')		

		metadata_builder = common_domain.FileMetadataBuilder()
		metadata = metadata_builder.artist('My Test Artist').title('My Test Title').album('My Test Album').track_number('7').build()		

		accoustic_tester.tell(messages.OverrideFileMetadata(source_file, metadata, 'tracking-id'))		

		assert_that(accoustic_tester.inspector().num_instances(messages.OverrideFileMetadataDone), is_(equal_to(1)), 'Total amount of OverrideFileMetadataDone messages received is wrong')

		message = accoustic_tester.inspector().get_first(messages.OverrideFileMetadataDone)

		assert_that(message.source(), is_(equal_to(source_file)), 'Source file is not present in response')
		assert_that(message.metadata().artist, is_(equal_to('Bon Jovi')), 'Artist is not present within metadata')
		assert_that(message.metadata().album, is_(equal_to('New Jersey')), 'Album is not present within metadata')
		assert_that(message.metadata().title, is_(equal_to('Ride Cowboy Ride')), 'Album is not present within metadata')
		assert_that(message.tracking(), is_(equal_to('tracking-id')), 'Tracking id is missing')

	def test_override_metadata_failure(self):

		data_dir = os.path.join(testutils.current_dirpath(__file__), 'data')

		accoustic_tester = testutils.TestActorBuilder().withType(musicbrainz.MusicMetadataActor).build()

		source_file = os.path.join(data_dir, '09-override_id3taginfo.mp3')		

		metadata_builder = common_domain.FileMetadataBuilder()
		metadata = metadata_builder.artist('My Test Artist').title('My Test Title').album('My Test Album').track_number(None).build()		

		accoustic_tester.tell(messages.OverrideFileMetadata(source_file, metadata, 'tracking-id'))		

		assert_that(accoustic_tester.inspector().num_instances(messages.OverrideFileMetadataFailed), is_(equal_to(1)), 'Total amount of OverrideFileMetadataFailed messages received is wrong')

		message = accoustic_tester.inspector().get_first(messages.OverrideFileMetadataFailed)

		assert_that(message.source_file(), is_(equal_to(source_file)), 'Source file is not present in response')
		assert_that(message.tracking(), is_(equal_to('tracking-id')), 'Tracking id is missing')

if __name__ == '__main__':
    unittest.main()		