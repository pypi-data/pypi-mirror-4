# copyright 2011 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
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
"""edit entity attributes/relations from any view view, without going to the entity form"""
__docformat__ = "restructuredtext en"

from cubicweb import typed_eid, UnknownEid
from cubicweb.utils import json
from cubicweb.web.views import basecontrollers, reledit
from cubicweb.web.views.ajaxcontroller import ajaxfunc

@ajaxfunc(output_type='xhtml')
def cancel_reledit(self):
    req = self._cw
    form = req.form
    rset = req.eid_rset(typed_eid(form['eid']))
    args = {}
    try:
        args['reload'] = json.loads(form['reload'])
    except ValueError: # not true/false, an absolute url
        assert args['reload'].startswith('http')
    if 'rtype' in form:
        args['rtype'] = form['rtype']
        args['role'] = form['role']
        view = req.vreg['views'].select('reledit', req, rset=rset, rtype=args['rtype'])
    else:
        view = req.vreg['views'].select('edit-related-rset', req, rset=rset,
                                        reload=args['reload'], action=None)
    return self._call_view(view, **args)

@ajaxfunc(output_type='xhtml')
def reledit_form(self):
    req = self._cw
    args = dict((x, req.form[x])
                for x in ('rtype', 'role', 'reload', 'action'))
    rset = req.eid_rset(typed_eid(self._cw.form['eid']))
    try:
        args['reload'] = json.loads(args['reload'])
    except ValueError: # not true/false, an absolute url
        assert args['reload'].startswith('http')
    view = req.vreg['views'].select('reledit', req, rset=rset, rtype=args['rtype'])
    return self._call_view(view, **args)


class ContainerIsGone(basecontrollers.RemoteCallFailed):

    def __init__(self, msg, *args, **kwargs):
        super(ContainerIsGone, self).__init__('--GONE--: ' + msg, *args, **kwargs)


@ajaxfunc(output_type='xhtml')
def edit_related_form(self):
    req = self._cw
    args = dict((x, req.form.get(x))
                for x in ('reload', 'action', 'container', 'rtype', 'role', 'topleveldiv'))
    entity_eid = self._cw.form['eid']
    try:
        rset = req.eid_rset(typed_eid(entity_eid))
    except UnknownEid:
        # this is the second coming ... at this point
        # the entity has been wiped
        if args['action'] != 'delete-related':
            raise
        # we must regenerate the whole reledit thing
        container_eid = args.pop('container')
        try:
            rset = req.eid_rset(typed_eid(container_eid))
        except UnknownEid:
            raise ContainerIsGone('Container %s of deleted entity %s seems to '
                                  'have been deleted too' % (container_eid, entity_eid) )
        view = req.vreg['views'].select('reledit', req, rset=rset, rtype=args['rtype'])
        args.pop('action')
        args.pop('topleveldiv')
        return self._call_view(view, **args)
    try:
        args['reload'] = json.loads(args['reload'])
    except ValueError: # not true/false, an absolute url
        assert args['reload'].startswith('http')
    view = req.vreg['views'].select('edit-related-entity', req, rset=rset,
                                    action=args['action'], reload=args['reload'])
    return self._call_view(view, **args)


def registration_callback(vreg):
    vreg.register_all(globals().values(), __name__, (reledit_form,))
    vreg.register_and_replace(reledit_form, reledit.reledit_form)
