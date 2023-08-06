from longtang.actors import messages

class KickOffMediaProcessing(messages.ActorMessage):
	def __init__(self):
		messages.ActorMessage.__init__(self)

class MediaProcessingFinished(messages.ActorMessage):
	def __init__(self, summary):
		messages.ActorMessage.__init__(self)
		self.__summary=summary

	def summary(self):
		return self.__summary