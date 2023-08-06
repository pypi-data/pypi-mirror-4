class ActivitySummary():

	def __init__(self, tracking_info):
		self.__tracking_info=tracking_info

	@staticmethod
	def create(tracking_info):
		return ActivitySummary(tracking_info)

	def total(self):
		return len(self.__tracking_info)

	def __is_failure(self, event):
		return 'FAILURE' in event.type()

	def __is_success(self, event):
		return not self.__is_failure(event)

	def __mediafile_failed(self, mediafile_tracking):
		for event in mediafile_tracking.tracking_events:
			if self.__is_failure(event):
				return True

		return False

	def total_failures(self):
		def map_elements(mediafile_tracking):
			if self.__mediafile_failed(mediafile_tracking):
				return 1

			return 0

		def reduce_elements(accum, value):
			return accum + value

		return reduce(reduce_elements,map(map_elements, self.__tracking_info.itervalues()))		

	def total_successes(self):
		def map_elements(mediafile_tracking):
			if self.__mediafile_failed(mediafile_tracking):
				return 0

			return 1

		def reduce_elements(accum, value):
			return accum + value

		return reduce(reduce_elements,map(map_elements, self.__tracking_info.itervalues()))

	def failures(self):
		for tracking_id, mediafile_tracking in self.__tracking_info.items():
			if self.__mediafile_failed(mediafile_tracking):
				yield tracking_id, mediafile_tracking

	def successes(self):
		for tracking_id, mediafile_tracking in self.__tracking_info.items():
			if not self.__mediafile_failed(mediafile_tracking):
				yield tracking_id, mediafile_tracking
