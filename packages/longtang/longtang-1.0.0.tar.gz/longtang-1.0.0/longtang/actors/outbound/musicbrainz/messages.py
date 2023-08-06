from longtang.actors import messages

class LookupFileMetadata(messages.TraceableActorMessage):

	def __init__(self, source, tracking):
		messages.TraceableActorMessage.__init__(self, tracking)
		self.__source=source

	def source(self):
		return self.__source


class FillUpMissingMetadataFields(messages.TraceableActorMessage):

	def __init__(self, source, metadata, tracking):
		messages.TraceableActorMessage.__init__(self, tracking)
		self.__source=source
		self.__metadata=metadata

	def source(self):
		return self.__source

	def metadata(self):
		return self.__metadata

class FillUpMissingMetadataFieldsFailed(messages.TrackingActorFailureMessage):
	def __init__(self, tracking, source_message, reason):
		messages.TrackingActorFailureMessage.__init__(self, tracking, reason, source_message)

	def source_file(self):
		return self.source_message().source()

class FileMetadataSuccessfullyFilled(messages.TraceableActorMessage):

	def __init__(self, source, metadata, tracking):
		messages.TraceableActorMessage.__init__(self, tracking)
		self.__source=source
		self.__metadata=metadata

	def source(self):
		return self.__source

	def metadata(self):
		return self.__metadata			

class FileMetadataFound(messages.TraceableActorMessage):

	def __init__(self, source, metadata, tracking):
		messages.TraceableActorMessage.__init__(self, tracking)
		self.__metadata=metadata
		self.__source=source

	def metadata(self):
		return self.__metadata	

	def source(self):
		return self.__source

class FileMetadataNotFound(messages.TraceableActorMessage):
	def __init__(self, source, tracking):
		messages.TraceableActorMessage.__init__(self, tracking)
		self.__source = source

	def source(self):
		return self.__source

class MusicBrainzServiceFailed(messages.TraceableActorMessage):
	def __init__(self, source, tracking):
		messages.TraceableActorMessage.__init__(self, tracking)
		self.__source = source

	def source(self):
		return self.__source

class OverrideFileMetadata(messages.TraceableActorMessage):

	def __init__(self, source, metadata, tracking):
		messages.TraceableActorMessage.__init__(self, tracking)
		self.__source=source
		self.__metadata=metadata

	def source(self):
		return self.__source

	def metadata(self):
		return self.__metadata

class OverrideFileMetadataDone(messages.TraceableActorMessage):

	def __init__(self, source, metadata, tracking):
		messages.TraceableActorMessage.__init__(self, tracking)
		self.__source=source
		self.__metadata=metadata

	def source(self):
		return self.__source

	def metadata(self):
		return self.__metadata

class OverrideFileMetadataFailed(messages.TrackingActorFailureMessage):
	def __init__(self, tracking, source_message, reason):
		messages.TrackingActorFailureMessage.__init__(self, tracking, reason, source_message)

	def source_file(self):
		return self.source_message().source()		