#!/usr/bin/env python2.7

import collections
import copy
import curses
import itertools
import json
import logging
import os
import Queue
import re
import subprocess
import sys
import threading
import time
import traceback

import pkg_resources

logging.basicConfig(level=logging.DEBUG if os.environ.get("DEBUG") else logging.ERROR,
                    format="%(asctime)s: %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")
_logger = logging.getLogger(__name__)

CONFIG_FN = pkg_resources.resource_filename(__name__, "conf/completeme.json")
def get_config(key, default="NO_DEFAULT"):
    """ Returns the value for the config key, loading first from the working directory and then the basic install point.  Can be overridden with CONFIG_FN environment variable. """

    def load_config():
        CONFIG_CACHE_KEY = "cached_config"
        if hasattr(get_config, CONFIG_CACHE_KEY):
            return getattr(get_config, CONFIG_CACHE_KEY)

        base_fn = os.path.basename(CONFIG_FN)
        fn_paths = [ os.path.join("conf", base_fn),
                     CONFIG_FN ]
        if "CONFIG_FN" in os.environ:
            fn_paths.append(os.environ["CONFIG_FN"])

        for fn in fn_paths:
            try:
                cfg = json.load(open(fn, "r"))
                setattr(get_config, CONFIG_CACHE_KEY, cfg)
                return cfg
            except IOError:
                pass

        raise Exception("Couldn't load config from any of {}".format(fn_paths))

    return load_config()[key] if default == "NO_DEFAULT" else load_config().get(key, default)

HIGHLIGHT_COLOR_PAIR = 1
STATUS_BAR_COLOR_PAIR = 2
NEWLINE = "^J"
TAB = "^I"
def init_screen():
    screen = curses.initscr()
    curses.start_color()
    curses.init_pair(HIGHLIGHT_COLOR_PAIR, curses.COLOR_RED, curses.COLOR_WHITE)
    curses.init_pair(STATUS_BAR_COLOR_PAIR, curses.COLOR_GREEN, curses.COLOR_BLACK)
    screen.keypad(1)
    screen.nodelay(1) # nonblocking input
    return screen

def cleanup_curses():
    curses.nocbreak()
    curses.echo()
    curses.endwin()

class ComputationInterruptedException(Exception):
    pass

