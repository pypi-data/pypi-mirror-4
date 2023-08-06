import messages
import domain

from longtang.actors import actors

class ID3TagWriterActor(actors.Actor):
	def receive(self, message):
		if isinstance(message, messages.WriteFileMetadata):

			self.logger().info(u'Saving metadata on file....{0}'.format(message.metadata()), message.tracking())

			if message.metadata().missing_tags():
				self.sender().tell(messages.WriteFileMetadataFailed(message.tracking(), message, 'One or more metadata field is missing'), self.myself())
			else:
				try:
					writer = domain.ID3TagWriterFactory.createFromType(message.source())
					writer.save(message.metadata())

					self.sender().tell(messages.FileMetadataUpdated(message.source(), message.metadata(), message.tracking()), self.myself())

				except IOError as e:

					self.logger().error(u'Metadata could not be saved. Reason: {0}'.format(str(e)), message.tracking())
					self.sender().tell(messages.WriteFileMetadataFailed(message.tracking(), message, str(e)), self.myself())
		else: 
			self.notify_marooned_message(message)