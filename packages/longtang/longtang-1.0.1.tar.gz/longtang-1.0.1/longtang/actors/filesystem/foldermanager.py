import messages
import domain
import os

from longtang.actors import actors

class FolderManagerActor(actors.Actor):
	def receive(self, message):
		if isinstance(message, messages.CreateFolderFromMetadata):

			self.logger().info(u'Using metadata for folder creation....{0}'.format(message.metadata()), message.tracking())

			if message.metadata().missing_tags():
				self.logger().error(u'Folder could not be created from metadata {0}. Reason: One or more metadata fields are missing'.format(message.metadata()), message.tracking())
				self.sender().tell(messages.CreateFolderFromMetadataFailed(message.tracking(), message, 'One or more metadata fields are missing'), self.myself())
			else:
				try:
					
					full_dir_path = os.path.join(message.base_dir(), message.metadata().artist, message.metadata().album)

					if not os.path.exists(full_dir_path):
						os.makedirs(full_dir_path)

					self.sender().tell(\
						messages.FolderFromMetadataSuccessfullyCreated(message.source_file(), message.metadata(), full_dir_path, message.tracking()),\
						self.myself())

				except Exception as e:

					self.logger().error(u'Folder could not be created from metadata {0}. Reason: {1}'.format(message.metadata(), str(e)), message.tracking())
					self.sender().tell(messages.CreateFolderFromMetadataFailed(message.tracking(), message, str(e)), self.myself())