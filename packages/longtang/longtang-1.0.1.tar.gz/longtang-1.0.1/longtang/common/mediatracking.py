class MediaFileTracking():
	def __init__(self, descriptor):
		self.__descriptor=descriptor
		self.__events_container=TrackingEventsProcessor([])

	@staticmethod
	def create_from(descriptor):
		return MediaFileTracking(descriptor)

	@property
	def mediafile(self):
		return self.__descriptor

	@property
	def tracking_events(self):
		return self.__events_container.get_events_registry()

	def track_activity(self, track_event):
		self.__descriptor = self.__events_container.process(self.__descriptor, track_event)

class MediaFileTrackingEvent():

	def __init__(self, entry_type, description, context_information={}):
		self.__type=entry_type
		self.__description=description
		self.__context_info=context_information

	def type(self):
		return self.__type

	def description(self):
		return self.__description

	def context_information(self):
		return self.__context_info

	def process(self, file_descriptor):
		return file_descriptor

class MediaFileDescriptor:
	def __init__(self):
		self.__sourcepath=None
		self.__destinationpath=None

	@property
	def sourcepath(self):
		return self.__sourcepath

	@sourcepath.setter
	def sourcepath(self, value):
		self.__sourcepath=value

	@property
	def destinationpath(self):
		return self.__destinationpath

	@destinationpath.setter
	def destinationpath(self, value):
		self.__destinationpath=value

class MediaFileDescriptorBuilder:
	def __init__(self):
		self.__sourcepath=None

	def sourcepath(self, sourcepath):
		self.__sourcepath=sourcepath
		return self

	def build(self):
		descriptor=MediaFileDescriptor()
		descriptor.sourcepath=self.__sourcepath

		return descriptor

class TrackingEventsBrowser:
	def __init__(self, entries):
		self.__tracking_groups={}
		self.__tracking_entries=entries

		self.__group_entries(entries)

	def __group_entries(self, entries):
		for entry in entries:
			self.__assign_event_to_group(entry)

	def __assign_event_to_group(self, tracking_entry):

		if self.__tracking_groups.has_key(tracking_entry.type()):
			self.__tracking_groups[tracking_entry.type()].append(tracking_entry)
		else:
			self.__tracking_groups[tracking_entry.type()]=[tracking_entry]			

	def size(self):
		return len(self.__tracking_entries)

	def is_empty(self):
		return len(self.__tracking_entries) == 0

	def get_all(self):
		return TrackingEventsBrowser(self.__tracking_entries)

	def get(self, index):
		return self.__tracking_entries[index]

	def of_type(self, event_type):
		if self.__tracking_groups.has_key(event_type):
			return TrackingEventsBrowser(self.__tracking_groups[event_type])
		else:
			return TrackingEventsBrowser([])

	def __iter__(self):
		return iter(self.__tracking_entries)

class TrackingEventsProcessor():
	def __init__(self, entries):
		self.__tracking_entries=entries

	def process(self, current_descriptor, tracking_entry):
		self.__tracking_entries.append(tracking_entry)
		return tracking_entry.process(current_descriptor)

	def get_events_registry(self):
		return TrackingEventsBrowser(self.__tracking_entries)
