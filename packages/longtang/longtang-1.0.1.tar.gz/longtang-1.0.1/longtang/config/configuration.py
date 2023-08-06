class LongTangConfiguration():
	
	def __init__(self):
		self.__read_from=None
		self.__generate_at=None
		self.__override_tags=None
		self.__offline_mode=None

	@property
	def read_from(self):
		return self.__read_from

	@read_from.setter
	def read_from(self,value):
		self.__read_from=value

	@property
	def generate_at(self):
		return self.__generate_at

	@generate_at.setter
	def generate_at(self,value):
		self.__generate_at=value

	@property
	def override_tags(self):
		return self.__override_tags

	@override_tags.setter
	def override_tags(self, value):
		self.__override_tags = value

	@property
	def offline_mode(self):
		return self.__override_tags

	@offline_mode.setter
	def offline_mode(self, value):
		self.__offline_mode = value


class LongTangConfigurationBuilder():

	def __init__(self):
		self.__read_from=None
		self.__generate_at=None
		self.__override_tags=False
		self.__offline_mode=False

	def read_from(self, path):
		self.__read_from=path
		return self

	def generate_at(self, path):
		self.__generate_at=path
		return self

	def override_tags(self, value):
		self.__override_tags=value
		return self

	def offline_mode(self, value):
		self.__offline_mode=value
		return self

	def build(self):
		config = LongTangConfiguration()

		#TODO We have to check whether the minimum values have been informed
		config.read_from=self.__read_from
		config.generate_at=self.__generate_at
		config.override_tags=self.__override_tags
		config.offline_mode=self.__offline_mode

		return config