from contextlib import contextmanager
import errno
import os
import shutil
import subprocess
import tempfile


class GitExeException(Exception):
    """
    Thrown when the external git exe doesn't return a 0.
    """
    pass


class Repo(object):
    """
    Interface to a git repo.

    Generally you should create one with `fleeting_repo`, which
    manages cleanup.
    """

    def __init__(self, repo_root, git_exe=None):
        """
        - `repo_root`: the (presumably temporary) dir in which to init
          and manage a git repo, e.g. '/tmp/Fkjwpa'

        - `git_exe`: the git exe to use.  Should be a list, suitable
          for passing to subprocess.call.  If None, defaults to
          ["/usr/bin/env", "git"], which should work fine on most
          systems.

        Calls "git init" to create a new repo, and therefore may raise
        a GitExeException.
        """
        self.repo_root = _real_abs(repo_root)
        self.git_exe = git_exe
        if self.git_exe is None:
            self.git_exe = ["/usr/bin/env", "git"]
        self.do_git(["init"])

    def commit(self, fnames_with_contents, commit_msg=None, author=None):
        """
        Apply the sequential changes described in fnames_with_contents
        in the repo directory, and then commit the results.

        Like all methods in this class that invoke git, this can raise
        a GitExeException.

        - `fnames_with_contents`: a list of tuples of the
          form

          [(str(fname), str(contents)|None), ...]

          E.g.

          [('test.txt', 'this is a test\\n'),
           ('testdir_one/to_be_removed.txt', None)]

          Each fname should be relative to the git repo root.  If
          fname contains directory paths, they will be created under
          the repo root.  If the contents is not None, the string will
          be written to the file indicated by fname.  If contents is
          None, the file will be git rm'ed.

        - `commmit_msg`: a utf-8 str() being the commit message to
          pass to the commit.

          If None, the commit message will be:

          "Test commit."

        - `author`: a utf-8 str() being the author for the commit,
          formatted according to git requirements as:

          "Author Name <author@email>"

          If author is None, the author will be:

          "Test Author <test@example.com>"
        """
        self._write_add_rm(fnames_with_contents)

        commit_cmd = ["commit", "--author"]

        if author is None:
            author = "Test Author <test@example.com>"
        commit_cmd.append(author)

        if commit_msg is None:
            commit_msg = "Test commit."

        # Use a temp file to hold the commit message, in case it's
        # long or weird and wouldn't do well on the command line.
        with _temp_fname() as commit_fname:
            with open(commit_fname, 'wb') as fil:
                fil.write(commit_msg)

            commit_cmd.append("-F")
            commit_cmd.append(commit_fname)

            self.do_git(commit_cmd)

    def get_path(self, fname):
        """
        Return a full path to fname under the repository root.

        - `fname`: a file or directory name, relative to the repo
          root.

        >>> repo = Repo('/some/dir')
        >>> repo.get_path('testing/test.txt')
        '/some/dir/testing/test.txt'
        """
        return os.path.join(self.repo_root, fname)

    def _write_add_rm(self, fnames_with_contents):
        """
        Write contents for each fname in fname with contents, then git
        add it.

        For each fname with None contents, git rm it.
        """
        for (fname, contents) in fnames_with_contents:
            fpath = os.path.join(self.repo_root, fname)
            _ensure_dir_for_fpath(fpath)
            if contents is None:
                self.do_git(["rm", fname])
            else:
                with open(fpath, 'wb') as fil:
                    fil.write(contents)
                self.do_git(["add", fname])

    def do_git(self, cmd):
        """
        Run a git cmd in the repo root and don't worry about what it
        writes to stdout / stderr.

        If you need access to stdout / stderr, take a look at
        `yield_git`.

        Raises a GitExeException if git returns non-0.

        - `cmd`: a list of strings, suitable for passing to
          subprocess.call, e.g. ["add", "some_file.txt"]
        """
        with self.yield_git(cmd):
            pass

    def yield_git(self, cmd):
        """
        Run git_exe in the repo root, passing cmd to it.

        Raises a GitExeException if git returns non-0.

        - `cmd`: a list of strings, suitable for passing to
          subprocess.call, e.g. ["add", "some_file.txt"]

        Yields a tuple of open (file(), file()), being the stdout and
        stderr written to by the git process, to support use like:

        >>> repo = Repo('/some/dir')
        >>> with repo.yield_git(["log", "--oneline"]) as git_output:
        ...     git_out, git_err = git_output
        ...     output = git_out.read()

        Note that means this is *not* what you want to do:

        >>> repo.yield_git(["log", "--oneline"])

        as this will just yield the generator and run nothing.

        Use do_git for that.
        """
        # this is ugly, creating a local function and calling it, but
        # otherwise @contextmanager ruins the args in interactive help
        @contextmanager
        def _yield_git():
            whole_cmd = self.git_exe + cmd

            with _temp_dir() as tmp_dir:
                # don't bother using temp files for these, just a tmp dir,
                # as it will be recursively cleaned up.
                stdout_fname = os.path.join(tmp_dir, 'git_stdout')
                stderr_fname = os.path.join(tmp_dir, 'git_stderr')
                with open(stdout_fname, 'wb') as o_f:
                    with open(stderr_fname, 'wb') as e_f:
                        returncode = subprocess.call(whole_cmd,
                                                     stdout=o_f,
                                                     stderr=e_f,
                                                     cwd=self.repo_root)
                        if returncode != 0:
                            raise GitExeException(_fmt_err(whole_cmd,
                                                           returncode,
                                                           stderr_fname,
                                                           stdout_fname))

                # if we get here, the git command returned 0.  We re-open
                # and yield the stdout and stderr in case the caller wants
                # them.  After the yield returns, the entire temp
                # directory will be cleaned up.
                with open(stdout_fname, 'rb') as git_out_f:
                    with open(stderr_fname, 'rb') as git_err_f:
                        yield (git_out_f, git_err_f)

        return _yield_git()


