from longtang.actors import messages

class CreateFolderFromMetadata(messages.TraceableActorMessage):
	def __init__(self, source_file, metadata, base_dir, tracking):
		messages.TraceableActorMessage.__init__(self, tracking)

		self.__source_file = source_file
		self.__metadata = metadata
		self.__base_dir = base_dir

	def source_file(self):
		return self.__source_file

	def metadata(self):
		return self.__metadata

	def base_dir(self):
		return self.__base_dir

class FolderFromMetadataSuccessfullyCreated(messages.TraceableActorMessage):
	def __init__(self, source_file, metadata, new_dir_path, tracking):
		messages.TraceableActorMessage.__init__(self, tracking)

		self.__source_file = source_file
		self.__metadata = metadata
		self.__new_dir_path = new_dir_path

	def source_file(self):
		return self.__source_file

	def metadata(self):
		return self.__metadata

	def new_dir_path(self):
		return self.__new_dir_path

class RenameFileFromMetadata(messages.TraceableActorMessage):
	def __init__(self, source_file, metadata, tracking):
		messages.TraceableActorMessage.__init__(self, tracking	)

		self.__source_file = source_file
		self.__metadata = metadata

	def source_file(self):
		return self.__source_file

	def metadata(self):
		return self.__metadata

class FileSuccessfullyRenamed(messages.TraceableActorMessage):
	def __init__(self, source_file, metadata, new_file, tracking):
		messages.TraceableActorMessage.__init__(self, tracking)

		self.__source_file = source_file
		self.__metadata = metadata
		self.__new_file = new_file

	def source_file(self):
		return self.__source_file

	def metadata(self):
		return self.__metadata

	def new_file(self):
		return self.__new_file

class CopyFileTo(messages.TraceableActorMessage):
	def __init__(self, source_file, metadata, copy_to_path, tracking):
		messages.TraceableActorMessage.__init__(self, tracking)

		self.__source_file = source_file
		self.__metadata = metadata
		self.__copy_to_path = copy_to_path

	def source_file(self):
		return self.__source_file

	def metadata(self):
		return self.__metadata

	def copy_to_path(self):
		return self.__copy_to_path

class FileSuccessfullyCopied(messages.TraceableActorMessage):
	def __init__(self, source_file, metadata, copied_file, tracking):
		messages.TraceableActorMessage.__init__(self, tracking)

		self.__source_file = source_file
		self.__metadata = metadata
		self.__copied_file = copied_file

	def source_file(self):
		return self.__source_file

	def metadata(self):
		return self.__metadata

	def copied_file(self):
		return self.__copied_file

class CopyFileToFailed(messages.TraceableActorFailureMessage):
	def __init__(self, tracking, source_message, reason):
		messages.TraceableActorFailureMessage.__init__(self, tracking, reason, source_message)

	def source_file(self):
		return self.source_message().source_file()

	def metadata(self):
		return self.source_message().metadata()

	def copy_to_path(self):
		return self.source_message().copy_to_path()

class RenameFileFromMetadataFailed(messages.TraceableActorFailureMessage):
	def __init__(self, tracking,source_message, reason):
		messages.TraceableActorFailureMessage.__init__(self, tracking, reason, source_message)

	def source_file(self):
		return self.source_message().source_file()

	def metadata(self):
		return self.source_message().metadata()


class CreateFolderFromMetadataFailed(messages.TraceableActorFailureMessage):
	def __init__(self, tracking, source_message, reason):
		messages.TraceableActorFailureMessage.__init__(self, tracking, reason, source_message)

	def source_file(self):
		return self.source_message().source_file()

	def metadata(self):
		return self.source_message().metadata()

	def base_dir(self):
		return self.source_message().base_dir()