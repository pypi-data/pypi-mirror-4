import unittest
import os

from longtang.actors import testutils
from longtang.actors.filesystem import foldermanager, messages, domain
from longtang.common import domain as common_domain
from hamcrest import *


class TestFolderManagerActor(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		global base_test_dir
		base_test_dir = testutils.create_tmp_dir(suffix='folder_management_test')

	@classmethod
	def tearDownClass(cls):
		testutils.remove_tmp_dir(base_test_dir)

	def test_create_folder_from_metadata_message(self):
		
		data_dir = os.path.join(testutils.current_dirpath(__file__), 'data')
		source_file = os.path.join(data_dir, 'sample.mp3')

		metadata_builder = common_domain.FileMetadataBuilder()
		metadata = metadata_builder.artist('Folder Artist').title('Folder Title').album('Folder Album').track_number('7').build()

		folder_tester = testutils.TestActorBuilder().withType(foldermanager.FolderManagerActor).build()

		folder_tester.tell(messages.CreateFolderFromMetadata(source_file, metadata, base_test_dir, 'tracking-id'))

		assert_that(folder_tester.inspector().num_instances(messages.FolderFromMetadataSuccessfullyCreated), is_(equal_to(1)), 'Total amount of FolderFromMetadataCreated messages received is wrong')		

		message = folder_tester.inspector().get_first(messages.FolderFromMetadataSuccessfullyCreated)

		assert_that(message.source_file(), is_(not_none()), 'Source file is empty')
		assert_that(message.metadata(), is_(not_none()), 'File metadata information is empty')
		assert_that(message.new_dir_path(), is_(not_none()), 'New dir path information is empty')
		assert_that(message.tracking(), is_(equal_to('tracking-id')), 'Tracking id is missing')

	def test_create_folder_from_metadata_folder_existance(self):
		
		data_dir = os.path.join(testutils.current_dirpath(__file__), 'data')
		source_file = os.path.join(data_dir, 'sample.mp3')

		metadata_builder = common_domain.FileMetadataBuilder()
		metadata = metadata_builder.artist('Folder Artist').title('Folder Title').album('Folder Album').track_number('7').build()

		folder_tester = testutils.TestActorBuilder().withType(foldermanager.FolderManagerActor).build()

		folder_tester.tell(messages.CreateFolderFromMetadata(source_file, metadata, base_test_dir, 'tracking-id'))

		message = folder_tester.inspector().get_first(messages.FolderFromMetadataSuccessfullyCreated)

		full_dir_path= os.path.join(base_test_dir, 'Folder Artist', 'Folder Album')

		assert_that(os.path.isdir(full_dir_path), is_(equal_to(True)), 'Target directory does not exist or full name is not right')
		assert_that(message.tracking(), is_(equal_to('tracking-id')), 'Tracking id is missing')

	def test_folder_name_capitalization(self):
		
		data_dir = os.path.join(testutils.current_dirpath(__file__), 'data')
		source_file = os.path.join(data_dir, 'sample.mp3')

		metadata_builder = common_domain.FileMetadataBuilder()
		metadata = metadata_builder.artist('CAPITAL ARTIST').title('CAPITAL TITLE').album('CAPITAL ALBUM').track_number('7').build()

		folder_tester = testutils.TestActorBuilder().withType(foldermanager.FolderManagerActor).build()

		folder_tester.tell(messages.CreateFolderFromMetadata(source_file, metadata, base_test_dir, 'tracking-id'))

		message = folder_tester.inspector().get_first(messages.FolderFromMetadataSuccessfullyCreated)

		full_dir_path= os.path.join(base_test_dir, 'Capital Artist', 'Capital Album')

		assert_that(os.path.isdir(full_dir_path), is_(equal_to(True)), 'Target directory does not exist or full name is not right')
		assert_that(message.tracking(), is_(equal_to('tracking-id')), 'Tracking id is missing')

	def test_create_folder_from_metadata_dir_failure(self):
		
		data_dir = os.path.join(testutils.current_dirpath(__file__), 'data')
		source_file = os.path.join(data_dir, 'sample.mp3')

		metadata_builder = common_domain.FileMetadataBuilder()
		metadata = metadata_builder.artist('Folder Artist').title('Folder Title').album('Folder Album').track_number('7').build()

		folder_tester = testutils.TestActorBuilder().withType(foldermanager.FolderManagerActor).build()

		folder_tester.tell(messages.CreateFolderFromMetadata(source_file, metadata, '/dummy_dir', 'tracking-id'))

		assert_that(folder_tester.inspector().num_instances(messages.CreateFolderFromMetadataFailed), is_(equal_to(1)), 'Total amount of CreateFolderFromMetadataFailed messages received is wrong')		

		message = folder_tester.inspector().get_first(messages.CreateFolderFromMetadataFailed)

		assert_that(message.source_file(), is_(not_none()), 'Source file is empty')
		assert_that(message.metadata(), is_(not_none()), 'File metadata information is empty')
		assert_that(message.base_dir(), is_(not_none()), 'Base dir path information is empty')	
		assert_that(message.reason(), is_(not_none()), 'Reason information is empty')
		assert_that(message.source_message(), is_(not_none()), 'Source message information is empty')
		assert_that(message.tracking(), is_(equal_to('tracking-id')), 'Tracking id is missing')