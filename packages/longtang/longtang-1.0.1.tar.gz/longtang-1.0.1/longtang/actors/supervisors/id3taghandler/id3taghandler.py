import messages
import events

from longtang.actors import actors
from longtang.actors.media.id3tag import id3tagchecker, messages as id3tag_messages
from longtang.actors.outbound.musicbrainz import musicbrainz, messages as mb_messages
from longtang.actors.tracking import facade

class Id3TagSupervisor(actors.Actor):

	def __init__(self, config, system_ref, unique_id):
		actors.Actor.__init__(self, system_ref, unique_id)

		self.__config=config

	def pre_setup(self):

		self.logger().info('Initializing actors...')

		self.logger().info('Creating id3tag-reader-actor ....... DONE')

		self.__id3tagchecker_ref = self.context().from_type(id3tagchecker.ID3TagCheckerActor,'id3tag-reader-actor')

		self.logger().info('Creating musicbrainz-actor ....... DONE')

		self.__musicbrainz_ref = self.context().from_type(musicbrainz.MusicMetadataActor,'musicbrainz-actor')

	def receive(self, message):

		if isinstance(message, messages.InspectFileMetadata):
			self.logger().info(u'Starting metadata inspection on file .....', message.tracking())
			facade.MediaTrackingFacade.from_context(self.context()).notify(message.tracking(), events.MetadataInspectionStarted())
			self.context().get_by_id('id3tag-reader-actor').tell(id3tag_messages.CheckFileMetadata(message.source_file(), message.tracking()), self.myself())

		elif isinstance(message, id3tag_messages.FileMetadataIsComplete):
			facade.MediaTrackingFacade.from_context(self.context()).notify(message.tracking(), events.MetadataAvailable())

			if self.__config.override_tags:
				self.context().get_by_id('musicbrainz-actor').tell(mb_messages.OverrideFileMetadata(message.source(), message.metadata(), message.tracking()), self.myself())				
			else:
				self.parent().tell(messages.FileMetadataAvailable(message.source(), message.metadata(), message.tracking()), self.myself())

		elif isinstance(message, id3tag_messages.FileMetadataIsIncomplete):

			if not self.__config.offline_mode:
				self.logger().info('There\'re some metadata fields missing. Trying with musicbrainz .....', message.tracking())
				facade.MediaTrackingFacade.from_context(self.context()).notify(message.tracking(), events.FileMetadataIncomplete())
				self.context().get_by_id('musicbrainz-actor').tell(mb_messages.FillUpMissingMetadataFields(message.source(), message.metadata(), message.tracking()), self.myself())
			else:
				self.logger().error('File metadata could not be fulfilled and offline mode is active.', message.tracking())
				facade.MediaTrackingFacade.from_context(self.context()).notify(message.tracking(), events.MetadataNotAvailable())
				self.parent().tell(messages.FileMetadataNotFullyAvailable(message.source(), message.tracking()), self.myself())				

		elif isinstance(message, mb_messages.OverrideFileMetadataDone):
			self.logger().info('File metadata overriden with MusicBrainz info .....', message.tracking())
			facade.MediaTrackingFacade.from_context(self.context()).notify(message.tracking(), events.MetadataAvailable())
			self.parent().tell(messages.FileMetadataAvailable(message.source(), message.metadata(), message.tracking()), self.myself())

		elif isinstance(message, mb_messages.FileMetadataSuccessfullyFilled):
			self.logger().info('File metadata found in MusicBrainz .....', message.tracking())
			facade.MediaTrackingFacade.from_context(self.context()).notify(message.tracking(), events.MetadataAvailable())
			self.parent().tell(messages.FileMetadataAvailable(message.source(), message.metadata(), message.tracking()), self.myself())

		elif isinstance(message, id3tag_messages.FileMetadataCouldNotBeChecked):
			self.logger().error('File metadata failed to be checked. Reason: {0}'.format(message.reason()), message.tracking())
			facade.MediaTrackingFacade.from_context(self.context()).notify(message.tracking(), events.MetadataEvaluationFailed())
			self.parent().tell(messages.FileMetadataCouldNotBeEvaluated(message.source_file(), message.tracking()), self.myself())

		elif isinstance(message, mb_messages.FillUpMissingMetadataFieldsFailed) or isinstance(message, mb_messages.OverrideFileMetadataFailed):
			self.logger().error('File metadata could not be fulfilled. Reason: {0}'.format(message.reason()), message.tracking())
			facade.MediaTrackingFacade.from_context(self.context()).notify(message.tracking(), events.MetadataNotAvailable())
			self.parent().tell(messages.FileMetadataNotFullyAvailable(message.source_file(), message.tracking()), self.myself())

		elif isinstance(message, mb_messages.MusicBrainzServiceFailed):
			self.logger().error('Musicbrainz service is not responding.', message.tracking())
			facade.MediaTrackingFacade.from_context(self.context()).notify(message.tracking(), events.MusicbrainzServiceFailed())
			self.parent().tell(messages.FileMetadataNotFullyAvailable(message.source(), message.tracking()), self.myself())			
		else: 
			self.notify_marooned_message(message)