CurrentFilenames = collections.namedtuple("CurrentFilenames", [ "candidates", "candidate_computation_complete", "git_root_dir", "current_search_dir" ])
class FilenameCollectionThread(threading.Thread):
    def __init__(self, initial_input_str):
        super(FilenameCollectionThread, self).__init__()
        self.daemon = True

        self.ex_traceback = None
        self.search_dir_queue = Queue.Queue()
        self.state_lock = threading.Lock()            # for updating shared state

        self.current_search_dir = None                # only re-run find/git if the search directory changes
        self.candidate_computation_complete = False   # are we done getting all filenames for the current search directory?
        self.candidate_fns_cache = {}                 # cache for candidate filenames given an input_str
        self.candidate_fns = set()                    # current set of candidate functions
        self.git_root_dir = None                      # git root directory

        self.update_input_str(initial_input_str)

    def get_traceback(self):
        """ Returns the traceback for the exception that killed this thread. """
        return self.ex_traceback

    def _interrupted(self):
        return not self.search_dir_queue.empty()

    def run(self):
        try:
            while True:
                if self.search_dir_queue.empty():
                    # don't hold the state lock until we have a queued search_dir available
                    time.sleep(0.005)
                    continue

                with self.state_lock:
                    assert not self.search_dir_queue.empty()
                    # clear out the queue in case we had multiple strings queued up
                    while not self.search_dir_queue.empty():
                        next_search_dir = self.search_dir_queue.get()

                    self.current_search_dir = next_search_dir

                    # indicate that we're not done computing
                    self.candidate_computation_complete = False

                    # reset
                    self.candidate_fns = set()

                try:
                    self._compute_candidates()
                except ComputationInterruptedException:
                    _logger.debug("Candidate computation interrupted!")
                    continue

                with self.state_lock:
                    # this set of candidate filenames is definitely done, so add it to the cache!
                    self.candidate_fns_cache[self.current_search_dir] = self.candidate_fns
                    # we're done, as long as no one has queued us up for more
                    self.candidate_computation_complete = self.search_dir_queue.empty()
        except Exception:
            self.ex_traceback = traceback.format_exc()
            raise

    def _compute_candidates(self):
        """ The actual meat of computing the candidate filenames. """
        try:
            # don't use check_output because it won't swallow stdout
            git_root_dir = subprocess.Popen("cd {} && git rev-parse --show-toplevel".format(self.current_search_dir),
                        shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0].strip() or None
        except subprocess.CalledProcessError:
            git_root_dir = None

        with self.state_lock:
            self.git_root_dir = git_root_dir

        def append_batched_filenames(shell_cmd, absolute_path=False, base_dir=None):
            """ Adds all the files from the output of this command to our candidate_fns in batches. """
            BATCH_SIZE = 100

            _logger.debug("running shell cmd {}".format(shell_cmd))
            proc = subprocess.Popen(shell_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            batch = []
            while True:
                if self._interrupted():
                    raise ComputationInterruptedException("Interrupted while executing: {}".format(shell_cmd))

                nextline = proc.stdout.readline().strip()
                if nextline == "" and proc.poll() != None:
                    break

                fn = os.path.join(base_dir, nextline) if base_dir is not None else nextline
                batch.append(os.path.abspath(fn) if absolute_path else os.path.relpath(fn))

                if len(batch) >= BATCH_SIZE:
                    with self.state_lock:
                        self.candidate_fns.update(batch)
                        batch = []

            if batch:
                with self.state_lock:
                    # clean up the stragglers
                    self.candidate_fns.update(batch)

        if self.git_root_dir is not None:
            # return all files in this git tree
            for shell_cmd in (
                    "git ls-tree --full-tree -r HEAD" if get_config("git_entire_tree") else "git ls-tree -r HEAD",
                    "git ls-files --exclude-standard --others"):
                append_batched_filenames("cd {} && {} | cut -f2".format(self.current_search_dir, shell_cmd), base_dir=self.git_root_dir)
        else:
            # return all files in the current_search_dir
            find_cmd = "find -L {} -type f".format(self.current_search_dir)
            if not get_config("find_hidden_directories"):
                find_cmd = "{} {}".format(find_cmd, "-not -path '*/.*/*'")
            if not get_config("find_hidden_files"):
                find_cmd = "{} {}".format(find_cmd, "-not -name '.*'")
            append_batched_filenames(find_cmd, absolute_path=os.path.isabs(self.current_search_dir))

    def update_input_str(self, input_str):
        """ Determines the appropriate directory and queues a recompute of eligible files matching the input string. """
        new_search_dir = self._guess_root_directory(input_str)

        if new_search_dir != self.current_search_dir:
            with self.state_lock:
                _logger.debug("Switching search directory from {} to {}".format(self.current_search_dir, new_search_dir))
                self.search_dir_queue.put(new_search_dir)

    def get_current_filenames(self):
        """ Get all the relevant filenames given the input string, whether we're done computing them or not. """

        with self.state_lock:
            candidate_fns = copy.copy(self.candidate_fns)
            candidate_computation_complete = self.candidate_computation_complete
            git_root_dir = self.git_root_dir
            current_search_dir = self.current_search_dir

        return CurrentFilenames(candidates=candidate_fns, candidate_computation_complete=candidate_computation_complete, git_root_dir=git_root_dir, current_search_dir=current_search_dir)

    def _guess_root_directory(self, input_str):
        """ Given an input_str, deduce what directory we should search, either by relative path (../../whatever) or by absolute path (/). """
        # TODO return whether the path is absolute (starts with /)
        # If the path is absolute, display as absolute
        # If the path is relative, display as relative
        return "."

EligibleFilenames = collections.namedtuple("EligibleFilenames", [ "eligible", "search_complete" ])
class SearchThread(threading.Thread):
    NewInput = collections.namedtuple("NewInput", [ "input_str", "current_search_dir", "candidate_fns", "candidate_computation_complete" ])
    IncrementalInput = collections.namedtuple("IncrementalInput", [ "new_candidate_fns", "candidate_computation_complete" ])
    MatchTuple = collections.namedtuple("MatchTuple", ["string", "num_nonempty_groups", "total_group_length", "num_dirs_in_path" ])

    def __init__(self, initial_input_str, initial_current_filenames):
        super(SearchThread, self).__init__()
        self.daemon = True

        self.ex_traceback = None

        self.input_queue = Queue.Queue()
        self.state_lock = threading.Lock()

        self.input_str = None
        self.current_search_dir = None
        self.new_candidate_fns = None               # used for incremental search
        self.candidate_fns = None
        self.candidate_computation_complete = None

        self.search_complete = False

        self.eligible_matchtuples = []
        self.eligible_matchtuples_cache = {}        # cache for eligible filenames given an input_str and a current_search_dir

        self.update_input(initial_input_str, initial_current_filenames)

    def get_traceback(self):
        """ Returns the traceback for the exception that killed this thread. """
        return self.ex_traceback

    def _interrupted(self):
        return not self.input_queue.empty()

    def run(self):
        try:
            while True:
                if self.input_queue.empty():
                    # don't hold our state_lock until we have a queued item available
                    time.sleep(0.005)
                    continue

                with self.state_lock:
                    assert not self.input_queue.empty()
                    # clear out the queue in case we had a couple pile up
                    while not self.input_queue.empty():
                        next_input = self.input_queue.get()

                    if isinstance(next_input, self.NewInput):
                        self.input_str = next_input.input_str
                        self.current_search_dir = next_input.current_search_dir
                        self.candidate_fns = next_input.candidate_fns
                        self.new_candidate_fns = None
                        self.candidate_computation_complete = next_input.candidate_computation_complete
                        self.eligible_matchtuples = []

                    elif isinstance(next_input, self.IncrementalInput):
                        self.candidate_fns.update(next_input.new_candidate_fns)
                        self.new_candidate_fns = next_input.new_candidate_fns
                        self.candidate_computation_complete = next_input.candidate_computation_complete

                    else:
                        raise Exception("Unrecognized input!: {}".format(next_input))

                    self.search_complete = False

                try:
                    self._compute_eligible_filenames()
                except ComputationInterruptedException:
                    _logger.debug("Searching interrupted!")
                    continue

                with self.state_lock:
                    self.search_complete = self.input_queue.empty()
        except Exception:
            self.ex_traceback = traceback.format_exc()
            raise

    def update_input(self, input_str, current_filenames):
        """ Queue up computation given a (possibly new) input string and the current state from the FilenameCollectionThread's get_current_filenames() . """
        if any( map(lambda x: x is None, [ input_str, current_filenames.current_search_dir, current_filenames.candidates ]) ):
            # nothing to update!
            return

        if (input_str != self.input_str
                or not self.input_queue.empty()):
            # we've got a new input str or we've already queued up input OR we're already going to trigger a new search, so make sure we've got the latest input before we start
            with self.state_lock:
                _logger.debug("Triggering new search with input string '{}' and {:d} candidate filenames.".format(input_str, len(current_filenames.candidates)))
                self.input_queue.put(self.NewInput(
                    input_str=input_str,
                    current_search_dir=current_filenames.current_search_dir,
                    candidate_fns=current_filenames.candidates,
                    candidate_computation_complete=current_filenames.candidate_computation_complete
                    ))

        elif (input_str == self.input_str
                and current_filenames.current_search_dir == self.current_search_dir
                and self.search_complete
                and not self.candidate_computation_complete
                and self.input_queue.empty()):
            # we've found more files in the same directory with the same query and aren't currently interrupted
            # so... add on an incremental search!
            with self.state_lock:
                new_files = current_filenames.candidates.difference(self.candidate_fns)
                _logger.debug("Adding {:d} more files to current search for input_str '{}' in directory {}".format(len(new_files), input_str, current_filenames.current_search_dir))
                self.input_queue.put(self.IncrementalInput(
                    new_candidate_fns=new_files,
                    candidate_computation_complete=current_filenames.candidate_computation_complete
                    ))

    def get_eligible_filenames(self):
        """ Retrieve a current snapshot of what we think are the current eligible filenames. """
        with self.state_lock:
            eligible_fns = [ match.string for match in self.eligible_matchtuples ]
            search_complete = self.search_complete

        return EligibleFilenames(eligible=eligible_fns, search_complete=search_complete)

    @staticmethod
    def _matchtuple_cmp(match_one, match_two):
        # prefer the fewest number of empty groups (fewest gaps in fuzzy matching)

        # (more nonempty groups -> show up later in the list)
        diff = match_one.num_nonempty_groups - match_two.num_nonempty_groups
        if diff != 0:
            return diff

        # then the shortest total length of all groups (prefer "MyGreatFile.txt" over "My Documents/stuff/File.txt")
        diff = match_one.total_group_length - match_two.total_group_length
        if diff != 0:
            return diff

        # prefer files in this directory before files elsewhere
        diff = match_one.num_dirs_in_path - match_two.num_dirs_in_path
        if diff != 0:
            return diff

        # and finally in lexicographical order
        return cmp(match_one.string, match_two.string)

    def _compute_eligible_filenames(self):
        """ Return a sorted ordering of the filenames based on this input string.

        All filenames that match the input_string are included, and we prefer those
        that match on word boundaries.
        """
        lowered = self.input_str.lower()
        if len(lowered) >= 100:
            # more helpful explanation for the exception we'll get with regex.compile()
            raise Exception("python2.7 supports only 100 named groups, so this isn't going to work.  What're you doing searching for a string with >= 100 characters?")

        def make_cache_key(search_dir, normalized_input):
            return (os.path.abspath(search_dir), normalized_input)

        cache_key = make_cache_key(self.current_search_dir, lowered)

        def is_incremental_search():
            return self.new_candidate_fns is not None

        def get_num_dirs_in_path(fn):
            count = 0
            while fn:
                head, _ = os.path.split(fn)
                if head:
                    count += 1
                else:
                    break
                fn = head
            return count

        def perform_search():
            if cache_key in self.eligible_matchtuples_cache:
                _logger.debug("Found cached eligible_matchtuples key: {}".format(cache_key))
                return self.eligible_matchtuples_cache[cache_key]

            if is_incremental_search():
                initial_filenames = self.new_candidate_fns
            else:
                # if this query is at least two characters long and the prefix minus this last letter has already been computed, start with those eligible filenames
                # no need to prune down the whole list if we've already limited the search space
                prev_cache_key = make_cache_key(self.current_search_dir, lowered[:-1])
                if len(lowered) >= 2 and prev_cache_key in self.eligible_matchtuples_cache:
                    initial_filenames = [ match.string for match in self.eligible_matchtuples_cache[prev_cache_key] ]
                else:
                    initial_filenames = self.candidate_fns

            _logger.debug("Searching {:d} files for '{}'{}".format(len(initial_filenames), lowered, " (incremental!)" if is_incremental_search() else ""))

            if lowered == "":
                _logger.debug("Returning all candidates for empty input str.")
                return [ self.MatchTuple(string=fn, num_nonempty_groups=0, total_group_length=0, num_dirs_in_path=get_num_dirs_in_path(fn)) for fn in initial_filenames ]


            # fuzzy matching: for input string abc, find a*b*c substrings (consuming as few characters as possible in between)
            # guard against user input that may be construed as a regex
            regex_str = "(.*?)".join( re.escape(ch) for ch in lowered )
            filter_regex = re.compile(regex_str, re.IGNORECASE | re.DOTALL)
            # prepend (?:.*) to push off the matching as much as possible (more expensive but more accurate)
            ranking_regex = re.compile("(?:.*)" + regex_str, re.IGNORECASE | re.DOTALL)

            def get_match_tuples_it():
                def nonempty_groups(match):
                    return filter(lambda x: x, match.groups())

                for fn in initial_filenames:
                    if self._interrupted():
                        raise ComputationInterruptedException("Searching interrupted!")

                    filter_match = filter_regex.search(fn)
                    if filter_match is not None:
                        ranking_match = ranking_regex.search(fn)
                        negs = nonempty_groups(ranking_match)
                        yield self.MatchTuple(
                                string=fn,
                                num_nonempty_groups = len(negs),
                                total_group_length=len("".join(negs)),
                                num_dirs_in_path=get_num_dirs_in_path(fn)
                                )
            return list(get_match_tuples_it())

        if is_incremental_search():
            eligible_matchtuples = self.eligible_matchtuples + perform_search()
        else:
            eligible_matchtuples = perform_search()

        # need to re-sort if incremental!
        eligible_matchtuples.sort(cmp=self._matchtuple_cmp)
        _logger.debug("Found {:d} eligible matchtuples.".format(len(eligible_matchtuples)))

        with self.state_lock:
            self.eligible_matchtuples = eligible_matchtuples

            if self.candidate_computation_complete: # if we're dealing with a complete set of candidates, cache the results
                self.eligible_matchtuples_cache[cache_key] = eligible_matchtuples

class SearchStatus(object):
    SEARCH_STATUS_CHARS = ("|", "\\", "-", "/")

    def __init__(self):
        super(SearchStatus, self).__init__()
        self.curr_idx = None
        self.reset_status()

    def reset_status(self):
        self.curr_idx = 0

    def get_next_status_char(self):
        self.curr_idx = (self.curr_idx + 1) % len(self.SEARCH_STATUS_CHARS)
        return self.SEARCH_STATUS_CHARS[self.curr_idx]

def select_filename(screen, fn_collection_thread, input_str):
    highlighted_pos = 0
    key_name = None

    search_thread = SearchThread(input_str, fn_collection_thread.get_current_filenames())
    search_thread.start()

    search_status = SearchStatus()

    def get_display_uuid(input_str, curr_fns, eligible_fns):
        """ Returns a unique id to represent what we're currently displaying on the screen.  Useful for us to block if we're not showing anything new. """
        return hash("".join(map(str,[
            input_str,
            curr_fns.candidate_computation_complete, curr_fns.current_search_dir, len(curr_fns.candidates),
            eligible_fns.search_complete, len(eligible_fns.eligible) ])))

    def ensure_threads_alive(*threads):
        for th in threads:
            if not th.is_alive():
                raise Exception("{} died with traceback:\n{}".format(th, th.get_traceback()))

    prev_display_uuid = None
    while True:
        ensure_threads_alive(fn_collection_thread, search_thread)

        screen.clear()

        fn_collection_thread.update_input_str(input_str)
        curr_fns = fn_collection_thread.get_current_filenames()

        search_thread.update_input(input_str, curr_fns)
        eligible_fns = search_thread.get_eligible_filenames()

        if not eligible_fns.search_complete:
            highlighted_pos = 0

        highlighted_fn = eligible_fns.eligible[highlighted_pos] if eligible_fns.eligible else None

        STATUS_BAR_Y = 0      # status bar first!
        INPUT_Y = 2           # where the input line should go
        FN_OFFSET = 3         # first Y coordinate of a filename
        max_height, max_width = screen.getmaxyx()
        max_files_to_show = min(len(eligible_fns.eligible), max_height - FN_OFFSET)

        def add_line(y, x, line, attr, fill_line=False):
            s = line[-(max_width - 1):]
            if fill_line:
                s = s.ljust(max_width - 1, " ")
            try:
                screen.addstr(y, x, s, attr)
            except Exception:
                _logger.debug("Couldn't add string to screen: {}".format(s))

        if (not eligible_fns.search_complete or not curr_fns.candidate_computation_complete):
            search_status_prefix = "{} ".format(search_status.get_next_status_char())
        else:
            search_status_prefix = "  "
            search_status.reset_status()

        # add status bar
        status_text = "{}{:d} of {:d} candidate filenames{}".format(
                search_status_prefix,
                len(eligible_fns.eligible),
                len(curr_fns.candidates),
                " (git: {})".format(curr_fns.git_root_dir) if curr_fns.git_root_dir is not None else "")
        add_line(STATUS_BAR_Y, 0, status_text, curses.color_pair(STATUS_BAR_COLOR_PAIR), fill_line=True)

        # input line
        add_line(INPUT_Y, 0, input_str, curses.A_UNDERLINE, fill_line=True)

        for pos, fn in enumerate(eligible_fns.eligible[:max_files_to_show]):
            attr = curses.color_pair(HIGHLIGHT_COLOR_PAIR) if pos == highlighted_pos else curses.A_NORMAL
            add_line(FN_OFFSET + pos, 0, fn, attr)

        screen.refresh()

        # put the cursor at the end of the string
        input_x = min(len(input_str), max_width - 1)

        # getch is nonblocking; try in 20ms increments for up to 120ms before redrawing screen (60s if we know the screen won't change without input)
        new_display_uuid = get_display_uuid(input_str, curr_fns, eligible_fns)
        getch_time = 60 if new_display_uuid == prev_display_uuid and curr_fns.candidate_computation_complete and eligible_fns.search_complete else 0.120
        prev_display_uuid = new_display_uuid

        start_getch = time.time()
        raw_key = -1
        while (time.time() - start_getch) < getch_time:
            raw_key = screen.getch(INPUT_Y, input_x)
            if raw_key != -1: break
            time.sleep(0.020)

        if raw_key == -1:
            continue

        key_name = curses.keyname(raw_key)

        if key_name == NEWLINE:
            # open the file in $EDITOR
            open_file(highlighted_fn)
            return
        elif key_name == TAB:
            # dump the character back to the prompt
            dump_to_prompt(highlighted_fn)
            return

        elif key_name == "KEY_DOWN":
            highlighted_pos = min(highlighted_pos + 1, max_files_to_show - 1)
        elif key_name == "KEY_UP":
            highlighted_pos = max(highlighted_pos - 1, 0)
        elif key_name == "KEY_NPAGE": # page down
            highlighted_pos = max_files_to_show - 1
        elif key_name == "KEY_PPAGE": # page up
            highlighted_pos = 0
        else:
            if key_name in ["KEY_BACKSPACE", "^?"]:   # delete single character
                input_str = input_str[:-1]
            elif key_name == "^W":                    # delete whole line
                input_str = ""
            elif (key_name.startswith("KEY_")
                    or key_name.startswith("^")):     # just ignore it
                continue
            else:                                     # add character (doesn't special key checking)
                input_str += key_name

            # at this point, input_str has changed, so reset the highlighted_pos
            highlighted_pos = 0

    # something's definitely not right
    raise Exception("Should be unreachable.  Exit this function within the loop!")

def _shellquote(s):
    """ Cleans up a filename for the shell (from http://stackoverflow.com/a/35857) """
    return "'" + s.replace("'", "'\\''") + "'"

OUTPUT_SH = "/tmp/completeme.sh"
def dump_to_prompt(fn):
    if fn:
        with open(OUTPUT_SH, 'wb') as f:
            new_token = _shellquote(_shellquote(fn) + " ") # double shell-quote because we're setting an environment variable with the quoted string
            print >> f, "READLINE_LINE='{}'{}".format(os.environ.get("READLINE_LINE", ""), new_token),
            print >> f, "READLINE_POINT='{}'".format(int(os.environ.get("READLINE_POINT", 0)) + len(new_token))

def open_file(fn):
    if fn:
        editor_cmd = os.getenv("EDITOR")
        if editor_cmd is None:
            raise Exception("Environment variable $EDITOR is missing!")

        with open(OUTPUT_SH, "wb") as f:
            cmd = "{} {}".format(editor_cmd, _shellquote(fn))
            print >> f, cmd
            print >> f, "history -s \"{}\"".format(cmd)

def get_initial_input_str():
    """ Returns the string that should seed our search.

    TODO parse the existing commandline (READLINE_LINE, READLINE_POINT).
    If we're in the middle of typing something, seed with that argument.
    """
    return ""

def main():
    initial_input_str = get_initial_input_str()
    fn_collection_thread = FilenameCollectionThread(initial_input_str)
    fn_collection_thread.start()
    try:
        screen = init_screen()
        select_filename(screen, fn_collection_thread, initial_input_str)
    except KeyboardInterrupt:
        pass
    finally:
        cleanup_curses()

if __name__ == "__main__":
    if os.environ.get("RUN_PROFILER"):
        import cProfile
        import pstats
        import tempfile
        _, profile_fn = tempfile.mkstemp()
        cProfile.run("main()", profile_fn)
        pstats.Stats(profile_fn).sort_stats("cumulative").print_stats()
    else:
        main()
