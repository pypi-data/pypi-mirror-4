import os
import shutil
import unittest

from .. import fleeting_repo, Repo, GitExeException

# git exe to use, can be overriden with env setting
# IMPERMAGIT_TEST_GIT_EXE.
git_exe = None


class TestFleetingRepo(unittest.TestCase):

    def test_fleeting_creates_git_repo(self):
        with fleeting_repo(git_exe=git_exe) as repo:
            self.assertTrue(os.path.isdir(repo.repo_root))
            self.assertTrue(os.path.isdir(os.path.join(repo.repo_root,
                                                       '.git')))

    def test_fleeting_rms_git_repo(self):
        repo_root = None
        with fleeting_repo(git_exe=git_exe) as repo:
            repo_root = repo.repo_root
            self.assertTrue(os.path.isdir(repo_root))
        self.assertFalse(os.path.isdir(repo_root))


class RepoTestCase(unittest.TestCase):

    def setUp(self):
        self.test_dir_name = "impermagit_path_test_repo"
        self.test_repo_dir_name = "real_repo"
        self.linked_repo_dir_name = "linked_repo"

        if os.path.isdir(self.test_dir_name):
            shutil.rmtree(self.test_dir_name)
        os.mkdir(self.test_dir_name)
        os.mkdir(self._rel_dir(self.test_repo_dir_name))
        save_dir = os.getcwd()
        os.chdir(self.test_dir_name)
        os.symlink(self.test_repo_dir_name, self.linked_repo_dir_name)
        os.chdir(save_dir)

        test_repo_dir = self._rel_dir(self.test_repo_dir_name)
        self.test_repo_dir = os.path.abspath(os.path.realpath(test_repo_dir))

    def tearDown(self):
        if os.path.isdir(self.test_dir_name):
            shutil.rmtree(self.test_dir_name)

    def _rel_dir(self, dir_name):
        return os.path.join(self.test_dir_name, dir_name)


class TestRepoPaths(RepoTestCase):

    def test_repo_root_uses_abs_path(self):
        rel_dir = self._rel_dir(self.test_repo_dir_name)
        self.assertNotEqual(rel_dir, os.path.abspath(rel_dir))
        repo = Repo(rel_dir, git_exe=git_exe)
        self.assertEqual(os.path.abspath(rel_dir), repo.repo_root)

    def test_repo_root_uses_real_path(self):
        ln_dir = os.path.abspath(self._rel_dir(self.linked_repo_dir_name))
        real_dir = os.path.abspath(self._rel_dir(self.test_repo_dir_name))
        self.assertNotEqual(ln_dir, os.path.realpath(real_dir))
        repo = Repo(ln_dir, git_exe=git_exe)
        self.assertEqual(real_dir, repo.repo_root)

    def test_repo_root_uses_real_abs_path(self):
        rel_ln_dir = self._rel_dir(self.linked_repo_dir_name)
        real_abs_dir = os.path.realpath(os.path.abspath(rel_ln_dir))
        self.assertNotEqual(rel_ln_dir, real_abs_dir)
        repo = Repo(rel_ln_dir, git_exe=git_exe)
        self.assertEqual(real_abs_dir, repo.repo_root)

    def test_get_path_returns_full_path(self):
        repo = Repo(self.test_repo_dir, git_exe=git_exe)
        self.assertEquals(os.path.join(repo.repo_root,
                                       'test.txt'),
                          repo.get_path('test.txt'))


class TestRepoBarfs(RepoTestCase):

    def test_repo_barfs_on_bad_git(self):
        self.assertRaises(OSError,
                          Repo,
                          self.test_repo_dir,
                          ["not_a_git_exe"])

    def test_repo_barfs_on_bad_dir(self):
        self.assertRaises(OSError,
                          Repo,
                          "not_a_dir",
                          git_exe)

    def test_repo_barfs_on_bad_cmd(self):
        self.repo = Repo(self.test_repo_dir, git_exe=git_exe)
        self.assertRaises(GitExeException,
                          self.repo.do_git,
                          ["not_a_git_cmd"])

    def test_git_exe_exception_contains_command_info(self):
        self.repo = Repo(self.test_repo_dir, git_exe=git_exe)
        ex = None

        try:
            self.repo.do_git(["not_a_git_cmd"])
        except GitExeException, e:
            ex = e

        self.assertTrue("not_a_git_cmd" in str(ex))


