# -*- coding: utf-8 -*-
import os.path as osp

from mercurial import commands, hg, ui

from cubicweb import Unauthorized, ValidationError, Binary
from cubicweb.devtools.testlib import CubicWebTC

from cubes.mercurial_server.utils import mscui
from cubes.mercurial_server.testutils import MercurialServerTCMixin

class HooksBasicTC(MercurialServerTCMixin, CubicWebTC):
    # msc = MercurialServerConfig

    def test_nonascii_login(self):
        req = self.request()
        user = self.create_user(req, login=u'françois')
        self.commit()
        req = self.request()
        with self.assertRaises(ValidationError):
            req.create_entity('SshPubKey',
                              data=Binary('42'),
                              reverse_public_key=user)

    def _test_permission_prologue(self):
        access_key = self.user().public_key[0]
        perm = self.admin_user_repo.reverse_granted_on[0]
        self._assert_end_of_prologue(access_key, perm)
        req = self.request()
        return req.entity_from_eid(access_key.eid), req.entity_from_eid(perm.eid)

    def _assert_end_of_prologue(self, access_key, perm):
        # Testing addition
        pubkey = self._hgadmin_file_content('default', 'keys', self.server_config.keys_subdir,
                                            self.user().login, str(access_key.eid))
        self.assertEqual(pubkey, 'admin private key')

        # Check access.conf content
        content = self._hgadmin_file_content('default', self.server_config.conf_filename)
        self.assertEqual(content,
                         'write user=cw/%(login)s/%(key_eid)d repo=admin_repo\n'
                         % {'login': self.user().login,
                            'key_eid': access_key.eid})

    def test_msc_regeration_service(self):
        access_key, perm = self._test_permission_prologue()

        userdesc = self.session.user.format_name_for_mercurial()
        msc = self.server_config
        with msc.exec_in_hgadmin_clone("pouette", user=userdesc) as (ui, hgrepo):
            commands.remove(hgrepo.ui, hgrepo,
                            osp.join(hgrepo.root, 'keys', msc.keys_subdir))
            filename = osp.join(hgrepo.root, msc.conf_filename_str)
            with open(filename, 'wb') as access:
                access.write('')
        self.vreg['services'].select('regenerate_hgadmin_repo', self.session).call(self.server_config.eid)
        self._assert_end_of_prologue(access_key, perm)

    def test_msc_deletion_ok(self):
        access_key, _perm = self._test_permission_prologue()
        self.execute('DELETE MercurialServerConfig X WHERE X eid %s' % self.server_config.eid)
        self.commit()

        # Check access.conf content
        content = self._hgadmin_file_content('default', self.server_config.conf_filename)
        self.assertEqual(content, '\n')

        with self.assertRaises(IOError):
            self._hgadmin_file_content('default', 'keys', self.server_config.keys_subdir,
                                       self.user().login, str(access_key.eid))

    def test_msc_deletion_with_rollback_inside(self):
        """ on deletion failure (i.e.: deletion order is issued
        but the trasnaction fails), the hgadmin repo files should
        be untouched -- though we may observe a pair of deletion commit/backout
        at the mercurial repository level
        """
        access_key, perm = self._test_permission_prologue()
        self.execute('DELETE MercurialServerConfig X WHERE X eid %s' % self.server_config.eid)
        self.rollback()

        self._assert_end_of_prologue(access_key, perm)

        # check that a 'backout' commit did happen
        hgrepo = hg.repository(mscui(), self.server_config.hgadmin_repopath)
        commands.log(hgrepo.ui, hgrepo)
        self.assertTrue('backout' in ''.join(hgrepo.ui._output))

    def test_permission_AUD(self):
        """ Test Adding, Updating and Deleting """
        access_key, perm = self._test_permission_prologue()
        # Updating
        perm.set_attributes(permission_level=u"write")
        self.commit() # Triggers hooks
        # Testing update
        # Check access.conf content
        content = self._hgadmin_file_content('default', self.server_config.conf_filename)
        self.assertEqual(content,
                         'write user=cw/%(login)s/%(key_eid)d repo=admin_repo\n'
                         % {'login': self.user().login,
                            'key_eid': access_key.eid,
                            })


        # Deleting the permission, thus the access_key relation
        perm.cw_delete()
        self.commit() # Triggers hooks
        #Check access.conf content
        content = self._hgadmin_file_content('default', self.server_config.conf_filename)
        self.assertEqual(content, '\n')


    def test_accesskey_AUD(self):
        """ Test Adding, Updating and Deleting"""
        access_key, perm = self._test_permission_prologue()

        # Updating
        access_key.set_attributes(data=Binary('24'))
        self.commit() # Triggers hooks
        # Testing update
        pubkey = self._hgadmin_file_content('default', 'keys', 'cw',
                                            self.user().login, str(access_key.eid))
        self.assertEqual(pubkey, '24')

        # Deleting the key, thus the access_key relation
        access_key.cw_delete()
        self.commit() # Triggers hooks
        # Testing deletion
        with self.assertRaises(IOError) as exc :
            pubkey = self._hgadmin_file_content('default', 'keys', 'cw',
                                                self.user().login, str(access_key.eid))

        # Check access.conf content
        content = self._hgadmin_file_content('default', self.server_config.conf_filename)
        self.assertEqual(content, '\n')


    def test_consistent_permissions(self):
        """ Test at most one permissions for any (key, repo) pair"""
        req = self.request()
        # Adding
        access_key = req.create_entity('SshPubKey',
                                       data=Binary('42'),
                                       reverse_public_key=self.user())
        perm = req.create_entity('MercurialServerPermission',
                                 permission_level=u'read',
                                 access_key=access_key,
                                 granted_on=self.admin_user_repo)
        self.commit() # Triggers hooks
        with self.assertRaises(ValidationError) as exc :
            # The relations access_key and repo are inlined ...
            perm = req.create_entity('MercurialServerPermission',
                                     permission_level=u'deny',
                                     access_key=access_key,
                                     granted_on=self.admin_user_repo)
            self.commit() # ... so are checked immediatly even without commit



