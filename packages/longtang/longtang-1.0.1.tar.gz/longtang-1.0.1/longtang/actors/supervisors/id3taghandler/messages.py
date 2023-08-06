from longtang.actors import messages

class FileMetadataAvailable(messages.TraceableActorMessage):
	def __init__(self, source_file, metadata, tracking):
		messages.TraceableActorMessage.__init__(self, tracking)

		self.__source_file = source_file
		self.__metadata = metadata

	def source_file(self):
		return self.__source_file

	def metadata(self):
		return self.__metadata

class FileMetadataNotFullyAvailable(messages.TraceableActorMessage):
	def __init__(self, source_file, tracking):
		messages.TraceableActorMessage.__init__(self, tracking)

		self.__source_file = source_file

	def source_file(self):
		return self.__source_file

class InspectFileMetadata(messages.TraceableActorMessage):
	def __init__(self, source_file, tracking):
		messages.TraceableActorMessage.__init__(self, tracking)

		self.__source_file = source_file

	def source_file(self):
		return self.__source_file

class FileMetadataCouldNotBeEvaluated(messages.TraceableActorMessage):
	def __init__(self, source_file, tracking):
		messages.TraceableActorMessage.__init__(self, tracking)
		self.__source_file = source_file

	def source_file(self):
		return self.__source_file		