import os.path as osp

from mercurial import commands

from cubicweb import Binary, ValidationError
from cubicweb.devtools.testlib import CubicWebTC

from cubes.mercurial_server.testutils import MercurialServerTCMixin


class EntitiesBasicTC(MercurialServerTCMixin, CubicWebTC):
    """ Test features of entities which does not require any mercurial server.
    """

    def test_repotitle_constraint(self):
        with self.assertRaises(ValidationError) as wraperr:
            self.create_local_mercurial_repo(self.basepath, u'default',
                                             u'testrepo', u'test repo')
        wraperr.exception.translate(lambda x:x)
        self.assertEqual({'title-subject': u"u'test repo' doesn't match the '^\\\\w+$' regular expression"},
                         wraperr.exception.args[1])

    def test_exec_in_hgadmin_clone(self):
        req = self.request()
        with self.server_config.exec_in_hgadmin_clone('test commit msg') as (ui, repo):
            filename = osp.join(repo.root, 'whatever.txt')
            with open(filename, 'a') as fobj:
                fobj.write('Hello World\n')
            commands.add(ui, repo, filename)

        content = self._hgadmin_file_content('default', 'whatever.txt')
        self.assertEqual(content, 'Hello World\n')


    def test_mercurial_server_permission(self):
        req = self.request()

        access_key = req.create_entity('SshPubKey',
                                       data=Binary('42'),
                                       reverse_public_key=self.user())

        perm = req.create_entity('MercurialServerPermission',
                                 permission_level=u'read',
                                 access_key=access_key,
                                 granted_on=self.admin_user_repo)

        self.assertEqual(perm.server_config.eid, self.server_config.eid)
        self.assertEqual(perm.pubkey.getvalue(), '42')

    def test_mercurial_server_access_key(self):
        req = self.request()
        access_key = req.create_entity('SshPubKey',
                                       data=Binary('42'),
                                       reverse_public_key=self.user())

        perm = req.create_entity('MercurialServerPermission',
                                 permission_level=u'read',
                                 access_key=access_key,
                                 granted_on=self.admin_user_repo)
        mcs = access_key.mercurial_server_configs
        self.assertListEqual( [m.eid for m in mcs], [self.server_config.eid])

    def test_access_conf_generation(self):
        req = self.request()
        msc = req.entity_from_eid(self.server_config.eid)
        access_key = self.user().public_key[0]
        self.assertEqual(msc.generate_access_conf(),
                         'write user=cw/%(login)s/%(key_eid)d repo=admin_repo\n'
                         % {'login': self.user().login,
                            'key_eid': access_key.eid,
                           })
