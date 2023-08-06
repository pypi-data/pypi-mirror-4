import domain
import itertools

from longtang.actors import actors, messages

class DeadLetters(actors.Actor):

	ROOT_PARENT='ROOT'

	def __init__(self, system_ref, unique_id, registry):
		actors.Actor.__init__(self,system_ref, unique_id)
		self.__registry=registry

	def receive(self, message):

		self.logger().info('Dead letter received....[reporter={0}, message={1}]'.format(message.reporter(), message.marooned_message()))

		self.__registry.append(message.reporter(),message.marooned_message())

class DeadLetterMessageReported(messages.ActorMessage):
	def __init__(self, reporter, message):
		self.__reporter=reporter
		self.__message=message

	def reporter(self):
		return self.__reporter

	def marooned_message(self):
		return self.__message

class DeadLettersManager:

	def __init__(self):
		self.__dead_letters_actor=None
		self.__registry=MaroonedMessagesRegistry()

	def report(self, reporter, message):
		self.__dead_letters_actor.tell(DeadLetterMessageReported(reporter,message))

	def reported_by(self, reporter):
		return self.__registry.reported_by(reporter)

	def register_within_system(self, system):
		self.__dead_letters_actor = system.with_factory(DeadLettersActorFactory(self.__registry), 'dead-letters', DeadLetters.ROOT_PARENT)
		return self.__dead_letters_actor

	def all(self):
		return self.__registry.all_messages()

class MaroonedMessagesRegistry:
	def __init__(self):
		self.__marooned_messages = {}

	def append(self, reporter, message):
		if reporter in self.__marooned_messages.keys():
			self.__marooned_messages[reporter].append(message)
		else:
			self.__marooned_messages[reporter] = [message]

	def reported_by(self, reporter):
		if reporter in self.__marooned_messages.keys():
			return MaroonedMessagesBrowser(self.__marooned_messages[reporter])
		else:
			return MaroonedMessagesBrowser()

	def all_messages(self):
		return MaroonedMessagesBrowser(list(itertools.chain(self.__marooned_messages.itervalues())))


class MaroonedMessagesBrowser():
	def __init__(self, messages=[]):
		self.__messages=messages

	def size(self):
		return len(self.__messages)

	def get(self, index):
		return self.__messages[index]

class DeadLettersActorFactory(domain.ActorFactory):

	def __init__(self, registry):
		self.__registry=registry

	def create(self, unique_id, system_ref):
		return DeadLetters(system_ref,unique_id,self.__registry)