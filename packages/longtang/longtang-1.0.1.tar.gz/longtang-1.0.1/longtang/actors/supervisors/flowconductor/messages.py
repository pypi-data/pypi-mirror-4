from longtang.actors import messages

class MediaFileAvailable(messages.TraceableActorMessage):
	def __init__(self, filepath, tracking):
		messages.TraceableActorMessage.__init__(self, tracking)

		self.__filepath=filepath

	def filepath(self):
		return self.__filepath

class MediaFileHasBeenProcessed(messages.TraceableActorMessage):
	def __init__(self, tracking):
		messages.TraceableActorMessage.__init__(self, tracking)

class MediaFileProcessingFailed(messages.TraceableActorFailureMessage):
	def __init__(self, tracking, source_message=None):
		messages.TraceableActorFailureMessage.__init__(self, tracking, "", source_message)		