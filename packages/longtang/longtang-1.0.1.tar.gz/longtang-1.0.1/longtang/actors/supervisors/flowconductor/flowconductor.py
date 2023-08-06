import messages

from longtang.actors import actors
from longtang.actors.inbound import filepoller, messages as fp_messages
from longtang.actors.supervisors.filepackaging import filepackaging, messages as packaging_messages
from longtang.actors.supervisors.id3taghandler import id3taghandler, messages as id3tag_messages, factory, configuration as id3tag_config

class FlowConductorSupervisor(actors.Actor):

	def __init__(self, config, system_ref, unique_id):
		actors.Actor.__init__(self, system_ref, unique_id)

		self.__config=config

	def pre_setup(self):
		
		self.logger().info('Initializing actors...')

		self.logger().info('Initializing filepackaging-actor...')
		self.__filepackaging_ref = self.context().from_type(filepackaging.FilePackagingSupervisor,'filepackaging-actor')

		id3tagconfig = id3tag_config.Id3TagHandlerConfigurationBuilder().override_tags(self.__config.override_tags)\
																		  .offline_mode(self.__config.offline_mode)\
																		  .build()

		self.logger().info('Initializing id3taghandler-actor...')
		self.__id3taghandler_ref = self.context().with_factory(factory.Id3TagSupervisorFactory(id3tagconfig),'id3taghandler-actor')
	
	def receive(self, message):
		if isinstance(message, messages.MediaFileAvailable):
			self.context().get_by_id('id3taghandler-actor').tell(id3tag_messages.InspectFileMetadata(message.filepath(), message.tracking()), self)
		elif isinstance(message, id3tag_messages.FileMetadataAvailable):
			self.context().get_by_id('filepackaging-actor').tell(packaging_messages.PerformFilePackaging(message.source_file(), message.metadata(), self.__config.generate_at, message.tracking()), self)
		elif isinstance(message, packaging_messages.FilePackagingFinished):
			self.parent().tell(messages.MediaFileHasBeenProcessed(message.tracking()), self.myself())
		elif isinstance(message, id3tag_messages.FileMetadataCouldNotBeEvaluated):
			self.logger().error('Mediafile metadata evaluation failed...', message.source_file())
			self.parent().tell(messages.MediaFileProcessingFailed(message.tracking(), message), self.myself())
		elif isinstance(message, packaging_messages.FilePackagingFailure):
			self.logger().error('Mediafile metadata evaluation failed...', message.source_file())
			self.parent().tell(messages.MediaFileProcessingFailed(message.tracking(), message), self.myself())
		elif isinstance(message, id3tag_messages.FileMetadataNotFullyAvailable):
			self.logger().error('Mediafile metadata evaluation failed...', message.source_file())
			self.parent().tell(messages.MediaFileProcessingFailed(message.tracking(), message), self.myself())			
		else:
			self.notify_marooned_message(message)		