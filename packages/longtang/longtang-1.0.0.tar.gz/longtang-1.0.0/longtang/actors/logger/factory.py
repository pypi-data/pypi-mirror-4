import logger

from longtang.system import domain

class LoggerActorFactory(domain.ActorFactory):
	def __init__(self, level):
		self.__level = level

	def create(self, unique_id, system_ref):
		return logger.LoggerActor(self.__level, system_ref, unique_id)