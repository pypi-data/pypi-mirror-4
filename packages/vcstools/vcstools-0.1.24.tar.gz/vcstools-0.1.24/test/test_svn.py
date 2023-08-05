#!/usr/bin/env python
# Software License Agreement (BSD License)
#
# Copyright (c) 2009, Willow Garage, Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following
#    disclaimer in the documentation and/or other materials provided
#    with the distribution.
#  * Neither the name of Willow Garage, Inc. nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

from __future__ import unicode_literals

import os
import io
import unittest
import subprocess
import tempfile
import shutil
import re
from vcstools.svn import SvnClient


class SvnClientTestSetups(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.root_directory = tempfile.mkdtemp()
        self.directories = dict(setUp=self.root_directory)
        self.remote_path = os.path.join(self.root_directory, "remote")
        init_path = os.path.join(self.root_directory, "init")

        # create a "remote" repo
        subprocess.check_call("svnadmin create %s" % self.remote_path, shell=True, cwd=self.root_directory)
        self.local_url = "file://localhost" + self.remote_path

        # create an "init" repo to populate remote repo
        subprocess.check_call("svn checkout %s %s" % (self.local_url, init_path), shell=True, cwd=self.root_directory)

        subprocess.check_call("touch fixed.txt", shell=True, cwd=init_path)
        subprocess.check_call("svn add fixed.txt", shell=True, cwd=init_path)
        subprocess.check_call("svn commit -m initial", shell=True, cwd=init_path)

        self.local_version_init = "-r1"

        # files to be modified in "local" repo
        subprocess.check_call("touch modified.txt", shell=True, cwd=init_path)
        subprocess.check_call("touch modified-fs.txt", shell=True, cwd=init_path)
        subprocess.check_call("svn add modified.txt modified-fs.txt", shell=True, cwd=init_path)
        subprocess.check_call("svn commit -m initial", shell=True, cwd=init_path)

        self.local_version_second = "-r2"

        subprocess.check_call("touch deleted.txt", shell=True, cwd=init_path)
        subprocess.check_call("touch deleted-fs.txt", shell=True, cwd=init_path)
        subprocess.check_call("svn add deleted.txt deleted-fs.txt", shell=True, cwd=init_path)
        subprocess.check_call("svn commit -m modified", shell=True, cwd=init_path)

        self.local_path = os.path.join(self.root_directory, "local")

    @classmethod
    def tearDownClass(self):
        for d in self.directories:
            shutil.rmtree(self.directories[d])

    def tearDown(self):
        if os.path.exists(self.local_path):
            shutil.rmtree(self.local_path)


class SvnClientTest(SvnClientTestSetups):

    def test_get_url_by_reading(self):
        client = SvnClient(self.local_path)
        client.checkout(self.local_url)
        self.assertTrue(client.path_exists())
        self.assertTrue(client.detect_presence())
        self.assertEqual(self.local_url, client.get_url())
        #self.assertEqual(client.get_version(), self.local_version)
        self.assertEqual(client.get_version("PREV"), "-r2")
        self.assertEqual(client.get_version("2"), "-r2")
        self.assertEqual(client.get_version("-r2"), "-r2")
        # test invalid cient and repo without url
        client = SvnClient(os.path.join(self.remote_path, 'foo'))
        self.assertEqual(None, client.get_url())

    def test_get_type_name(self):
        local_path = "/tmp/dummy"
        client = SvnClient(local_path)
        self.assertEqual(client.get_vcs_type_name(), 'svn')

    def test_get_url_nonexistant(self):
        local_path = "/tmp/dummy"
        client = SvnClient(local_path)
        self.assertEqual(client.get_url(), None)

    def test_checkout(self):
        url = self.local_url
        client = SvnClient(self.local_path)
        self.assertFalse(client.path_exists())
        self.assertFalse(client.detect_presence())
        self.assertFalse(client.detect_presence())
        self.assertTrue(client.checkout(url))
        self.assertTrue(client.path_exists())
        self.assertTrue(client.detect_presence())
        self.assertEqual(client.get_path(), self.local_path)
        self.assertEqual(client.get_url(), url)

    def test_checkout_emptyversion(self):
        url = self.local_url
        client = SvnClient(self.local_path)
        self.assertFalse(client.path_exists())
        self.assertFalse(client.detect_presence())
        self.assertFalse(client.detect_presence())
        self.assertTrue(client.checkout(url, version=''))
        self.assertTrue(client.path_exists())
        self.assertTrue(client.detect_presence())
        self.assertEqual(client.get_path(), self.local_path)
        self.assertEqual(client.get_url(), url)
        self.assertTrue(client.update(None))
        self.assertTrue(client.update(""))

    def test_checkout_specific_version_and_update_short(self):
        "using just a number as version"
        url = self.local_url
        version = "3"
        client = SvnClient(self.local_path)
        self.assertFalse(client.path_exists())
        self.assertFalse(client.detect_presence())
        self.assertTrue(client.checkout(url, version))
        self.assertTrue(client.path_exists())
        self.assertTrue(client.detect_presence())
        self.assertEqual(client.get_version(), "-r3")
        new_version = '2'
        self.assertTrue(client.update(new_version))
        self.assertEqual(client.get_version(), "-r2")

    def testDiffClean(self):
        client = SvnClient(self.remote_path)
        self.assertEquals('', client.get_diff())

    def testStatusClean(self):
        client = SvnClient(self.remote_path)
        self.assertEquals('', client.get_status())


class SvnDiffStatClientTest(SvnClientTestSetups):

    @classmethod
    def setUpClass(self):
        SvnClientTestSetups.setUpClass()
        client = SvnClient(self.local_path)
        client.checkout(self.local_url)
        # after setting up "local" repo, change files and make some changes
        subprocess.check_call("rm deleted-fs.txt", shell=True, cwd=self.local_path)
        subprocess.check_call("svn rm deleted.txt", shell=True, cwd=self.local_path)
        f = io.open(os.path.join(self.local_path, "modified.txt"), 'a')
        f.write('0123456789abcdef')
        f.close()
        f = io.open(os.path.join(self.local_path, "modified-fs.txt"), 'a')
        f.write('0123456789abcdef')
        f.close()
        f = io.open(os.path.join(self.local_path, "added-fs.txt"), 'w')
        f.write('0123456789abcdef')
        f.close()
        f = io.open(os.path.join(self.local_path, "added.txt"), 'w')
        f.write('0123456789abcdef')
        f.close()
        subprocess.check_call("svn add added.txt", shell=True, cwd=self.local_path)

    def tearDown(self):
        pass

    def assertEqualDiffs(self, expected, actual):
        "True if actual is similar enough to expected, minus svn properties"
        filtered = []
        # A block starts with \nIndex, and the actual diff goes up to the first line starting with [a-zA-Z], e.g. "Properties changed:"
        for block in actual.split("\nIndex: "):
            if filtered != []:
                # restore "Index: " removed by split()
                block = "Index: " + block
            newblock = []
            for line in block.splitlines():
                if re.search("[=+-\\@ ].*", line) == None:
                    break
                else:
                    newblock.append(line)
            filtered.extend(newblock)
        filtered = "\n".join(filtered)
        self.assertEquals(expected, filtered, "Assert failed, expected something like '" + expected + "'\n but got:\n'" + filtered + "'\n, original:\n''" + actual)

    def test_diff(self):
        client = SvnClient(self.local_path)
        self.assertTrue(client.path_exists())
        self.assertTrue(client.detect_presence())

        self.assertEqualDiffs('Index: added.txt\n===================================================================\n--- added.txt\t(revision 0)\n+++ added.txt\t(revision 0)\n@@ -0,0 +1 @@\n+0123456789abcdef\n\\ No newline at end of file\nIndex: modified-fs.txt\n===================================================================\n--- modified-fs.txt\t(revision 3)\n+++ modified-fs.txt\t(working copy)\n@@ -0,0 +1 @@\n+0123456789abcdef\n\\ No newline at end of file\nIndex: modified.txt\n===================================================================\n--- modified.txt\t(revision 3)\n+++ modified.txt\t(working copy)\n@@ -0,0 +1 @@\n+0123456789abcdef\n\\ No newline at end of file',
                          client.get_diff().rstrip())

    def test_diff_relpath(self):
        client = SvnClient(self.local_path)
        self.assertTrue(client.path_exists())
        self.assertTrue(client.detect_presence())

        self.assertEqualDiffs('Index: local/added.txt\n===================================================================\n--- local/added.txt\t(revision 0)\n+++ local/added.txt\t(revision 0)\n@@ -0,0 +1 @@\n+0123456789abcdef\n\\ No newline at end of file\nIndex: local/modified-fs.txt\n===================================================================\n--- local/modified-fs.txt\t(revision 3)\n+++ local/modified-fs.txt\t(working copy)\n@@ -0,0 +1 @@\n+0123456789abcdef\n\\ No newline at end of file\nIndex: local/modified.txt\n===================================================================\n--- local/modified.txt\t(revision 3)\n+++ local/modified.txt\t(working copy)\n@@ -0,0 +1 @@\n+0123456789abcdef\n\\ No newline at end of file', client.get_diff(basepath=os.path.dirname(self.local_path)).rstrip())

    def test_status(self):
        client = SvnClient(self.local_path)
        self.assertTrue(client.path_exists())
        self.assertTrue(client.detect_presence())
        self.assertEquals('A       added.txt\nD       deleted.txt\nM       modified-fs.txt\n!       deleted-fs.txt\nM       modified.txt\n', client.get_status())

    def test_status_relpath(self):
        client = SvnClient(self.local_path)
        self.assertTrue(client.path_exists())
        self.assertTrue(client.detect_presence())
        self.assertEquals('A       local/added.txt\nD       local/deleted.txt\nM       local/modified-fs.txt\n!       local/deleted-fs.txt\nM       local/modified.txt\n', client.get_status(basepath=os.path.dirname(self.local_path)))

    def test_status_untracked(self):
        client = SvnClient(self.local_path)
        self.assertTrue(client.path_exists())
        self.assertTrue(client.detect_presence())
        self.assertEquals('?       added-fs.txt\nA       added.txt\nD       deleted.txt\nM       modified-fs.txt\n!       deleted-fs.txt\nM       modified.txt\n', client.get_status(untracked=True))


class SvnExportRepositoryClientTest(SvnClientTestSetups):

    @classmethod
    def setUpClass(self):
        SvnClientTestSetups.setUpClass()
        client = SvnClient(self.local_path)
        client.checkout(self.local_url)

        self.basepath_export = os.path.join(self.root_directory, 'export')

    def tearDown(self):
        pass

    def test_export_repository(self):
        client = SvnClient(self.local_path)
        self.assertTrue(
          client.export_repository('',
            self.basepath_export)
        )

        self.assertTrue(os.path.exists(self.basepath_export + '.tar.gz'))
        self.assertFalse(os.path.exists(self.basepath_export + '.tar'))
        self.assertFalse(os.path.exists(self.basepath_export))
