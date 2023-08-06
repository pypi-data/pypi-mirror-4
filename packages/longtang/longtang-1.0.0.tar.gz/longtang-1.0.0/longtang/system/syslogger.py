import exceptions

from longtang.actors.logger import logger, messages, factory


class SystemLoggerFactory:

	@staticmethod
	def createIfAbsent(system, level):
		syslogger_ref=None

		if level is not None:
			try:
				syslogger_ref = system.find_by_id('sys-logger')
			except exceptions.ActorNotFound as e:
				syslogger_ref = system.with_factory(factory.LoggerActorFactory(level),'sys-logger')

		return SystemLogger(syslogger_ref)


class SystemLogger:
	def __init__(self, logger_actor_ref):
		self.__logger_actor_ref=logger_actor_ref

	def info(self, actor_id, message, source_file):
		if self.__logger_actor_ref is not None and actor_id is not self.__logger_actor_ref.unique_id():
			self.__logger_actor_ref.tell(messages.FileInformationEventMessage(actor_id, source_file, message))

	def error(self, actor_id, message, source_file):
		if self.__logger_actor_ref is not None and actor_id is not self.__logger_actor_ref.unique_id():
			self.__logger_actor_ref.tell(messages.FileErrorEventMessage(actor_id, source_file, message))

	def debug(self, actor_id, message, source_file):
		if self.__logger_actor_ref is not None and actor_id is not self.__logger_actor_ref.unique_id():
			self.__logger_actor_ref.tell(messages.FileDebugEventMessage(actor_id, source_file, message))

	def warn(self, actor_id, message, source_file):
		if self.__logger_actor_ref is not None and actor_id is not self.__logger_actor_ref.unique_id():
			self.__logger_actor_ref.tell(messages.FileWarnEventMessage(actor_id, source_file, message))		