class ActorMessage:
	def __init__(self):
		pass

class TraceableActorMessage(ActorMessage):
	def __init__(self, tracking):
		ActorMessage.__init__(self)
		self.__tracking = tracking

	def tracking(self):
		return self.__tracking

class TraceableActorFailureMessage(TraceableActorMessage):
	def __init__(self, tracking, reason, source_message=None):
		TraceableActorMessage.__init__(self,tracking)
		self.__reason=reason
		self.__source_message=source_message

	def reason(self):
		return self.__reason

	def source_message(self):
		return self.__source_message		

class ActorFailureMessage(ActorMessage):
	def __init__(self, reason, source_message=None):
		ActorMessage.__init__(self)
		self.__reason=reason
		self.__source_message=source_message

	def reason(self):
		return self.__reason

	def source_message(self):
		return self.__source_message

class TrackingActorFailureMessage(ActorFailureMessage):
	def __init__(self, tracking, reason, source_message=None):
		ActorFailureMessage.__init__(self, reason, source_message)
		self.__tracking=tracking

	def tracking(self):
		return self.__tracking

class PoisonPill(ActorMessage):
	def __init__(self):
		ActorMessage.__init__(self)


class Terminated(ActorMessage):
	def __init__(self, actor_id):
		ActorMessage.__init__(self)
		self.__actor_id=actor_id

	def actor_id(self):
		return self.__actor_id
