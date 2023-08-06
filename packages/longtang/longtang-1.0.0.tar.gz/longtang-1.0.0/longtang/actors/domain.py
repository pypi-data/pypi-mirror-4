from longtang.actors.logger import messages

class Envelope:
    def __init__(self, message, sender):
        self.__message = message
        self.__sender = sender

    def message(self):
        return self.__message

    def sender(self):
        return self.__sender

class SystemRefWrapper():
    def __init__(self, system_ref, actor_inst):

        self.__system_ref = system_ref
        self.__actor_ref = actor_inst

    def from_type(self, actor_type, unique_id):
        self.__system_ref.from_type(actor_type, unique_id, self.__system_ref.get_by_id(self.__actor_ref.unique_id()))

    def with_factory(self, factory_instance, unique_id):
        self.__system_ref.with_factory(factory_instance, unique_id, self.__system_ref.get_by_id(self.__actor_ref.unique_id()))

    def child(self, child_unique_id):
        return self.__system_ref.get_child(child_unique_id, self.__actor_ref.unique_id())

    def get_by_id(self,unique_id):
        return self.__system_ref.get_by_id(unique_id)

    def _system_ref(self):
        return self.__system_ref

class LoggerHelper():

    def __init__(self, system_ref, actor_inst):
        self.__system_ref = system_ref
        self.__actor_inst = actor_inst

    def info(self, message, source_file=None):
        self.__system_ref.logger().info(self.__actor_inst.unique_id(), message, source_file)

    def error(self, message, source_file=None):
        self.__system_ref.logger().error(self.__actor_inst.unique_id(), message, source_file)

    def debug(self, message, source_file=None):
        self.__system_ref.logger().debug(self.__actor_inst.unique_id(), message, source_file)        

    def warn(self, message, source_file=None):
        self.__system_ref.logger().warn(self.__actor_inst.unique_id(), message, source_file)


class ActorStatus:
    READY = 'Ready'
    PREPARING = 'Preparing'
    RUNNING = 'Running'
    TERMINATING = 'Terminating'
    TERMINATED = 'Terminated'        