def fleeting_repo(git_exe=None):
    """
    Create a temp directory and yield a Repo built from it.

    The temp dir will be cleaned up afterwards.

    >>> with fleeting_repo() as repo:
    ...     repo.do_git(["some", "git", "cmd"])

    - `git_exe`: the git exe to use.  Should be a list, suitable for
      passing to subprocess.call.  If None, defaults to
      ["/usr/bin/env", "git"], which should work fine on most systems.
    """
    # this is ugly, creating a local function and returning it, but
    # otherwise @contextmanager screws up the param names in the
    # interactive help.
    @contextmanager
    def _fleeting_repo():
        with _temp_dir() as temp_dir:
            yield Repo(temp_dir, git_exe=git_exe)
    return _fleeting_repo()


@contextmanager
def _temp_fname():
    """
    Yield a temp file name, delete the file afterwards.
    """
    ntf = tempfile.NamedTemporaryFile(delete=False)
    fname = ntf.name
    ntf.close()
    try:
        yield fname
    finally:
        try:
            os.unlink(fname)
        except OSError:
            # this means it was already unlinked
            pass


@contextmanager
def _temp_dir():
    """
    Make a temp dir and yield it, removing it afterwards.
    """
    temp_dir = tempfile.mkdtemp()
    try:
        yield temp_dir
    finally:
        shutil.rmtree(temp_dir)


def _ensure_dir_for_fpath(fpath):
    """
    Ensure that the directory in which fpath will reside exists,
    recursively creating it otherwise.

    Adapted from:

    http://stackoverflow.com/questions/600268/mkdir-p-functionality-in-python
    """
    dir_name = os.path.dirname(fpath)
    try:
        os.makedirs(dir_name)
    except OSError, exc:
        if exc.errno != errno.EEXIST or not os.path.isdir(dir_name):
            raise


def _fmt_cmd_for_err(cmd):
    """
    Join a git cmd, quoting individual segments first so that it's
    relatively easy to see if there were whitespace issues or not.
    """
    return ' '.join(['"%s"' % seg for seg in cmd])


def _fmt_err(git_cmd, returncode, stderr_fname, stdout_fname):
    """
    Format an error string for a failed git command, which includes
    the harvested stdout and stderr of the process.
    """
    git_cmd_s = _fmt_cmd_for_err(git_cmd)
    err_msg = '\n'.join([_read_fname(stderr_fname),
                         _read_fname(stdout_fname)])
    return ("Git command %s returned %d with err log %s" %
            (git_cmd_s,
             returncode,
             err_msg))


def _read_fname(fname):
    """
    Open fname, read the contents, return them.
    """
    with open(fname, 'rb') as fil:
        return fil.read()


def _real_abs(path):
    """
    Return a real, absolute path.
    """
    return os.path.abspath(os.path.realpath(path))
