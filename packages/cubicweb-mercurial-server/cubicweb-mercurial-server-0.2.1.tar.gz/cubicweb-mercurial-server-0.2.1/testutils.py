# -*- coding: utf-8 -*-
# copyright 2011 Florent Cayré (FRANCE), all rights reserved.
# contact florent.cayre@gmail.com
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.

import tempfile
import os, os.path as osp
import shutil
from contextlib import contextmanager

from mercurial import commands, hg

from cubicweb import Binary

from cubes.vcsfile import bridge

from cubes.mercurial_server.utils import mscui

class MercurialServerTCMixin(object):
    debug = False

    @contextmanager
    def userlogin(self, *args):
        cnx = self.login(*args)
        yield cnx
        self.restore_connection()

    def _prepare_repo(self, basepath, basename, reponame):
        repopath = osp.join(basepath, basename, reponame)
        if osp.isdir(repopath):
            shutil.rmtree(repopath)
        os.makedirs(repopath)
        return repopath

    def create_local_mercurial_repo(self, basepath, basename, reponame, title, req=None):
        """ Create a local mercurial repository """
        repopath = self._prepare_repo(basepath, basename, reponame)
        req = req or self.session
        repo = req.create_entity('Repository',
                                 title=title,
                                 type=u'mercurial',
                                 source_url=u'file://' + repopath)
        return repo

    def create_local_mercurial_server(self, basepath, name):
        # mercurial server creates repo directory recursively but this is not
        # the case in this fake env: we need to create receiving directory first
        self._prepare_repo(basepath, name, 'hgadmin')
        server_config = self.session.create_entity('MercurialServerConfig',
                                                   name=u'test hgs',
                                                   base_url=u'file://' + osp.join(basepath, name),
                                                   hgadmin_path=u'hgadmin')
        source_url = 'file://%s/hgadmin' % osp.join(basepath, name)
        commands.init(mscui(),  source_url.encode('ascii'))
        return server_config

    def refresh(self):
        bridge._REPOHDLRS = {} # wipe this cache, else we get errors on import ...
        with self.session.repo.internal_session() as session:
            bridge.import_content(session, raise_on_error=True)
            session.commit()

    def setup_database(self):
        '''initialize a fake hgadmin repository'''
        super(MercurialServerTCMixin, self).setup_database()
        self.basepath = tempfile.mkdtemp()
        # wipe local repo caches: they get old wrong default push paths
        shutil.rmtree(osp.join(self.config.appdatahome, 'repo_cache'))
        self.server_config = self.create_local_mercurial_server(self.basepath, 'default')
        self.commit()
        self.refresh()
        self.request().create_entity('SshPubKey', data=Binary('admin private key'),
                                     reverse_public_key=self.user())
        self.commit()
        self.admin_user_repo = self.create_local_mercurial_repo(self.basepath, 'default', 'admin_repo',
                                                                u'Repo_for_user_admin')
        self.admin_user_repo.set_relations(hosted_by=self.server_config)
        self.commit()
        self.refresh()

    def tearDown(self):
        '''removes the fake hgadmin repository'''
        super(MercurialServerTCMixin, self).tearDown()
        if self.basepath and osp.isdir(self.basepath):
            if not self.debug:
                shutil.rmtree(self.basepath, ignore_errors=True)
            else:
                print "[DEBUG] repositories can be found in %s" % self.basepath

    def _hgadmin_file_content(self, name, *path):
        path = tuple(str(x) for x in path)
        repo = hg.repository(mscui(),
                             osp.join(self.basepath, name, 'hgadmin'))
        commands.update(repo.ui, repo)
        fullpath = osp.join(repo.root, *path)
        with open(fullpath, 'r') as f:
            return f.read()
