import gevent
import domain
import strategies
import exceptions
import deadletters
import syslogger
import properties

class ActorSystem():

	def __init__(self, props=None):
		self.__props=props

		if self.__props is None:
			self.__props = properties.SystemPropertiesBuilder().build() #grab defaults

		self.__actors_ref={}
		self.__actors_hierarchy={}
		self.__dead_letters_manager = deadletters.DeadLettersManager()
		self.__dead_letters_actor_ref = self.__dead_letters_manager.register_within_system(self)
		self.__syslogger = syslogger.SystemLoggerFactory.createIfAbsent(self, self.__props.verbosity)

	def __resolve_parent(self, parent):
		if parent is not None:
			if not isinstance(parent, deadletters.DeadLetters):
				return parent
			else:
				return None
		else:
			return self.__dead_letters_actor_ref

	def _register_actor_ref(self, actor_ref):
		self.__actors_ref[actor_ref.unique_id()] = actor_ref

		if actor_ref.parent() is not deadletters.DeadLetters.ROOT_PARENT:
			if actor_ref.parent().unique_id() in self.__actors_hierarchy.keys():
				self.__actors_hierarchy[actor_ref.parent().unique_id()].append(actor_ref.unique_id())
			else:
				self.__actors_hierarchy[actor_ref.parent().unique_id()]=[actor_ref.unique_id()]
		else:
			#We've just received dead-letters
			self.__actors_hierarchy[actor_ref.unique_id()]=[]

	def _update_actor_ref(self, actor_ref):
		self.__actors_ref[actor_ref.unique_id()] = actor_ref		

	def from_type(self, actor_type, unique_id, parent=None):
		strategy = strategies.ActorTypeRegistrationStrategy(actor_type)
		return self.__add_actor(strategy, unique_id, parent)

	def with_factory(self, factory, unique_id, parent=None):
		strategy = strategies.ActorFactoryRegistrationStrategy(factory)
		return self.__add_actor(strategy, unique_id, parent)

	def shutdown(self):
		xx = [actor._instance() for actor in self.__actors_ref.itervalues()]

		#TODO Tell dead_letters to finish
		#TODO Tell logger to finish

		gevent.killall(xx,gevent.GreenletExit,True)

	def wait_for(self, actor_ref):
		gevent.joinall([actor_ref._instance()])

	def __add_actor(self, strategy, unique_id, parent):
		actor_reg = strategies.ActorSystemRegistration(strategy, domain.WritableSystemRef(self))
		actor_ref = actor_reg.add(unique_id, self.__resolve_parent(parent))

		try:
			self.active_logger().debug(None, "{0}....Created".format(actor_ref), None)
		except AttributeError as e:
			pass #Omitted because logger is being built in contructor method

		return actor_ref

	def find_by_id(self, unique_id):
		try:
			return self.__actors_ref[unique_id]
		except KeyError as e:
			raise exceptions.ActorNotFound(unique_id)

	def get_parent(self, unique_id):
		return self.find_by_id(unique_id).parent()

	def get_child(self, child_unique_id, parent_unique_id):
		try:
			children = self.__actors_hierarchy[parent_unique_id]

			if child_unique_id in children:
				return self.__actors_ref[child_unique_id]
			else:
				raise exceptions.ActorNotFound(child_unique_id, 'Is {0} his actual parent?'.format(parent_unique_id))			

		except KeyError as e:
			raise exceptions.ActorNotFound(parent_unique_id)

	def is_child_of(unique_id, parent_unique_id):

		try:
			self.get_child(unique_id, parent_unique_id)
		except exceptions.ActorNotFound:
			return False

		return True


	def get_children(self, parent_unique_id):
		try:
			children = self.__actors_hierarchy[parent_unique_id]
			return [self.__actors_ref[child] for child in children]
		except KeyError as e:
			raise exceptions.ActorNotFound(parent_unique_id)

	def have_children(self, parent_unique_id):
		try:
			return len(self.get_children(parent_unique_id)) > 0
		except exceptions.ActorNotFound as e:
			return False

	def marooned_messages(self):
		return self.__dead_letters_manager

	def active_logger(self):
		return self.__syslogger