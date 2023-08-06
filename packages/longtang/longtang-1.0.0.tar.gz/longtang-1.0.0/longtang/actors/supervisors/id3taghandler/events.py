from longtang.common import mediatracking

class MetadataAvailable(mediatracking.MediaFileTrackingEvent):
	def __init__(self):
		mediatracking.MediaFileTrackingEvent.__init__(self, "METADATA_AVAILABLE", "Metadata is fully available")

class MetadataNotAvailable(mediatracking.MediaFileTrackingEvent):
	def __init__(self):
		mediatracking.MediaFileTrackingEvent.__init__(self, "METADATA_NOT_AVAILABLE_FAILURE", "Metadata could not be completed")

class MetadataEvaluationFailed(mediatracking.MediaFileTrackingEvent):
	def __init__(self):
		mediatracking.MediaFileTrackingEvent.__init__(self, "METADATA_EVALUATION_FAILURE", "Metadata could not be evaluated from file")		

class MetadataInspectionStarted(mediatracking.MediaFileTrackingEvent):
	def __init__(self):
		mediatracking.MediaFileTrackingEvent.__init__(self, "METADATA_INSPECTION_STARTED", "Metadata inspection from file started")

class FileMetadataIncomplete(mediatracking.MediaFileTrackingEvent):
	def __init__(self):
		mediatracking.MediaFileTrackingEvent.__init__(self, "FILE_METADATA_INCOMPLETE", "Metadata is incomplete. Trying MusicBrainz")

class MusicbrainzServiceFailed(mediatracking.MediaFileTrackingEvent):
	def __init__(self):
		mediatracking.MediaFileTrackingEvent.__init__(self, "MUSICBRAINZ_SERVICE_FAILURE", "Musicbrainz service is not responding")	