class SchemaPermTC(MercurialServerTCMixin, CubicWebTC):

    def test_ordinary_user_AUD(self):
        toto = self.create_user(u'toto')
        titi = self.create_user(u'titi')
        self.commit()
        with self.userlogin('toto') as cnx:
            # toto cannot create a mercurial server config
            req = cnx.request()
            with self.assertRaises(Unauthorized):
                self.create_local_mercurial_server(self.basepath, 'for_toto')
        with self.userlogin('toto') as cnx:
            # without a public key, toto cannot create a hosted repository
            req = cnx.request()
            toto_repo = self.create_local_mercurial_repo(self.basepath,
                                                         'default', 'toto_repo',
                                                         u'Repo_for_user_toto')
            with self.assertRaises(ValidationError) as wraperr:
                toto_repo.set_relations(hosted_by=self.server_config)
            self.assertEqual({'hosted_by': 'To create a hosted repository, toto must have a public key'},
                             wraperr.exception.args[1])
        with self.userlogin('titi') as cnx:
            # user titi owns a Repository, but not hosted_by
            req = cnx.request()
            pubkey = req.create_entity('SshPubKey', data=Binary('titi public key'),
                                       reverse_public_key=titi.eid)
            cnx.commit()
            titi_repo = self.create_local_mercurial_repo(self.basepath,
                                                         'default', 'titi_repo',
                                                         u'Repo_for_user_titi')
            cnx.commit()
        with self.userlogin('toto') as cnx:
            req = cnx.request()
            pubkey = req.create_entity('SshPubKey', data=Binary('toto public key'),
                                       reverse_public_key=toto.eid)
            cnx.commit()
            req = cnx.request()
            toto_repo = self.create_local_mercurial_repo(self.basepath,
                                                         'default', 'toto_repo',
                                                         u'Repo_for_user_toto')
            toto_repo.set_relations(hosted_by=self.server_config)
            cnx.commit()
            req = cnx.request()
            with self.assertRaises(ValidationError) as wraperr:
                # attempting to set titi repo hosted_by mcs fails
                req.execute('SET R hosted_by M WHERE R eid %(r)s, M eid %(m)s',
                            {'r': titi_repo.eid, 'm': self.server_config.eid})
            self.assertEqual({'hosted_by': ('Only managers or owners can set a '
                                            'repository to a mercurial-server host.')},
                wraperr.exception.args[1])
            req = cnx.request()
            req.entity_from_eid(toto_repo.eid)
            self.assertEqual(1, len(toto_repo.reverse_granted_on))
            content = self._hgadmin_file_content('default', self.server_config.conf_filename)
            self.assertEqual(['write user=cw/admin/959 repo=admin_repo',
                              'write user=cw/toto/972 repo=toto_repo'],
                             content.splitlines())
            pk = self._hgadmin_file_content('default', 'keys', self.server_config.keys_subdir,
                                                toto.login, str(pubkey.eid))
            self.assertEqual('toto public key', pk)
        self.execute('DELETE CWUser U WHERE U login "toto"')
        self.commit()
        content = self._hgadmin_file_content('default', self.server_config.conf_filename)
        # all info about toto is gone
        self.assertEqual(['write user=cw/admin/959 repo=admin_repo'],
                         content.splitlines())
        with self.assertRaises(IOError):
            self._hgadmin_file_content('default', 'keys', self.server_config.keys_subdir,
                                       toto.login, str(pubkey.eid))
