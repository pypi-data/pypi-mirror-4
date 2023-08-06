# -*- coding: utf-8 -*-

import messages
import domain
import os
import shutil

from longtang.actors import actors

class FileManagerActor(actors.Actor):

	def receive(self, message):

		if isinstance(message, messages.RenameFileFromMetadata):
			
			self.logger().info(u'File renaming using metadata requested .....{0}'.format(message.metadata()), message.tracking()) 

			target_dir = os.path.dirname(message.source_file())

			current_filename, current_ext = os.path.splitext(message.source_file())
			new_filename = u'{track:02d} - {title}{ext}'.format(track=message.metadata().track_number, title=message.metadata().title, ext=current_ext)
			new_filepath = os.path.join(target_dir, new_filename)

			self.logger().info(u'Resolved file name....\'{0}\''.format(new_filename), message.tracking())

			try:
				os.rename(message.source_file(), new_filepath)

				self.sender().tell(\
					messages.FileSuccessfullyRenamed(message.source_file(), message.metadata(), new_filepath, message.tracking()),\
					self.myself())

			except OSError as e:

				self.logger().error(u'File rename could not be done. Reason: {0}'.format(str(e)), message.tracking())

				self.sender().tell(\
					messages.RenameFileFromMetadataFailed(message.tracking(), message, str(e)), self.myself())
 

		elif isinstance(message, messages.CopyFileTo):

			self.logger().info(u'Copying file to {0}'.format(message.copy_to_path()), message.tracking())
			
			current_filepath, current_filename = os.path.split(message.source_file())
			copied_filepath = os.path.join(message.copy_to_path(), current_filename)

			try:
				shutil.copy2(message.source_file(),os.path.join(message.copy_to_path(), copied_filepath))

				self.sender().tell(\
					messages.FileSuccessfullyCopied(message.source_file(), message.metadata(), copied_filepath, message.tracking()),\
					self.myself())	

			except IOError as e:

				self.logger().error(u'File copy operation could not be done. Reason: {0}'.format(str(e)), message.tracking())

				self.sender().tell(\
					messages.CopyFileToFailed(message.tracking(), message, str(e)), self.myself())
		
