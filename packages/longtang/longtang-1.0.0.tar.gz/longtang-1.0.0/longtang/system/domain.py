from longtang.actors import domain

class SystemRef():
	def __init__(self, system_instance):
		self.__system_instance = system_instance

	def get_parent(self, unique_id):
		return self.__system_instance.get_parent(unique_id)

	def get_by_id(self,unique_id):
		return self.__system_instance.find_by_id(unique_id)

	def from_type(self, actor_type, unique_id, parent):
		return self.__system_instance.from_type(actor_type, unique_id, parent)

	def with_factory(self, factory_instance, unique_id, parent):
		return self.__system_instance.with_factory(factory_instance, unique_id, parent)		

	def get_child(self, child_unique_id, parent_unique_id):
		return self.__system_instance.get_child(child_unique_id, parent_unique_id)

	def get_children(self, parent_unique_id):
		return self.__system_instance.get_children(parent_unique_id)

	def have_children(self, parent_unique_id):
		return self.__system_instance.have_children(parent_unique_id)

	def notify_marooned_message(self, message, notifier):
		self.__system_instance.marooned_messages().report(notifier, message)

	def logger(self):
		return self.__system_instance.active_logger()

	def _system_instance(self):
		return self.__system_instance

class WritableSystemRef(SystemRef):
	def __init__(self, system_instance):
		SystemRef.__init__(self, system_instance)

	def register_actor(self, actor_ref):
		self._system_instance()._register_actor_ref(actor_ref)

	def update_actor(self, actor_ref):
		self._system_instance()._update_actor_ref(actor_ref)		

class ActorRef():
	def __init__(self, actor_instance, parent):
		self.__actor_instance = actor_instance
		self.__parent = parent

	def status(self):
		return self.__actor_instance.status()

	def context(self):
		return self.__actor_instance.context()

	def tell(self,message, sender=None):
		self.__actor_instance.tell(message, sender)

	def _instance(self):
		return self.__actor_instance

	def parent(self):
		return self.__parent

	def delegate_setup(self):
		self.__actor_instance.pre_setup()

	def kickoff(self):
		self.__actor_instance.start()

	def type(self):
		return self.__actor_instance.__class__

	def unique_id(self):
		return self.__actor_instance.unique_id()

	def is_terminated(self):
		return self.__actor_instance.is_terminated()

	def __str__(self):
		return "ActorRef[type={0}, unique_id={1}, parent={2}]".format(self.__actor_instance.__class__.__name__, self.__actor_instance.unique_id(), self.__parent)

class ActorFactory():
	def create(self, unique_id, system_ref):
		raise NotImplemented()