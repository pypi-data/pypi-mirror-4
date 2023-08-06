class ActorNotFound(Exception):
	def __init__(self, actor_id, msg=None):
		self.__actor_id = actor_id
		self.__msg = msg

	def __str__(self):
		return repr("Actor '{0}' could not be found within the system. {1}".format(self.__actor_id, self.__msg if self.__msg is not None else ''))