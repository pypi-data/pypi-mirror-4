from longtang.common import domain as common_domain

class AcoustidResponseWrapper():
	def __init__(self, response):
		self.__response=response

	def album(self):
		if 'results' in self.__response:
			if len(self.__response['results']) > 0:
				if 'recordings' in self.__response['results'][0]:
					if len(self.__response['results'][0]['recordings']) > 0:
						if 'releasegroups' in self.__response['results'][0]['recordings'][0]:
							if len(self.__response['results'][0]['recordings'][0]['releasegroups']) > 0:
								return self.__response['results'][0]['recordings'][0]['releasegroups'][0]['title']

		return None

	def artist(self):
		if 'results' in self.__response:
			if len(self.__response['results']) > 0:
				if 'recordings' in self.__response['results'][0]:
					if len(self.__response['results'][0]['recordings']) > 0:
						if 'artists' in self.__response['results'][0]['recordings'][0]:
							if len(self.__response['results'][0]['recordings'][0]['artists']) > 0:
								return self.__response['results'][0]['recordings'][0]['artists'][0]['name']

		return None

	def title(self):
		if 'results' in self.__response:		
			if len(self.__response['results']) > 0:
				if 'recordings' in self.__response['results'][0]:
					if len(self.__response['results'][0]['recordings']) > 0:
						return self.__response['results'][0]['recordings'][0]['title']

		return None

	def found(self):

		return self.album() is not None and self.artist() is not None and self.title() is not None

	def successful(self):
		return self.__response['status'] == 'ok'

	def extract_metadata(self):
		builder = common_domain.FileMetadataBuilder()

		return builder.artist(self.artist()) \
						.album(self.album()) \
						.title(self.title()).build()