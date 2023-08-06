#http://docs.python.org/2/howto/unicode

# -*- coding: utf-8 -*-

import fnmatch
import os
import messages
import types

from longtang.actors import actors

class FilePoller(actors.Actor):
	def receive(self, message):

		if isinstance(message, messages.StartPolling):

			source = message.source()

			if type(source) is not types.UnicodeType:
				source = unicode(message.source(), encoding='utf-8', errors='replace')

			self.logger().info(u'Polling request recieved. Polling source: {0}'.format(source))

			try:
				for root, dirnames, filenames in os.walk(source):
	  				for filename in fnmatch.filter(filenames, u'*.mp3'):

	  					full_path = os.path.join(root, filename)

						self.logger().info(u'New file found: {0}'.format(full_path))

						self.sender().tell(messages.AudioFileFound(full_path), self.myself())

				self.sender().tell(messages.FilePollingDone(), self.myself())
			except Exception as e:
				self.logger().warn(u'Polling process interrupted. Reason: {0}'.format(str(e)))
				self.sender().tell(messages.FilePollingDone(), self.myself())

		else: 
			self.notify_marooned_message(message)

