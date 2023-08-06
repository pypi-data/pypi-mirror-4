#https://github.com/hamcrest/PyHamcrest
#http://packages.python.org/PyHamcrest/

from longtang.common import mediatracking
import unittest

from hamcrest import *

class MediaTrackingTest(unittest.TestCase):

	def test_creation(self):

		full_filepath = '/dummy_path.mp3'
		descriptor = mediatracking.MediaFileDescriptorBuilder().sourcepath(full_filepath).build()
		file_tracking = mediatracking.MediaFileTracking.create_from(descriptor)

		assert_that(file_tracking.mediafile.sourcepath, is_(not_none()), 'Media file path is empty')
		assert_that(file_tracking.mediafile.sourcepath, is_(equal_to(full_filepath)), 'Media file path value is wrong')
		assert_that(file_tracking.tracking_events, is_(not_none()), 'Tracking events has not being initialized')
		assert_that(file_tracking.tracking_events.is_empty(), is_(True), 'Tracking events is not empty')

	def test_add_tracking_event(self):

		full_filepath = '/dummy_path.mp3'
		descriptor = mediatracking.MediaFileDescriptorBuilder().sourcepath(full_filepath).build()
		file_tracking = mediatracking.MediaFileTracking.create_from(descriptor)

		file_tracking.track_activity(mediatracking.MediaFileTrackingEvent('my-unique-type', 'short description', {'value-of-interest1':1000, 'value-of-interes2':'testing'}))		

		assert_that(file_tracking.tracking_events.is_empty(), is_(False), 'Tracking events is empty')
		assert_that(file_tracking.tracking_events.get_all(), is_(not_none()), 'All tracking event list is empty')
		assert_that(file_tracking.tracking_events.get_all().size(), is_(equal_to(1)), 'All tracking event list has not the right size')
		assert_that(file_tracking.tracking_events.of_type('my-unique-type').is_empty(), is_(False), 'Tracking events of type \'my-unique-type\' is empty')
		assert_that(file_tracking.tracking_events.of_type('my-unique-type').get(0), is_(not_none()), 'First tracking event could not be found')
		assert_that(file_tracking.tracking_events.of_type('my-unique-type').get_all(), is_(not_none()), 'First tracking event could not be found')
		assert_that(file_tracking.tracking_events.of_type('my-unique-type').get_all().size(), is_(equal_to(1)), 'Tracking event list of type \'my-unique-type\' has not the right size')

	def test_add_altering_tracking_event(self):
		pass


	
