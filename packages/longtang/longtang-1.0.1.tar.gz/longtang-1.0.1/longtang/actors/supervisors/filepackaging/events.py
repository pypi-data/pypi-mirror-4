from longtang.common import mediatracking

class FilePackagingFinished(mediatracking.MediaFileTrackingEvent):
	def __init__(self, packaged_file):
		mediatracking.MediaFileTrackingEvent.__init__(self, "FILE_PACKAGING_DONE", "File has been successfully packaged")
		self.__packaged_file=packaged_file

	def process(self, file_descriptor):

		file_descriptor.destinationpath=self.__packaged_file
		return file_descriptor

class FileCopyFailed(mediatracking.MediaFileTrackingEvent):
	def __init__(self):
		mediatracking.MediaFileTrackingEvent.__init__(self, "FILE_COPY_FAILURE", "File could not be copied")

class FolderCreationFailed(mediatracking.MediaFileTrackingEvent):
	def __init__(self):
		mediatracking.MediaFileTrackingEvent.__init__(self, "FOLDER_CREATION_FAILURE", "Target folder could not be created")

class MetadataWritingFailed(mediatracking.MediaFileTrackingEvent):
	def __init__(self):
		mediatracking.MediaFileTrackingEvent.__init__(self, "METADATA_WRITING_FAILURE", "Metadata could not be persisted")

class PackagingStarted(mediatracking.MediaFileTrackingEvent):
	def __init__(self):
		mediatracking.MediaFileTrackingEvent.__init__(self, "PACKAGING_STARTED", "File packaging process started")
		
class TargetFolderCreated(mediatracking.MediaFileTrackingEvent):
	def __init__(self):
		mediatracking.MediaFileTrackingEvent.__init__(self, "TARGET_FOLDER_CREATED", "Target folder created")

class MediaFileCopied(mediatracking.MediaFileTrackingEvent):
	def __init__(self):
		mediatracking.MediaFileTrackingEvent.__init__(self, "MEDIAFILE_COPIED", "Media file copied")

class MetadataUpdated(mediatracking.MediaFileTrackingEvent):
	def __init__(self):
		mediatracking.MediaFileTrackingEvent.__init__(self, "METADATA_UPDATED", "Media file metadata updated")

class FileRenamingFailed(mediatracking.MediaFileTrackingEvent):
	def __init__(self):
		mediatracking.MediaFileTrackingEvent.__init__(self, "FILE_RENAMING_FAILURE", "Media file renaming process failed")