class CommitTestCase(RepoTestCase):

    def setUp(self):
        super(CommitTestCase, self).setUp()
        self.repo = Repo(self.test_repo_dir, git_exe=git_exe)
        self.test_file_name = 'test.txt'
        self.test_file_path = os.path.join(self.test_repo_dir,
                                           self.test_file_name)

        # make sure that one of the files is in a subdir that doesn't
        # yet exist
        self.assertFalse(os.path.isdir(os.path.join(self.test_repo_dir,
                                                    'test_subdir')))
        self.test_file_name_two = 'test_subdir/test_two.txt'
        self.test_file_path_two = os.path.join(self.test_repo_dir,
                                               self.test_file_name_two)

        # wouldn't that be just like me?
        self.assertNotEqual(self.test_file_path,
                            self.test_file_path_two)

        self.assertFalse(os.path.exists(self.test_file_path))
        self.assertFalse(os.path.exists(self.test_file_path_two))

        self.test_contents = "this is a test\n"
        self.test_contents_two = "this is a test two\n"

        self.assertNotEqual(self.test_contents, self.test_contents_two)

        self.test_author = "Unit Test <unit@example.com>"
        self.test_commit_msg = "Unit test commit message"

        self.repo.commit([(self.test_file_name, self.test_contents),
                          (self.test_file_name_two, self.test_contents_two)],
                         author=self.test_author,
                         commit_msg=self.test_commit_msg)

        self.assertTrue(os.path.isdir(os.path.join(self.test_repo_dir,
                                                   'test_subdir')))

    def test_commit_writes_files(self):
        self.assertTrue(os.path.exists(self.test_file_path))
        self.assertTrue(os.path.exists(self.test_file_path_two))

        with open(self.test_file_path, 'rb') as fil:
            self.assertEquals(self.test_contents, fil.read())
        with open(self.test_file_path_two, 'rb') as fil:
            self.assertEquals(self.test_contents_two, fil.read())

    def test_commit_commits_files(self):
        with self.repo.yield_git(["ls-tree",
                                  "--name-only",
                                  "-r",
                                  "HEAD"]) as (out, err):
            ls = out.read()
            self.assertTrue(self.test_file_name in ls)
            self.assertTrue(self.test_file_name_two in ls)

        with self.repo.yield_git(["status"]) as (out, err):
            self.assertTrue("working directory clean" in out.read())

    def test_commit_makes_one_commit_only(self):
        with self.repo.yield_git(["log", "--oneline"]) as (out, err):
            # initial commit, then the test commit
            self.assertEquals(2, len(out.read().split("\n")))

    def test_commit_passes_author(self):
        with self.repo.yield_git(["log"]) as (out, err):
            self.assertTrue(("Author: %s" % self.test_author) in out.read())

    def test_commit_passes_msg(self):
        with self.repo.yield_git(["log"]) as (out, err):
            self.assertTrue(self.test_commit_msg in out.read())

    def test_commit_can_change_existing_files(self):
        new_test_contents = "new test contents\n"
        with open(self.test_file_path, 'rb') as fil:
            self.assertNotEqual(new_test_contents, fil.read())
        with self.repo.yield_git(["log", "--oneline"]) as (out, err):
            self.assertEquals(2, len(out.read().split("\n")))
        self.repo.commit([(self.test_file_name, new_test_contents)])
        with open(self.test_file_path, 'rb') as fil:
            self.assertEquals(new_test_contents, fil.read())
        with self.repo.yield_git(["log", "--oneline"]) as (out, err):
            self.assertEquals(3, len(out.read().split("\n")))

    def test_commit_can_rm_files(self):
        self.assertTrue(os.path.exists(self.test_file_path))
        self.assertTrue(os.path.exists(self.test_file_path_two))
        with self.repo.yield_git(["log", "--oneline"]) as (out, err):
            self.assertEquals(2, len(out.read().split("\n")))
        self.repo.commit([(self.test_file_name, None),
                          (self.test_file_name_two, None)])
        with self.repo.yield_git(["log", "--oneline"]) as (out, err):
            self.assertEquals(3, len(out.read().split("\n")))
        self.assertFalse(os.path.exists(self.test_file_path))
        self.assertFalse(os.path.exists(self.test_file_path_two))


class TestGitCmds(CommitTestCase):

    def test_do_git_runs_a_git_command(self):
        self.assertTrue(os.path.exists(self.test_file_path))
        self.repo.do_git(["rm", self.test_file_name])
        self.assertFalse(os.path.exists(self.test_file_path))

    def test_yield_git_runs_git_cmd_and_returns_out_and_err(self):
        with self.repo.yield_git(["log"]) as (out, err):
            self.assertTrue(isinstance(err, file))
            self.assertTrue(isinstance(out, file))
            self.assertTrue(self.test_commit_msg in out.read())
            self.assertEqual("", err.read())


if __name__ == '__main__':
    # in case someone is running tests on a machine where git is
    # installed strangely, let them set the path
    if 'IMPERMAGIT_TEST_GIT_EXE' in os.environ:
        git_exe = os.environ['IMPERMAGIT_TEST_GIT_EXE']
    unittest.main()
