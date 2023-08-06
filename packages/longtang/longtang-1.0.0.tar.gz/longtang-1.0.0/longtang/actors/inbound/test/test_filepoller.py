# -*- coding: utf-8 -*-

#http://docs.python.org/2/library/unittest.html#unittest.TestCase.assertEqual

import unittest
import os

from longtang.actors.inbound import filepoller, messages as fp_messages
from longtang.actors import testutils, messages

class TestFilePollerActor(unittest.TestCase):

    def test_filepoller(self):

    	data_dir = os.path.join(testutils.current_dirpath(__file__), 'data')

        poller_tester = testutils.TestActorBuilder().withType(filepoller.FilePoller).build()

        poller_tester.tell(fp_messages.StartPolling(data_dir))

        self.assertEqual(poller_tester.inspector().num_instances(), 5, 'Total amount of messages received is wrong')
        self.assertEqual(poller_tester.inspector().num_instances(fp_messages.AudioFileFound), 3, 'Total amount of AudioFileFound messages received is wrong')
        self.assertEqual(poller_tester.inspector().num_instances(fp_messages.FilePollingDone), 1, 'Total amount of FilePollingDone messages received is wrong')
        self.assertEqual(poller_tester.inspector().num_instances(messages.Terminated), 1, 'Total amount of Terminated messages received is wrong')

        self.assertIsNotNone(poller_tester.inspector().get_first(fp_messages.AudioFileFound).filepath(), 'File descriptor is empty or wrong')

    def test_encoding_filepoller(self):

        data_dir = os.path.join(testutils.current_dirpath(__file__), 'anóther_daña')

        poller_tester = testutils.TestActorBuilder().withType(filepoller.FilePoller).build()

        poller_tester.tell(fp_messages.StartPolling(data_dir))

        self.assertEqual(poller_tester.inspector().num_instances(), 4, 'Total amount of messages received is wrong')
        self.assertEqual(poller_tester.inspector().num_instances(fp_messages.AudioFileFound), 2, 'Total amount of AudioFileFound messages received is wrong')
        self.assertEqual(poller_tester.inspector().num_instances(fp_messages.FilePollingDone), 1, 'Total amount of FilePollingDone messages received is wrong')
        self.assertEqual(poller_tester.inspector().num_instances(messages.Terminated), 1, 'Total amount of Terminated messages received is wrong')

        self.assertIsNotNone(poller_tester.inspector().get_first(fp_messages.AudioFileFound).filepath(), 'File descriptor is empty or wrong')

if __name__ == '__main__':
    unittest.main()    