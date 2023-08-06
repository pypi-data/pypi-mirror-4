import main

from longtang.system import domain

class MainSupervisorFactory(domain.ActorFactory):
	def __init__(self, config):
		self.__config = config

	def create(self, unique_id, system_ref):
		return main.MainSupervisor(self.__config, system_ref, unique_id)