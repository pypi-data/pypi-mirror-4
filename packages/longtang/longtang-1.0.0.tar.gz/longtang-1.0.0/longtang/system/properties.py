class SystemProperties():

	def __init__(self):
		self.__verbosity=None

	@property
	def verbosity(self):
		return self.__verbosity

	@verbosity.setter
	def verbosity(self, level):
		self.__verbosity=level


class SystemPropertiesBuilder():

	def __init__(self):
		self.__verbosity=VerbosityLevel.DEBUG

	def verbosity(self, level):
		self.__verbosity=level
		return self

	def build(self):

		props = SystemProperties()

		props.verbosity=self.__verbosity

		return props

class VerbosityLevel:
    ERROR = 'ERROR'
    DEBUG = 'DEBUG'
    INFO = 'INFO'
    WARN = 'WARNING'