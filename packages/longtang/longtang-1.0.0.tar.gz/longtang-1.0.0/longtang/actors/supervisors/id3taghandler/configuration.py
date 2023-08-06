class Id3TagHandlerConfiguration():
	
	def __init__(self):
		self.__override_tags=None
		self.__offline_mode=None

	@property
	def override_tags(self):
		return self.__override_tags

	@override_tags.setter
	def override_tags(self, value):
		self.__override_tags = value

	@property
	def offline_mode(self):
		return self.__offline_mode

	@offline_mode.setter
	def offline_mode(self, value):
		self.__offline_mode = value

class Id3TagHandlerConfigurationBuilder():

	def __init__(self):
		self.__override_tags=False
		self.__offline_mode=False

	def override_tags(self, value):
		self.__override_tags=value
		return self

	def offline_mode(self, value):
		self.__offline_mode=value
		return self

	def build(self):
		config = Id3TagHandlerConfiguration()

		if self.__offline_mode and self.__override_tags:
			raise ValueError('Offline mode and Override tags are incompatible parameters. Only one of them should be enabled')

		config.override_tags=self.__override_tags
		config.offline_mode=self.__offline_mode

		return config