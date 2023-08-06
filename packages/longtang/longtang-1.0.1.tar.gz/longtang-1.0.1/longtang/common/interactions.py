import gevent

from longtang.actors import actors, messages

class InteractionPatterns:

	@staticmethod
	def ask(system_ref, actor_ref, message):

		#TODO The name could be dynamic i think
		host_actor = system_ref.from_type(HostActor,'interactions-actor', None)
		actor_ref.tell(message,host_actor)

		#system.wait_for(host_actor)
		gevent.joinall([host_actor._instance()])

		#TODO WE should remove this actor from the registry
		return host_actor._instance().response()

class HostActor(actors.Actor):
	def __init__(self, system_ref, unique_id):
		actors.Actor.__init__(self, system_ref, unique_id)
		self.__response=[]

	def receive(self, message):
		self.__response.append(message)
		self._silently_end()

	def response(self):
		return self.__response[0]