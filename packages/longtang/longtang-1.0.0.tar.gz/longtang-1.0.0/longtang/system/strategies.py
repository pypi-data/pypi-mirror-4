import domain

from longtang.actors import actors

class ActorRegistrationStrategy:

	def create_instance(self, unique_id, system_ref):
		raise NotImplemented()

	def create_ref(self, actor_instance, parent):
		raise NotImplemented()

	def signup(self, actor_ref, system_ref):
		raise NotImplemented()

	def start(self, actor_ref):
		raise NotImplemented()

class ActorTypeRegistrationStrategy(ActorRegistrationStrategy):
	def __init__(self, actor_type):
		self.__actor_type = actor_type

	def create_instance(self, unique_id, system_ref):
		return self.__actor_type(system_ref, unique_id)		

	def create_ref(self, actor_instance, parent):
		return domain.ActorRef(actor_instance, parent)

	def signup(self, actor_ref, system_ref):
		system_ref.register_actor(actor_ref)
		actor_ref.delegate_setup()
		system_ref.update_actor(actor_ref)

	def start(self, actor_ref):
		actor_ref.kickoff()

class ActorFactoryRegistrationStrategy(ActorRegistrationStrategy):
	def __init__(self, actor_factory):
		self.__actor_factory = actor_factory

	def create_instance(self, unique_id, system_ref):
		return self.__actor_factory.create(unique_id, system_ref)

	def create_ref(self, actor_instance, parent):
		return domain.ActorRef(actor_instance, parent)

	def signup(self, actor_ref, system_ref):
		system_ref.register_actor(actor_ref)
		actor_ref.delegate_setup()
		system_ref.update_actor(actor_ref)

	def start(self, actor_ref):
		actor_ref.kickoff()

class ActorSystemRegistration():

	def __init__(self, strategy, system_ref):
		self.__registration_strategy = strategy
		self.__system_ref = system_ref

	def add(self, unique_id, parent):
		actor_instance = self.__registration_strategy.create_instance(unique_id, self.__system_ref)
		actor_ref = self.__registration_strategy.create_ref(actor_instance, parent)

		self.__registration_strategy.signup(actor_ref, self.__system_ref)
		self.__registration_strategy.start(actor_ref)

		return actor_ref