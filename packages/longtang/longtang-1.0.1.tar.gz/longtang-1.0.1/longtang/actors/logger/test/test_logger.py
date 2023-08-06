import unittest
import os

from longtang.actors import testutils
from longtang.actors.logger import logger, messages, factory
from hamcrest import *


class TestLoggerActor(unittest.TestCase):

	def test_console_information_message(self):
		logger_tester = testutils.TestActorBuilder().withFactory(factory.LoggerActorFactory('DEBUG')).withId('logger-tester').build()

		logger_tester.tell(messages.FileInformationEventMessage('logger-tester','dummy.mp3','This is a simple information message'))

		assert_that(logger_tester.system().marooned_messages().reported_by('logger-tester'), is_(not_none()),'logger-tester actor marooned messages list is not none')
		assert_that(logger_tester.system().marooned_messages().reported_by('logger-tester').size(), is_(equal_to(0)),'logger-tester actor marooned messages list has elements')
		assert_that(logger_tester.system().marooned_messages().all(), is_(not_none()),'Global marooned messages list is not none')
		assert_that(logger_tester.system().marooned_messages().all().size(), is_(equal_to(0)),'Global marooned messages list is not empty')

	def test_console_error_message(self):
		logger_tester = testutils.TestActorBuilder().withFactory(factory.LoggerActorFactory('DEBUG')).withId('logger-tester').build()

		logger_tester.tell(messages.FileErrorEventMessage('logger-tester','dummy.mp3','This is a simple error message'))

		assert_that(logger_tester.system().marooned_messages().reported_by('logger-tester'), is_(not_none()),'logger-tester actor marooned messages list is not none')
		assert_that(logger_tester.system().marooned_messages().reported_by('logger-tester').size(), is_(equal_to(0)),'logger-tester actor marooned messages list has elements')
		assert_that(logger_tester.system().marooned_messages().all(), is_(not_none()),'Global marooned messages list is not none')
		assert_that(logger_tester.system().marooned_messages().all().size(), is_(equal_to(0)),'Global marooned messages list is not empty')

	def test_console_debug_message(self):
		logger_tester = testutils.TestActorBuilder().withFactory(factory.LoggerActorFactory('DEBUG')).withId('logger-tester').build()

		logger_tester.tell(messages.FileDebugEventMessage('logger-tester','dummy.mp3','This is a simple error message'))

		assert_that(logger_tester.system().marooned_messages().reported_by('logger-tester'), is_(not_none()),'logger-tester actor marooned messages list is not none')
		assert_that(logger_tester.system().marooned_messages().reported_by('logger-tester').size(), is_(equal_to(0)),'logger-tester actor marooned messages list has elements')
		assert_that(logger_tester.system().marooned_messages().all(), is_(not_none()),'Global marooned messages list is not none')
		assert_that(logger_tester.system().marooned_messages().all().size(), is_(equal_to(0)),'Global marooned messages list is not empty')		