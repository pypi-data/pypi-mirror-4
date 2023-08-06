import gevent
import shutil
import tempfile
import os
import sys

from cStringIO import StringIO
from longtang.actors import actors, messages
from longtang.system import system, domain as sys_domain

class TestActor(actors.Actor):

	def __init__(self, config, system_ref, unique_id):
		actors.Actor.__init__(self, system_ref, unique_id)
		self.messages={}
		self.__actor_ref = None
		self.__config=config

	def pre_setup(self):

		if not self.__config.use_factory():
			self.__actor_ref=self.context().from_type(self.__config.actor_type,self.__config.unique_id)
		else:
			self.__actor_ref=self.context().with_factory(self.__config.factory_type,self.__config.unique_id)

	def __force_termination(self):
		self.logger().info('Moratorium expired, termination will be forced....')
		self.context().get_by_id(self.__config.unique_id).tell(messages.PoisonPill(), self)

	def receive(self, message):
		msg_type = message.__class__

		print 'Tester received message....{0}'.format(message)

		if msg_type in self.messages:
			self.messages[msg_type].append(message)
		else:
			self.messages[msg_type] = [message]

		if isinstance(message, messages.Terminated):
			self._silently_end()

		if self.__config.termination_type is not None:
			if isinstance(message, self.__config.termination_type):
				print 'Termination message type received....terminating'
				self.context().get_by_id(self.__config.unique_id).tell(messages.PoisonPill(), self)

	def test(self,message, sender=None):

		print 'Tester.....{0}'.format(message)

		actor_ref = self.context().get_by_id(self.__config.unique_id)

		actor_ref.tell(message, self)

		if self.__config.termination_type is None:
			actor_ref.tell(messages.PoisonPill(), self)
		else:
			moratorium = gevent.Greenlet(self.__force_termination)
			moratorium.start_later(self.__config.termination_moratorium)

		#TODO Should be able to work with system
		gevent.joinall([actor_ref._instance()])

	def inspector(self):
		return MessageSetInspector(self.messages)

	class TestActorContext():

		def __init__(self, current_message, test_actor_ref):
			self.current_message = current_message
			self.test_actor_ref = test_actor_ref

		def current_message(self):
			return self.current_message


class TestActorBuilder():
	def __init__(self):
		self.actor_type=None
		self.__factory_type=None
		self.__unique_id='random-id-to-be-generated'
		self.__termination_message_type=None
		self.__termination_moratorium=1 #Seconds
		self.__terminate_system=True

	def terminate_system(self, value):
		self.__terminate_system = value
		return self

	def withType(self, actor_type):
		self.actor_type = actor_type
		return self

	def withFactory(self, factory_type):
		self.__factory_type = factory_type
		return self		

	def terminationType(self, message_type):
		self.__termination_message_type = message_type
		return self

	def terminationMoratorium(self, time):
		self.__termination_moratorium=time
		return self

	def withId(self, unique_id):
		self.__unique_id=unique_id
		return self

	def build(self):
		
		actor_system = system.ActorSystem()

		config = TestActorConfiguration()

		config.actor_type = self.actor_type
		config.factory_type = self.__factory_type
		config.unique_id = self.__unique_id
		config.termination_type = self.__termination_message_type
		config.termination_moratorium = self.__termination_moratorium

		return TestActorRef(actor_system, actor_system.with_factory(TestActorFactory(config), 'testutils-test-actor'), self.__terminate_system)

class TestActorRef(sys_domain.ActorRef):
	def __init__(self, system, actor_ref, terminate=True):
		sys_domain.ActorRef.__init__(self, actor_ref._instance(), actor_ref.parent())
		self.__system=system
		self.__terminate=terminate

	def tell(self,message, sender=None):
		self._instance().test(message, sender)
		
		if self.__terminate is True:
			self.__system.shutdown()

	def inspector(self):
		return self._instance().inspector()

	def system(self):
		return self.__system

class TestActorConfiguration:

	def __init__(self):
		self.__termination_type = None
		self.__termination_moratorium = None
		self.__unique_id=None
		self.__actor_type=None
		self.__factory_type=None

	@property
	def factory_type(self):
		return self.__factory_type

	@factory_type.setter
	def factory_type(self, value):
		self.__factory_type=value

	@property
	def actor_type(self):
		return self.__actor_type

	@actor_type.setter
	def actor_type(self, value):
		self.__actor_type=value

	@property
	def unique_id(self):
		return self.__unique_id

	@unique_id.setter
	def unique_id(self, value):
		self.__unique_id=value

	@property
	def termination_type(self):
		return self.__termination_type

	@termination_type.setter
	def termination_type(self, value):
		self.__termination_type = value

	@property
	def termination_moratorium(self):
		return self.__termination_moratorium

	@termination_moratorium.setter
	def termination_moratorium(self, value):
		self.__termination_moratorium = value

	def use_factory(self):
		return True if self.__actor_type is None and self.factory_type is not None else False

class TestActorFactory(sys_domain.ActorFactory):
	def __init__(self, config):
		self.__config = config

	def create(self, unique_id, system_ref):
		return TestActor(self.__config, system_ref, unique_id)

class MessageSetInspector:
	def __init__(self, messages):
		self.messages = messages

	def num_instances(self,msg_type=None):

		def map_elements(msg_list):
			return len(msg_list)

		def reduce_elements(accum, value):
			return accum + value

		message_group = self.messages.itervalues()

		if msg_type is not None:
			try:
				message_group = [self.messages[msg_type]]
			except KeyError:
				message_group = [[]]

		return reduce(reduce_elements,map(map_elements, message_group))

	def get_first(self, msg_type):
		try:
			return self.messages[msg_type][0]
		except KeyError, e:
			return None
		

def current_dirpath(source_file):
	return os.path.dirname(os.path.realpath(source_file))

def copy_to_tmp(source, prefix='longtang_', suffix='.tmp', dir=None):

	tmp_file=tempfile.NamedTemporaryFile('w+b',-1,suffix, prefix, delete=False, dir=dir)

	print 'Temp path....{0}'.format(tmp_file.name)

	shutil.copy2(source,tmp_file.name)

	return tmp_file.name

def create_tmp_dir(prefix='tmp_', suffix='', target_dir=None):

	return tempfile.mkdtemp(suffix, prefix, target_dir)

def remove_tmp_dir(path):
	shutil.rmtree(path,True)

def remove_dir_content(path):
	for root, dirs, files in os.walk(path):
		for f in files:
			os.unlink(os.path.join(root, f))
		for d in dirs:
			shutil.rmtree(os.path.join(root, d))

class StdoutSniffer():

	def __init__(self):
		self.__backup=None
		self.__value=None

	def start(self):
		# setup the environment
		self.__backup = sys.stdout

		# ####
		sys.stdout = StringIO()     # capture output

	def stop(self):
		self.__value = sys.stdout.getvalue() # release output
		# ####

		sys.stdout.close()  # close the stream 
		sys.stdout = self.__backup # restore original stdout

	def value(self):
		return self.__value      
