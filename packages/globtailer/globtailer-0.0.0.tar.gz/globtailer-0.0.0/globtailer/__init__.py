import glob
import logging
import os
import time


class TailMostRecentlyModifiedFileMatchingGlobPatternGenerator(object):
    """A generator that yields lines from the most recently modified file
    matching a glob pattern.

    This is useful if you are trying to consume log files that may rotate while
    you're reading them. For example, in my case, I am consuming log files with
    filenames of the form:

      applog.%H.%M

    where %H is the current hour and %M is the current minute.

    """


    def __init__(self, glob_pattern, interval=1, max_duration=None):
        self.glob_pattern = glob_pattern
        self.interval = interval
        self.max_duration = max_duration
        self.logger = logging.getLogger(self.__class__.__name__)


    def __iter__(self):
        most_recent_filename = self.get_most_recent_filename()
        previous_most_recent_filename = most_recent_filename

        if most_recent_filename:
            input_file = open(most_recent_filename)
            input_file.seek(0, 2)  # Seek to end of file
            offset = input_file.tell()
            input_file.close()
            self.on_start_watching_file(most_recent_filename)

        self.start_time = time.time()

        while self.max_duration is None or time.time() - self.start_time < self.max_duration:
            if most_recent_filename:
                with open(most_recent_filename) as input_file:
                    input_file.seek(offset, 0)

                    # I use a while loop and file.readline() instead of using a for loop:
                    # for line in input_file:
                    # The reason is that the for loop calls next() and triggers this error:
                    # IOError: telling position disabled by next() call
                    while True:
                        line = input_file.readline()
                        if line == '': break
                        yield self.yield_transformer(input_file, offset, line)
                        offset = input_file.tell()

            most_recent_filename = self.get_most_recent_filename()

            if most_recent_filename != previous_most_recent_filename:
                offset = 0
                self.on_switch_to_newer_file(most_recent_filename)

            previous_most_recent_filename = most_recent_filename
            time.sleep(self.interval)


    def yield_transformer(self, input_file, offset, line):
        """This simple method controls what the generator will yield.

        It's only reason for existence is so that folks can subclass and
        override this to make the generator return more information.

        """
        return line


    def get_most_recent_filename(self):
        """Get filename that matches self.glob_pattern and has most recent modification time."""

        # List of tuples (mtime, filename), sorted by mtime
        data = sorted([(os.stat(fn).st_mtime, fn) for fn in glob.glob(self.glob_pattern)])

        # Get the last tuple in list sorted by mtime and return the filename 
        if len(data) > 0:
            return data[-1][1]


    def on_start_watching_file(self, filename):
        self.logger.info("Started watching file %r" % filename)


    def on_switch_to_newer_file(self, filename):
        self.logger.info("Switched to new file %r" % filename)


class GetMostRecentlyModifiedFileMatchingGlobPatternGenerator(TailMostRecentlyModifiedFileMatchingGlobPatternGenerator):

    def yield_transformer(self, input_file, offset, line):
        return (input_file, offset, line)
