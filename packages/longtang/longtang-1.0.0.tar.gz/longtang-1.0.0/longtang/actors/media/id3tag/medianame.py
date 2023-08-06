import re
import os

class MedianameEvaluator():
	def __init__(self, mediapath):
		self.__mediapath=mediapath

	@staticmethod
	def create_from_path(mediapath):
		return MedianameEvaluator(os.path.basename(mediapath))

	def evaluate(self):

		track_number = TrackNumberGuesser.make_a_guess(self.__mediapath)

		result = MedianameEvaluationResult()
		result.track_number = track_number

		return result

class MedianameEvaluationResult():
	
	def __init__(self):
		self.__track_number=None

	@property
	def track_number(self):
		return self.__track_number

	@track_number.setter
	def track_number(self, value):
		self.__track_number = value

class MediaTagGuesser():

	@staticmethod
	def guess_value(value):
		raise NotImplemented()



class TrackNumberGuesser(MediaTagGuesser):

	@staticmethod
	def make_a_guess(medianame):
		m = re.search('(?<!\.mp)([0-9]{1,3})', medianame)
		
		if m is not None:
			return m.group(0)
		else:
			return None