from longtang.actors import messages

class CreateTrackingEntry(messages.ActorMessage):
	def __init__(self, sourcepath):
		messages.ActorMessage.__init__(self)
		self.__sourcepath = sourcepath

	def sourcepath(self):
		return self.__sourcepath

class TrackingEntryCreated(messages.ActorMessage):
	def __init__(self, tracking_id):
		messages.ActorMessage.__init__(self)
		self.__tracking_id = tracking_id

	def tracking_id(self):
		return self.__tracking_id


class LookupTrackingEntry(messages.ActorMessage):
	def __init__(self, tracking_id):
		messages.ActorMessage.__init__(self)
		self.__tracking_id = tracking_id

	def tracking_id(self):
		return self.__tracking_id

class TrackingEntryFound(messages.ActorMessage):
	def __init__(self, tracking_info):
		messages.ActorMessage.__init__(self)
		self.__tracking_info = tracking_info

	def tracking_info(self):
		return self.__tracking_info	

class TrackingEntryNotFound(messages.ActorMessage):
	def __init__(self, tracking_id):
		messages.ActorMessage.__init__(self)
		self.__tracking_id = tracking_id

	def tracking_id(self):
		return self.__tracking_id

class RegisterTrackingEvent(messages.ActorMessage):
	def __init__(self, tracking_id, tracking_event):
		self.__tracking_id=tracking_id
		self.__tracking_event=tracking_event

	def tracking_id(self):
		return self.__tracking_id

	def tracking_event(self):
		return self.__tracking_event

class TrackingEventSuccessfullyRegistered(messages.ActorMessage):
	pass

class GenerateSummary(messages.ActorMessage):
	pass

class SummarySuccessfullyGenerated(messages.ActorMessage):
	def __init__(self, summary):
		self.__summary=summary

	def summary(self):
		return self.__summary