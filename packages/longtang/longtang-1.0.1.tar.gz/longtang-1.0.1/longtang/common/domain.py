import sys

class FileMetadata(object):

	def __init__(self):
		self.__artist=None
		self.__title=None
		self.__album=None
		self.__track_number=None

	def __capitalize_words(self, source_str):
		if source_str is not None:
			return ' '.join(word[0].upper() + word[1:] for word in source_str.lower().split())
		else:
			return source_str

	@property
	def artist(self):
		return self.__artist

	@artist.setter
	def artist(self, value):
		self.__artist = self.__capitalize_words(value)

	@property
	def title(self):
		return self.__title

	@title.setter
	def title(self, value):
		self.__title = self.__capitalize_words(value)

	@property
	def album(self):
		return self.__album

	@album.setter
	def album(self, value):
		self.__album = self.__capitalize_words(value)

	@property
	def track_number(self):
		return self.__track_number

	@track_number.setter
	def track_number(self, value):
		try:
			if value is not None:
				self.__track_number = int(value)
		except ValueError:
			#Potencially the value is not a number, we leave the tag empty
			pass 

	def missing_tags(self):
		if self.album is None:
			return True

		if self.artist is None:
			return True			

		if self.title is None:
			return True

		if self.is_track_number_missing():
			return True

		return False

	def is_track_number_missing(self):
		if self.track_number is None:
			return True

		return False		

	def __encode_value(self, value):
		if value is not None:
			return value.encode(sys.getdefaultencoding(),'replace')

		return value


	def __str__(self):
		return u'[artist: {0}, title: {1}, album: {2}, track: {3}]'.format(self.__artist, self.__title, self.__album, self.__track_number)					

class FileMetadataBuilder:
	
	def __init__(self):
		self.__artist=None
		self.__title=None
		self.__album=None
		self.__track_number=None

	def artist(self, artist):
		self.__artist = artist
		return self

	def title(self, title):
		self.__title = title
		return self

	def album(self, album):
		self.__album=album
		return self

	def track_number(self, track_number):
		self.__track_number=track_number
		return self

	def build(self):
		metadata = FileMetadata()

		metadata.artist=self.__artist
		metadata.title=self.__title
		metadata.album=self.__album
		metadata.track_number=self.__track_number

		return metadata

class FileMetadataBlender:
	
	def __init__(self):
		self.__from=None
		self.__with=None
		self.__override=False

	def from_base(self, metadata):
		self.__from = metadata
		return self

	def using(self, metadata):
		self.__with = metadata
		return self

	def override(self, value):
		self.__override=value
		return self

	def blend(self):

		builder = FileMetadataBuilder()

		artist = self.__with.artist if self.__from.artist is None or self.__override else self.__from.artist
		album = self.__with.album if self.__from.album is None or self.__override else self.__from.album
		title = self.__with.title if self.__from.title is None or self.__override else self.__from.title
		track_number = self.__with.track_number if self.__from.track_number is None else self.__from.track_number

		return builder.artist(artist).album(album).title(title).track_number(track_number).build()