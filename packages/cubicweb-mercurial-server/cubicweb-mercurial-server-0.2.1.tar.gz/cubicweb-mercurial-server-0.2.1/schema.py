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

"""cubicweb-mercurial-server schema"""

from yams.buildobjs import (EntityType, RelationDefinition, SubjectRelation,
                            String, DEFAULT_ATTRPERMS)
from yams.constraints import RegexpConstraint

from cubicweb.schema import RQLConstraint, RRQLExpression, ERQLExpression

from cubes.vcsfile.schema import Repository


Repository.__permissions__['add'] += ('users', ) # XXX Validate this
Repository.__permissions__['update'] += ('users', ) # XXX Validate this
Repository.__permissions__['delete'] += ('owners', ) # XXX Validate this

repotitle = Repository.get_relation('title')
repotitle.constraints = [RegexpConstraint(r'^\w+$')]

class MercurialServerConfig(EntityType):
    __permissions__ = {
        'read':   ('managers', 'users'),
        # 'add' is further restrained by the ability to create hgadmin_repository mandatory relation
        'add':    ('managers', 'users'),
        'update': ('managers', 'owners'),
        'delete': ('managers', 'owners'),
        }
    name = String(required=True, maxsize=128, fulltextindexed=True)
    base_url = String(required=True,
                      description=_('Base URL to access the mercurial server (example: "ssh://hg@my.server")'))
    hgadmin_path = String(required=True, default='hgadmin',
                          description=_('Path of the mercurial repository holding the access '
                                        'configuration file and the keys (relative to base_url)'))
    conf_filename = String(required=True,
                           default='access.conf',
                           description=_('The name of the `access.conf`-like file to be generated.'))
    keys_subdir = String(required=True,
                         default=u'cw',
                         description=_('The subdirectory (relative to "hgadmin/keys") in '
                                       'which public keys will be written.'))


class hosted_by(RelationDefinition):
    """ Tell that the Repository subject is hosted and administered by
    the the MercurialServerConfig object"""
    __permissions__ = {
        'read':   ('managers', 'users'),
        'add':    ('managers', 'users'),
        'delete': ('managers', 'users'),
        }
    subject = 'Repository'
    inlined = True
    object = 'MercurialServerConfig'
    cardinality = '?*'
    composite = 'object'

class hgadmin_repository(RelationDefinition):
    """ The VCSRepository representing the hgadmin repo of the mercurial-server """
    __permissions__ = {
        'read':   ('managers', 'users'),
        'add':    ('managers',),
        'delete': ('managers',),
        }

    subject = 'MercurialServerConfig'
    object = 'Repository'
    cardinality = '1?'
    inlined = True
    composite = 'subject'


class SshPubKey(EntityType):
    __permissions__ = {
        'read':   ('managers', 'users'),
        'add':    ('managers', 'users'),
        'update': ('managers', ERQLExpression('U public_key X')),
        'delete': ('managers', ERQLExpression('U public_key X')),
        }
    data = Bytes(required=True)


class public_key(RelationDefinition):
    __permissions = {'read':   ('managers', 'users'),
                     'add':    ('managers', RRQLExpression('S identity U')),
                     'delete': ('managers', RRQLExpression('S identity U')),}
    subject = 'CWUser'
    object = 'SshPubKey'
    description=_('Public key')
    composite='subject'
    cardinality='*1'


class MercurialServerPermission(EntityType):
    """ Represent a reified relation : the permission given by a SSH key on a repository """
    __permissions__ = {
        'read':   ('managers', 'users'),
        'add':    ('managers', 'users'),
        'update': ('managers', ERQLExpression('X granted_on R, R hosted_by MSC, U has_update_permission MSC')),
        'delete': ('managers', ERQLExpression('X granted_on R, R hosted_by MSC, U has_update_permission MSC')),
        }

    _perms_for_repo = {
        'read':   ('managers', 'users'),
        'add':    ('managers', RRQLExpression('O hosted_by MSC, U has_update_permission MSC')),
        'delete': ('managers', RRQLExpression('O hosted_by MSC, U has_update_permission MSC')),
        }

    __unique_together__ = [('access_key', 'granted_on')]

    access_key = SubjectRelation('SshPubKey',
                                 description=_('SSH public key identifying who the permission is granted to'),
                                 cardinality='1*',
                                 inlined=True,
                                 composite='object')
    granted_on = SubjectRelation('Repository',
                                 description=_('Mercurial Repository on which the permission is granted'),
                                 cardinality='1*',
                                 inlined=True,
                                 composite='object',
                                 constraints=[RQLConstraint('EXISTS (O hosted_by X)')],
                                 __permissions__ =  _perms_for_repo)
    # at logilab, with evolve, we could make use of a 'publish' level (between write and init)
    permission_level = String(vocabulary=(u'deny', u'read', u'write'))

