from longtang.actors import messages

class CheckFileMetadata(messages.TraceableActorMessage):
	def __init__(self, source, tracking):
		messages.TraceableActorMessage.__init__(self, tracking)

		self.__source = source

	def source(self):
		return self.__source

class FileMetadataIsComplete(messages.TraceableActorMessage):
	def __init__(self, source, metadata, tracking):
		messages.TraceableActorMessage.__init__(self, tracking)	

		self.__source=source
		self.__metadata=metadata

	def source(self):
		return self.__source

	def metadata(self):
		return self.__metadata

class FileMetadataIsIncomplete(messages.TraceableActorMessage):
	def __init__(self, source, metadata, tracking):
		messages.TraceableActorMessage.__init__(self, tracking)	

		self.__source=source
		self.__metadata=metadata

	def source(self):
		return self.__source

	def metadata(self):
		return self.__metadata

class WriteFileMetadata(messages.TraceableActorMessage):
	def __init__(self, source, metadata, tracking):
		messages.TraceableActorMessage.__init__(self,tracking)

		self.__source=source
		self.__metadata=metadata

	def source(self):
		return self.__source

	def metadata(self):
		return self.__metadata

class FileMetadataUpdated(messages.TraceableActorMessage):
	def __init__(self, source, metadata, tracking):
		messages.TraceableActorMessage.__init__(self, tracking)	

		self.__source=source
		self.__metadata=metadata

	def source(self):
		return self.__source

	def metadata(self):
		return self.__metadata

class WriteFileMetadataFailed(messages.TrackingActorFailureMessage):
	def __init__(self, tracking, source_message, reason):
		messages.TrackingActorFailureMessage.__init__(self, tracking, reason, source_message)

	def source(self):
		return self.source_message().source()

	def metadata(self):
		return self.source_message().metadata()

class FileMetadataCouldNotBeChecked(messages.TraceableActorFailureMessage):
	def __init__(self, tracking, source_message, reason):
		messages.TraceableActorFailureMessage.__init__(self, tracking, reason, source_message)

	def source_file(self):
		return self.source_message().source()