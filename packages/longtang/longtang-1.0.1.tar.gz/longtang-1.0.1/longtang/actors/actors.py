#http://www.gevent.org/gevent.html#greenlet-objects

import gevent
import domain

from gevent.queue import Queue
from gevent.local import local
from longtang.actors import messages

class Actor(gevent.Greenlet):

    def __init__(self, system_ref, unique_id):
        gevent.Greenlet.__init__(self)
        self.__local_context=local()
        self.__inbox = Queue()
        self.__unique_id = unique_id
        self.__system_ref = system_ref
        self.__status = domain.ActorStatus.READY

    def status(self):
        return self.__status

    def receive(self, message):
        raise NotImplemented()

    def pre_setup(self):
        pass

    def _run(self):

        self.__status = domain.ActorStatus.RUNNING

        self.logger().debug('Running {0}'.format(self.__unique_id))

        self.running = True

        while self.running:
            envelope = self.__inbox.get()
            self.__local_context.sender=envelope.sender()
            self.__on_message(envelope.message())

    def __on_message(self,message):

        # 1- If current message is PoisonPill, then begin termination
        # 2- If current message is Terminated. If all children are dead then, current actor should call call self._silently_end()


        #TODO Maybe we could use a switch in here instead of an if statement
        if not self.is_terminating():
            
            self.logger().debug('New message received...[actor_id: {0}, message: {1}]'.format(self.unique_id(), message.__class__.__name__))
            
            if isinstance(message, messages.PoisonPill):
               
                # 1- If current has children, then should send each of them a poison pill and set current as TERMINATING
                # 2- If current has no children, call self._silently_end()

                self.__status = domain.ActorStatus.TERMINATING

                self.logger().debug('Start Termination...[actor_id: {0}, message: {1}]'.format(self.unique_id(), message.__class__.__name__))

                if self.__system_ref.have_children(self.unique_id()):

                    self.logger().debug('Notifying children...[actor_id: {0}, message: {1}]'.format(self.unique_id(), message.__class__.__name__))

                    children = self.__system_ref.get_children(self.unique_id())

                    for child in children:
                        if not child.is_terminated():
                            child.tell(messages.PoisonPill(), self.myself())
                else:
                    self.logger().debug('No children..so we kill ourself...[actor_id: {0}, message: {1}]'.format(self.unique_id(), message.__class__.__name__))
                    self._silently_end()
            else:
                self.receive(message)
        else:
            if isinstance(message, messages.Terminated):

                self.logger().debug('Child actor {2} finished...[actor_id: {0}, message: {1}]'.format(self.unique_id(), message.__class__.__name__, message.actor_id()))

                children = self.__system_ref.get_children(self.unique_id())

                should_terminate=True

                for child in children:
                    if not child.is_terminated():
                        should_terminate = False
                        break

                if should_terminate:
                    self.logger().debug('All children dead...terminating ourself...[actor_id: {0}, message: {1}]'.format(self.unique_id(), message.__class__.__name__))
                    self._silently_end()
            else:
                if self.__system_ref.is_child_of(self.sender().unique_id(), self.unique_id()):
                    self.receive(message)
                else:
                    self.logger().debug('Message ignored since we\'re in termination state. [Message: {0}]'.format(message))


    def context(self):
        return domain.SystemRefWrapper(self.__system_ref, self)

    def logger(self):
        return domain.LoggerHelper(self.__system_ref, self)

    def sender(self):
        return self.__local_context.sender

    def parent(self):
        return self.__system_ref.get_parent(self.__unique_id)

    def myself(self):
        return gevent.getcurrent()        

    def unique_id(self):
        return self.__unique_id

    def is_terminating(self):
        return self.__status is domain.ActorStatus.TERMINATING

    def is_terminated(self):
        return self.__status is domain.ActorStatus.TERMINATED

    def notify_marooned_message(self, message):
        self.__system_ref.notify_marooned_message(message, self.unique_id())

    def _silently_end(self):

        self.__status = domain.ActorStatus.TERMINATED

        self.logger().debug('Silently ending...[actor_id: {0}, sender: {1}]'.format(self.unique_id(), self.__local_context.sender))

        #TODO: Ufff...i need to check this one
        if self.parent().unique_id() != 'dead-letters':
            self.parent().tell(messages.Terminated(self.__unique_id))
            
        raise gevent.GreenletExit()

    def tell(self,message, sender=None):

        self.logger().debug('Telling....{0}_{1}'.format(self.__unique_id, message))

        self.__inbox.put(domain.Envelope(message, sender))

    def __str__(self):
        return "Actor[type={0}, unique_id={1}]".format(self.__class__.__name__, self.__unique_id)