# -*- coding: utf-8 -*-

#http://docs.python.org/2/library/logging.html#formatter-objects

import messages
import logging
import sys

from longtang.actors import actors

class LoggerActor(actors.Actor):

	def __init__(self, level, system_ref, unique_id):
		actors.Actor.__init__(self, system_ref, unique_id)

		self.__level=level

	def pre_setup(self):

		global my_logger

		if not globals().has_key('my_logger'):
			# create logger
			root_logger = logging.getLogger()
			root_logger.handlers = []

			my_logger = logging.getLogger('logger-actor')
			#my_logger.setLevel(logging.DEBUG)
			my_logger.setLevel(self.__level)
			#my_logger.propagate = False

			# create formatter
			formatter = logging.Formatter('[%(levelname)s][%(asctime)s][%(actor)s](%(source_file)s) @=> %(message)s')

			# create console handler and set level to debug
			ch = logging.StreamHandler(sys.stdout)
			ch.setLevel(logging.DEBUG)
			ch.setFormatter(formatter)

			# add handler to logger
			my_logger.addHandler(ch)

	def receive(self, message):

		if isinstance(message, messages.FileEventMessage):

			extra_info = {'actor': message.actor(), 'source_file': message.source_file()}
			if message.type() is 'INFO':
				my_logger.info(message.message(), extra=extra_info)
			elif message.type() is 'ERROR':
				my_logger.error(message.message(), extra=extra_info)
			elif message.type() is 'DEBUG':
				my_logger.debug(message.message(), extra=extra_info)
			elif message.type() is 'WARN':
				my_logger.warning(message.message(), extra=extra_info)
		else:
			self.notify_marooned_message(message)