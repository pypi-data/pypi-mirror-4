import messages
import events

from longtang.actors import actors
from longtang.actors.filesystem import filemanager, foldermanager, messages as filesystem_messages
from longtang.actors.media.id3tag import id3tagwriter, messages as id3tag_messages
from longtang.actors.tracking import facade

class FilePackagingSupervisor(actors.Actor):

	def pre_setup(self):
		
		self.logger().info('Initializing actors...')

		self.__folder_manager_ref = self.context().from_type(foldermanager.FolderManagerActor,'id3-folder-manager-actor')

		self.logger().info('Creating id3-folder-manager-actor ....... DONE')

		self.__file_manager_ref = self.context().from_type(filemanager.FileManagerActor,'id3-file-manager-actor')

		self.logger().info('Creating id3-file-manager-actor ....... DONE')

		self.__file_tagger_ref = self.context().from_type(id3tagwriter.ID3TagWriterActor,'id3-file-tagger-actor')

		self.logger().info('Creating id3-file-tagger-actor ....... DONE')
	
	def receive(self, message):
		if isinstance(message, messages.PerformFilePackaging):
			
			self.logger().info('File to be packaged received', message.tracking())
			facade.MediaTrackingFacade.from_context(self.context()).notify(message.tracking(), events.PackagingStarted())
			self.context().get_by_id('id3-folder-manager-actor').tell(filesystem_messages.CreateFolderFromMetadata(message.source_file(),\
																													message.metadata(), \
																													message.target_dir(), message.tracking()), self)

		elif isinstance(message, filesystem_messages.FolderFromMetadataSuccessfullyCreated):

			self.logger().info('Target folder has been succesfully created', message.tracking())
			facade.MediaTrackingFacade.from_context(self.context()).notify(message.tracking(), events.TargetFolderCreated())
			self.context().get_by_id('id3-file-manager-actor').tell(filesystem_messages.CopyFileTo(message.source_file(),\
																									message.metadata(),\
																									message.new_dir_path(), message.tracking()), self)
		elif isinstance(message, filesystem_messages.FileSuccessfullyCopied):

			self.logger().info('Media file succesfully copied', message.tracking())
			facade.MediaTrackingFacade.from_context(self.context()).notify(message.tracking(), events.MediaFileCopied())
			self.context().get_by_id('id3-file-tagger-actor').tell(id3tag_messages.WriteFileMetadata(message.copied_file(),\
																										message.metadata(), message.tracking()), self)
		elif isinstance(message, id3tag_messages.FileMetadataUpdated):
			
			self.logger().info('Media file succesfully updated with metadata', message.tracking())
			facade.MediaTrackingFacade.from_context(self.context()).notify(message.tracking(), events.MetadataUpdated())
			self.context().get_by_id('id3-file-manager-actor').tell(filesystem_messages.RenameFileFromMetadata(message.source(),\
																												 message.metadata(), message.tracking()), self)
		elif isinstance(message, filesystem_messages.FileSuccessfullyRenamed):

			self.logger().info('Media file succesfully renamed according to metadata', message.tracking())
			facade.MediaTrackingFacade.from_context(self.context()).notify(message.tracking(), events.FilePackagingFinished(message.new_file()))
			self.parent().tell(messages.FilePackagingFinished(message.source_file(), message.tracking()), self)

		elif isinstance(message, filesystem_messages.CopyFileToFailed):

			self.logger().error('Media file could not be copied. Reason: {0}'.format(message.reason()), message.tracking())
			facade.MediaTrackingFacade.from_context(self.context()).notify(message.tracking(), events.FileCopyFailed())
			self.parent().tell(messages.FilePackagingFailure(message.source_file(), message.metadata(), message.reason(), message.tracking()), self)

		elif isinstance(message, filesystem_messages.RenameFileFromMetadataFailed):

			self.logger().error('Media file could not be renamed. Reason: {0}'.format(message.reason()), message.tracking())
			facade.MediaTrackingFacade.from_context(self.context()).notify(message.tracking(), events.FileRenamingFailed())
			self.parent().tell(messages.FilePackagingFailure(message.source_file(), message.metadata(), message.reason(), message.tracking()), self)

		elif isinstance(message, filesystem_messages.CreateFolderFromMetadataFailed):

			self.logger().error('Target folder could not be created. Reason: {0}'.format(message.reason()), message.tracking())
			facade.MediaTrackingFacade.from_context(self.context()).notify(message.tracking(), events.FolderCreationFailed())
			self.parent().tell(messages.FilePackagingFailure(message.source_file(), message.metadata(), message.reason(), message.tracking()), self)

		elif isinstance(message, id3tag_messages.WriteFileMetadataFailed):
			
			self.logger().error('Id3 tags could not be saved. Reason: {0}'.format(message.reason()), message.tracking())
			facade.MediaTrackingFacade.from_context(self.context()).notify(message.tracking(), events.MetadataWritingFailed())
			self.parent().tell(messages.FilePackagingFailure(message.source_file(), message.metadata(), message.reason(), message.tracking()), self)

		else: 
			self.notify_marooned_message(message)