import messages
import domain
import medianame

from longtang.actors import actors

class ID3TagCheckerActor(actors.Actor):
	def receive(self, message):
		if isinstance(message, messages.CheckFileMetadata):

			self.logger().info(u'Checking ID3Tag information from file ...', message.tracking())

			try:
				reader = domain.ID3TagReaderFactory.createFromType(message.source())

				metadata = reader.extract_metadata()

				self.logger().info(u'Metadata information extracted: {0}'.format(metadata), message.tracking())

				if not metadata.missing_tags():
					self.sender().tell(messages.FileMetadataIsComplete(message.source(), metadata, message.tracking()), self.myself())
				else:

					if metadata.is_track_number_missing():
						evaluator = medianame.MedianameEvaluator.create_from_path(message.source())
						evaluation = evaluator.evaluate()

						if evaluation.track_number is not None:
							metadata.track_number = evaluation.track_number

					if not metadata.missing_tags():

						self.logger().info(u'Missing metadata guessed from name: {0}'.format(metadata), message.tracking())

						self.sender().tell(messages.FileMetadataIsComplete(message.source(), metadata, message.tracking()), self.myself())
					else:
						self.sender().tell(messages.FileMetadataIsIncomplete(message.source(), metadata, message.tracking()), self.myself())
			except IOError as e:
					self.logger().error(u'Metadata could not be checked. Reason: {0}'.format(str(e)), message.tracking())
					self.sender().tell(messages.FileMetadataCouldNotBeChecked(message.tracking(), message, str(e)), self.myself())
		else: 
			self.notify_marooned_message(message)