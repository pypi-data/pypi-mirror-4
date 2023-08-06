from longtang.actors import messages

class FileEventMessage(messages.ActorMessage):
	def __init__(self, actor, source_file, message):
		messages.ActorMessage.__init__(self)

		self.__message = message
		self.__source_file=source_file
		self.__actor=actor

	def message(self):
		return self.__message

	def actor(self):
		return self.__actor

	def source_file(self):
		return self.__source_file

	def type(self):
		raise NotImplemented()

class FileInformationEventMessage(FileEventMessage):
	def __init__(self, actor, source_file, message):
		FileEventMessage.__init__(self,actor, source_file, message)

	def type(self):
		return 'INFO'		

class FileErrorEventMessage(FileEventMessage):
	def __init__(self, actor, source_file, message):
		FileEventMessage.__init__(self,actor, source_file, message)	

	def type(self):
		return 'ERROR'

class FileDebugEventMessage(FileEventMessage):
	def __init__(self, actor, source_file, message):
		FileEventMessage.__init__(self,actor, source_file, message)	

	def type(self):
		return 'DEBUG'

class FileWarnEventMessage(FileEventMessage):
	def __init__(self, actor, source_file, message):
		FileEventMessage.__init__(self,actor, source_file, message)	

	def type(self):
		return 'WARN'					