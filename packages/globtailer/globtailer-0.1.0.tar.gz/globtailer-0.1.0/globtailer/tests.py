import logging
import multiprocessing
import os
import shutil
import tempfile
import time
import unittest

from globtailer import FileTailer

logging.basicConfig(level=logging.WARNING)


class BasicTestCase(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="python-globtailer-tests-")
        logging.info("Created temporary directory - %s" % self.tmpdir)
        self.tailer = FileTailer(self.get_path("log*"), max_duration=6)


    def tearDown(self):
        logging.info("Removing temporary directory - %s" % self.tmpdir)
        shutil.rmtree(self.tmpdir)
        logging.info("Removed temporary directory - %s" % self.tmpdir)


    def get_path(self, arg):
        return os.path.join(self.tmpdir, arg)


    def test_basic_use(self):
        with open(self.get_path("log.01.01"), "w") as f:
            f.write("line1\n")
            f.write("line2\n")
            f.write("line3\n")

        def write_to_log():
            time.sleep(1)

            with open(self.get_path("log.01.01"), "a") as f:
                f.write("line4\n")
                f.write("line5\n")
                f.write("line6\n")

            time.sleep(1)

            with open(self.get_path("log.01.02"), "a") as f:
                f.write("line7\n")
                f.write("line8\n")
                f.write("line9\n")

        self.assertEqual(self.tailer.glob_pattern, self.get_path("log*"))
        self.assertEqual(self.tailer.get_most_recent_filename(), self.get_path("log.01.01"))

        process = multiprocessing.Process(target=write_to_log)
        process.start()

        lines = [line for line in self.tailer]

        self.assertEqual(
            lines,
            ["line4\n", "line5\n", "line6\n",
             "line7\n", "line8\n", "line9\n"])

        process.join()


    def test_no_matching_files_to_start(self):
        def write_to_log():
            time.sleep(1)

            with open(self.get_path("log.01.01"), "a") as f:
                f.write("line4\n")
                f.write("line5\n")
                f.write("line6\n")

        self.assertEqual(self.tailer.glob_pattern, self.get_path("log*"))
        self.assertEqual(self.tailer.get_most_recent_filename(), None)

        process = multiprocessing.Process(target=write_to_log)
        process.start()

        lines = [line for line in self.tailer]

        self.assertEqual(lines, ["line4\n", "line5\n", "line6\n"])


    def test_no_matching_files(self):
        self.assertEqual(self.tailer.glob_pattern, self.get_path("log*"))
        self.assertEqual(self.tailer.get_most_recent_filename(), None)

        lines = [line for line in self.tailer]

        self.assertEqual(len(lines), 0)
