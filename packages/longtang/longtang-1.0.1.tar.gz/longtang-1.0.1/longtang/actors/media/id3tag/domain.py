from mutagen.easyid3 import EasyID3
from mutagen.id3 import TIT2, TALB, TRCK, TPE1
from mutagen.mp3 import MP3
from longtang.common import domain as common_domain

class ID3TagReaderFactory():

	@staticmethod
	def createFromType(source):
		if source.lower().endswith('mp3'):
			return Mp3ID3TagReader(source)

class ID3TagWriterFactory():

	@staticmethod
	def createFromType(source):
		if source.lower().endswith('mp3'):
			return Mp3ID3TagWriter(source)

class ID3TagReader():

	def artist(self):
		raise NotImplemented()

	def title(self):
		raise NotImplemented()

	def album(self):
		raise NotImplemented()

	def track_number(self):
		raise NotImplemented()

	def extract_metadata(self):

		builder = common_domain.FileMetadataBuilder()

		return builder.artist(self.artist()) \
						.album(self.album()) \
						.title(self.title()) \
						.track_number(self.track_number()).build()

class SimpleID3TagReader(ID3TagReader):

	#List all supported labels by mutagen: print EasyID3.valid_keys.keys()

	def __init__(self, source_file):
		self.__source_file = source_file

	def source_file(self):
		return self.__source_file

	def artist(self):
		return self.__read_tag('artist')

	def title(self):
		return self.__read_tag('title')

	def album(self):
		return self.__read_tag('album')

	def track_number(self):
		return self.__read_tag('tracknumber')

	def __read_tag(self, tagname):
		try:
			reader = EasyID3(self.__source_file)
			return reader[tagname][0]
		except KeyError:
			return None

class Mp3ID3TagReader(SimpleID3TagReader):

	def __init__(self, source_file):
		SimpleID3TagReader.__init__(self,source_file)

	def artist(self):
		return self.__read_tag('TPE1')

	def title(self):
		return self.__read_tag('TIT2')

	def album(self):
		return self.__read_tag('TALB')

	def track_number(self):
		return self.__read_tag('TRCK')

	def __read_tag(self, tagname):
		reader = MP3(self.source_file())
		reader.encoding=3 #utf8
		return reader[tagname].text[0] if tagname in reader else None

class ID3TagWriter():

	def save(metadata):
		raise NotImplemented()

class SimpleID3TagWriter(ID3TagWriter):
	def __init__(self, target_file):
		self.__target_file = target_file

	def target(self):
		return self.__target_file

	def save(self, metadata):

		writer = EasyID3(target_file)

		writer['artist'] = metadata.artist
		writer['title'] = metadata.title
		writer['album'] = metadata.album
		writer['tracknumber'] = metadata.track_number

		writer.save()

class Mp3ID3TagWriter(SimpleID3TagWriter):

	def __init__(self, target_file):
		SimpleID3TagWriter.__init__(self,target_file)

	def save(self, metadata):

		#reference: http://en.wikipedia.org/wiki/ID3

		audio_file = MP3(self.target())

		audio_file['TIT2'] = TIT2(encoding=3, text=[metadata.title]) #Title
		audio_file['TALB'] = TALB(encoding=3, text=[metadata.album]) #Album
		audio_file['TRCK'] = TRCK(encoding=3, text=[metadata.track_number]) #track
		audio_file['TPE1'] = TPE1(encoding=3, text=[metadata.artist]) #Artist

		audio_file.save()


