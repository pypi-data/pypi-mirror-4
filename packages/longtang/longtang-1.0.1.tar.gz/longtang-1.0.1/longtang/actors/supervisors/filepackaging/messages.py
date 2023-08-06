from longtang.actors import messages

class PerformFilePackaging(messages.TraceableActorMessage):
	def __init__(self, source_file, metadata, target_dir, tracking):
		messages.TraceableActorMessage.__init__(self, tracking)

		self.__source_file = source_file
		self.__metadata = metadata
		self.__target_dir = target_dir

	def source_file(self):
		return self.__source_file

	def metadata(self):
		return self.__metadata

	def target_dir(self):
		return self.__target_dir

class FilePackagingFinished(messages.TraceableActorMessage):

	def __init__(self, source_file, tracking):
		messages.TraceableActorMessage.__init__(self, tracking)
		self.__source_file=source_file

	def source_file(self):
		return self.__source_file	

class FilePackagingFailure(messages.TraceableActorMessage):
	def __init__(self, source_file, metadata, reason, tracking):
		messages.TraceableActorMessage.__init__(self, tracking)
		self.__source_file=source_file
		self.__metadata=metadata
		self.__reason=reason

	def source_file(self):
		return self.__source_file

	def metadata(self):
		return self.__metadata

	def reason(self):
		return self.__reason