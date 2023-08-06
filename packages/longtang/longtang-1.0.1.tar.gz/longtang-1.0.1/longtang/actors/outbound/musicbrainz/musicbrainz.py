import messages
import acoustid
import domain

from longtang.actors import actors
from longtang.common import domain as common_domain

class MusicMetadataActor(actors.Actor):

    __ACCOUSTID_API_KEY = '77CFDtEG'

    def receive(self, message):

        if isinstance(message, messages.FillUpMissingMetadataFields):

            self.logger().info(u'Filling up id3tag information .....', message.tracking())

            try:
                duration, fingerprint = acoustid.fingerprint_file(message.source())

                response = domain.AcoustidResponseWrapper(acoustid.lookup(self.__ACCOUSTID_API_KEY, fingerprint, duration, 'recordings releasegroups compress'))

                if response.successful() and response.found():

                    retrieved_metadata = response.extract_metadata()

                    self.logger().info(u'Metadata successfully retrieved from MusicBrainz. {0}'.format(retrieved_metadata), message.tracking())

                    blender = common_domain.FileMetadataBlender()
                    metadata = blender.from_base(message.metadata()).using(retrieved_metadata).blend()

                    if metadata.missing_tags():
                        self.logger().error('Could\'t find all the required id3tag information .....', message.tracking())
                        self.sender().tell(messages.FillUpMissingMetadataFieldsFailed(message.tracking(), message, 'Missing metadata fields could not be resolved'), self.myself())
                    else:
                        self.logger().info(u'Metadata blended. {0}'.format(metadata), message.tracking())
                        self.sender().tell(messages.FileMetadataSuccessfullyFilled(message.source(), metadata, message.tracking()), self.myself())
                else:
                    self.logger().error('Could\'t find all the required id3tag information .....', message.tracking())
                    self.sender().tell(messages.FillUpMissingMetadataFieldsFailed(message.tracking(), message, 'Missing metadata fields could not be resolved'), self.myself())

            except (acoustid.WebServiceError,acoustid.FingerprintGenerationError, KeyError) as e:
                self.sender().tell(messages.MusicBrainzServiceFailed(message.source(), message.tracking()), self.myself())

        elif isinstance(message, messages.LookupFileMetadata):

            self.logger().info('Looking up id3tag information .....', message.tracking())

            try:
                duration, fingerprint = acoustid.fingerprint_file(message.source())

                response = domain.AcoustidResponseWrapper(acoustid.lookup(self.__ACCOUSTID_API_KEY, fingerprint, duration, 'recordings releasegroups compress'))

                if response.successful() and response.found():

                    retrieved_metadata = response.extract_metadata()

                    self.logger().info(u'Metadata successfully retrieved from MusicBrainz. {0}'.format(retrieved_metadata), message.tracking())

                    self.sender().tell(messages.FileMetadataFound(message.source(), retrieved_metadata, message.tracking()), self.myself())
                else:
                    self.sender().tell(messages.FileMetadataNotFound(message.source(), message.tracking()), self.myself())

            except (acoustid.WebServiceError,acoustid.FingerprintGenerationError, KeyError) as e:
                self.sender().tell(messages.MusicBrainzServiceFailed(message.source()), self.myself())

        elif isinstance(message, messages.OverrideFileMetadata):

            self.logger().info(u'Overriding id3tag information .....', message.tracking())

            try:
                duration, fingerprint = acoustid.fingerprint_file(message.source())

                response = domain.AcoustidResponseWrapper(acoustid.lookup(self.__ACCOUSTID_API_KEY, fingerprint, duration, 'recordings releasegroups compress'))

                if response.successful() and response.found():

                    retrieved_metadata = response.extract_metadata()

                    self.logger().info(u'Metadata successfully retrieved from MusicBrainz. {0}'.format(retrieved_metadata), message.tracking())

                    blender = common_domain.FileMetadataBlender()
                    metadata = blender.from_base(message.metadata()).using(retrieved_metadata).override(True).blend()

                    if metadata.missing_tags():
                        self.logger().error('Could\'t find all the required id3tag information .....', message.tracking())
                        self.sender().tell(messages.OverrideFileMetadataFailed(message.tracking(), message, 'Missing metadata fields could not be resolved'), self.myself())
                    else:
                        self.logger().info(u'Metadata blended. {0}'.format(metadata), message.tracking())
                        self.sender().tell(messages.OverrideFileMetadataDone(message.source(), metadata, message.tracking()), self.myself())
                else:
                    self.logger().error('Could\'t find all the required id3tag information .....', message.tracking())
                    self.sender().tell(messages.OverrideFileMetadataFailed(message.tracking(), message, 'Missing metadata fields could not be resolved'), self.myself())

            except (acoustid.WebServiceError,acoustid.FingerprintGenerationError, KeyError) as e:
                self.sender().tell(messages.MusicBrainzServiceFailed(message.source(), message.tracking()), self.myself())

        else: 
            self.notify_marooned_message(message)                                                    