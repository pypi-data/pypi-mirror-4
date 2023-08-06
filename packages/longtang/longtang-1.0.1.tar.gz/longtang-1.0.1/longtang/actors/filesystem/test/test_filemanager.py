import unittest
import os

from longtang.actors import testutils
from longtang.actors.filesystem import filemanager, messages, domain
from longtang.common import domain as common_domain
from hamcrest import *

class TestFileManagerActor(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		global base_test_dir
		global base_io_target_dir

		base_test_dir = testutils.create_tmp_dir(suffix='_file_management_test')
		base_io_target_dir = testutils.create_tmp_dir(suffix='_file_management_test_io_target')

	@classmethod
	def tearDownClass(cls):
		testutils.remove_tmp_dir(base_test_dir)
		testutils.remove_tmp_dir(base_io_target_dir)

	def setUp(self):

		global source_file

		data_dir = os.path.join(testutils.current_dirpath(__file__), 'data')
		source_file = testutils.copy_to_tmp(source=os.path.join(data_dir, 'rename.mp3'),suffix='.tmp.mp3', dir=base_test_dir)

	def tearDown(self):
		testutils.remove_dir_content(base_test_dir)	

	def test_rename_file_from_metadata_message(self):

		metadata_builder = common_domain.FileMetadataBuilder()
		metadata = metadata_builder.artist('Dummy Artist').title('Dummy Title').album('Dummy Album').track_number('7').build()

		file_tester = testutils.TestActorBuilder().withType(filemanager.FileManagerActor).build()

		file_tester.tell(messages.RenameFileFromMetadata(source_file, metadata, 'tracking-id'))

		assert_that(file_tester.inspector().num_instances(messages.FileSuccessfullyRenamed), is_(equal_to(1)), 'Total amount of FileSuccessfullyRenamed messages received is wrong')

		message = file_tester.inspector().get_first(messages.FileSuccessfullyRenamed)

		assert_that(message.source_file(), is_(not_none()), 'Source file is empty')
		assert_that(message.new_file(), is_(not_none()), 'New file is empty')
		assert_that(message.metadata(), is_(not_none()), 'File metadata information is empty')
		assert_that(message.tracking(), is_(equal_to('tracking-id')), 'Tracking id is missing')

	def test_rename_file_filename_structure(self):

		metadata_builder = common_domain.FileMetadataBuilder()
		metadata = metadata_builder.artist('Dummy Artist').title('Dummy Title').album('Dummy Album').track_number('7').build()

		file_tester = testutils.TestActorBuilder().withType(filemanager.FileManagerActor).build()

		file_tester.tell(messages.RenameFileFromMetadata(source_file, metadata, 'tracking-id'))

		assert_that(file_tester.inspector().num_instances(messages.FileSuccessfullyRenamed), is_(equal_to(1)), 'Total amount of FileSuccessfullyRenamed messages received is wrong')

		message = file_tester.inspector().get_first(messages.FileSuccessfullyRenamed)

		filepath, new_full_name = os.path.split(message.new_file())

		assert_that(os.path.isfile(message.new_file()), is_(equal_to(True)), 'File does not exist')
		assert_that(new_full_name, is_(equal_to('07 - Dummy Title.mp3')),'Filename is not right!')
		assert_that(message.tracking(), is_(equal_to('tracking-id')), 'Tracking id is missing')

	def test_copy_file(self):

		metadata_builder = common_domain.FileMetadataBuilder()
		metadata = metadata_builder.artist('Dummy Artist').title('Dummy Title').album('Dummy Album').track_number('7').build()

		file_tester = testutils.TestActorBuilder().withType(filemanager.FileManagerActor).build()

		file_tester.tell(messages.CopyFileTo(source_file, metadata, base_io_target_dir, 'tracking-id'))

		assert_that(file_tester.inspector().num_instances(messages.FileSuccessfullyCopied), is_(equal_to(1)), 'Total amount of FileSuccessfullyCopied messages received is wrong')		

		message = file_tester.inspector().get_first(messages.FileSuccessfullyCopied)

		assert_that(message.source_file(), is_(not_none()), 'Source file is empty')
		assert_that(message.copied_file(), is_(not_none()), 'Copied file path is empty')
		assert_that(message.metadata(), is_(not_none()), 'File metadata information is empty')
		assert_that(message.tracking(), is_(equal_to('tracking-id')), 'Tracking id is missing')
		assert_that(os.path.isfile(message.copied_file()), is_(equal_to(True)), 'Copied file does not exist')

	def test_copy_file_failure(self):

		metadata_builder = common_domain.FileMetadataBuilder()
		metadata = metadata_builder.artist('Dummy Artist').title('Dummy Title').album('Dummy Album').track_number('7').build()

		file_tester = testutils.TestActorBuilder().withType(filemanager.FileManagerActor).build()

		file_tester.tell(messages.CopyFileTo('/dummy_path.mp3', metadata, base_io_target_dir, 'tracking-id'))

		assert_that(file_tester.inspector().num_instances(messages.CopyFileToFailed), is_(equal_to(1)), 'Total amount of CopyFileToFailed messages received is wrong')

		message = file_tester.inspector().get_first(messages.CopyFileToFailed)

		assert_that(message.source_file(), is_(not_none()), 'Source file is empty')
		assert_that(message.metadata(), is_(not_none()), 'File metadata information is empty')
		assert_that(message.copy_to_path(), is_(not_none()), 'Copy path to information is empty')
		assert_that(message.reason(), is_(not_none()), 'Reason information is empty')
		assert_that(message.tracking(), is_(equal_to('tracking-id')), 'Tracking id is missing')

	def test_rename_file_from_metadata_message_failure(self):

		metadata_builder = common_domain.FileMetadataBuilder()
		metadata = metadata_builder.artist('Dummy Artist').title('Dummy Title').album('Dummy Album').track_number('7').build()

		file_tester = testutils.TestActorBuilder().withType(filemanager.FileManagerActor).build()

		file_tester.tell(messages.RenameFileFromMetadata('/dummy_path.mp3', metadata, 'tracking-id'))

		assert_that(file_tester.inspector().num_instances(messages.RenameFileFromMetadataFailed), is_(equal_to(1)), 'Total amount of RenameFileFromMetadataFailure messages received is wrong')

		message = file_tester.inspector().get_first(messages.RenameFileFromMetadataFailed)

		assert_that(message.source_file(), is_(not_none()), 'Source file is empty')
		assert_that(message.metadata(), is_(not_none()), 'File metadata information is empty')
		assert_that(message.reason(), is_(not_none()), 'Reason information is empty')
		assert_that(message.tracking(), is_(equal_to('tracking-id')), 'Tracking id is missing')