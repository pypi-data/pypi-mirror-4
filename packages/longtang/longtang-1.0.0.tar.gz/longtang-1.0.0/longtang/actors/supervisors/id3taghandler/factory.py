import id3taghandler

from longtang.system import domain

class Id3TagSupervisorFactory(domain.ActorFactory):
	def __init__(self, config):
		self.__config = config

	def create(self, unique_id, system_ref):
		return id3taghandler.Id3TagSupervisor(self.__config, system_ref, unique_id)