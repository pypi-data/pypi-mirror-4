import flowconductor

from longtang.system import domain

class FlowConductorSupervisorFactory(domain.ActorFactory):
	def __init__(self, config):
		self.__config = config

	def create(self, unique_id, system_ref):
		return flowconductor.FlowConductorSupervisor(self.__config, system_ref, unique_id)