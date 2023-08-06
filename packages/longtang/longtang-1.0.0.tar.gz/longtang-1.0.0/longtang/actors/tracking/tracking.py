import messages
import hashlib
import summary
import sys

from longtang.actors import actors
from longtang.common import mediatracking

class TrackingActor(actors.Actor):

	def __init__(self, system_ref, unique_id):
		actors.Actor.__init__(self, system_ref, unique_id)

		self.__trackings={}

	def receive(self, message):
		if isinstance(message, messages.CreateTrackingEntry):
			self.logger().info(u'Creating tracking entry for source path {0} .....'.format(message.sourcepath()))
			descriptor = mediatracking.MediaFileDescriptorBuilder().sourcepath(message.sourcepath()).build()
			file_tracking = mediatracking.MediaFileTracking.create_from(descriptor)
			new_trackingid = hashlib.sha224(message.sourcepath().encode(sys.getdefaultencoding(),'replace')).hexdigest()

			self.__trackings[new_trackingid]=file_tracking

			self.sender().tell(messages.TrackingEntryCreated(new_trackingid), self.myself())

		elif isinstance(message, messages.LookupTrackingEntry):
			self.logger().info(u'Looking up tracking entry {0} .....'.format(message.tracking_id()))
			if self.__trackings.has_key(message.tracking_id()):
				self.sender().tell(messages.TrackingEntryFound(self.__trackings[message.tracking_id()]), self.myself())
			else:
				self.sender().tell(messages.TrackingEntryNotFound(message.tracking_id()), self.myself())	

		elif isinstance(message, messages.RegisterTrackingEvent):
			self.logger().info(u'Event of type \'{1}\' recieved for tracking id \'{0}\' .....'.format(message.tracking_id(),message.tracking_event().type()))

			if self.__trackings.has_key(message.tracking_id()):
				self.__trackings[message.tracking_id()].track_activity(message.tracking_event())

				if self.sender() is not None:
					self.sender().tell(messages.TrackingEventSuccessfullyRegistered(), self.myself())
			else:

				if self.sender() is not None:
					self.sender().tell(messages.TrackingEntryNotFound(message.tracking_id()), self.myself())

		elif isinstance(message, messages.GenerateSummary):
			self.sender().tell(messages.SummarySuccessfullyGenerated(summary.ActivitySummary.create(self.__trackings)), self.myself())			
		else: 
			self.notify_marooned_message(message)					