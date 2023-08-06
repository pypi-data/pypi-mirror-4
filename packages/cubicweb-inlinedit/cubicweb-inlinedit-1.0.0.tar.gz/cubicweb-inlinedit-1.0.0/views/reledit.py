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
from __future__ import with_statement
__docformat__ = "restructuredtext en"
_ = unicode

import copy

from warnings import warn

import cwtags.tag as t

from logilab.mtconverter import xml_escape
from logilab.common.deprecation import deprecated, class_renamed
from logilab.common.decorators import cached
from logilab.common.registry import yes

from cubicweb import neg_role, appobject
from cubicweb.schema import display_name
from cubicweb.utils import json_dumps
from cubicweb.predicates import non_final_entity, match_kwargs
from cubicweb.view import EntityView
from cubicweb.web import uicfg, stdmsgs
from cubicweb.web.formwidgets import Button, SubmitButton

from cubicweb.web.views import reledit as old_cw_reledit

uicfg.ReleditTags._keys = frozenset('novalue_label novalue_include_rtype '
                                    'reload evid rvid edit_target'.split())

class _DummyForm(object):
    __slots__ = ('event_args',)
    def form_render(self, **_args):
        return u''
    def render(self, *_args, **_kwargs):
        return u''
    def append_field(self, *args):
        pass
    def add_hidden(self, *args):
        pass

rctrl = uicfg.reledit_ctrl

def build_divid(rtype, role, entity_eid):
    """ builds an id for the root div of a reledit widget """
    return '%s-%s-%s' % (rtype, role, entity_eid)

@cached
def compute_ttypes(rschema, role):
    warn('[inlinedit 0.3.0] compute_ttypes is deprecated, '
         'use rschema.targets(etype=, role=)', DeprecationWarning)
    return rschema.targets(role=role)

class RelatedEntityEdit(EntityView):
    __regid__ = 'edit-related-entity'
    __select__ = EntityView.__select__ & match_kwargs('action', 'reload')
    # back path to container entity thru rtype/role
    _parent_attrs = ('container', 'topleveldiv', 'rtype', 'role')
    _default_evid = 'incontext'

    def call(self, action=None, reload=False, evid=None, **kwargs):
        w = self.w; rset = self.cw_rset
        if 'container' in kwargs and not evid:
            assert 'rtype' in kwargs, 'container must entail rtype'
            assert 'role' in kwargs, 'container must entail role'
            etype = self._cw.describe(kwargs.get('container'))[0]
            rules = rctrl.etype_get(etype, kwargs.get('rtype'), kwargs.get('role'), '*')
            evid = rules.get('evid', self._default_evid)
        else:
            evid = evid or self._default_evid
        extradata = dict((k, kwargs.get(k))
                         for k in self._parent_attrs)
        with t.div(w, Class=self.__regid__):
            for i in xrange(len(rset)):
                with t.div(w, Class='%s-item' % self.__regid__):
                    self.wview(self.__regid__, rset, row=i, action=action, evid=evid,
                               extradata=extradata, reload=reload, **kwargs)

    def cell_call(self, row, col, action=None, reload=False, extradata=None, evid='incontext', **kwargs):
        entity = self.cw_rset.get_entity(row, col)
        divid = 'none-none-%s' % entity.eid
        value = self._cw.view(evid, entity.as_rset())
        form_handler = self._cw.vreg['reledit'].select('entity-form-handler', self._cw, entity=entity)
        form_handler.apply(self.w, value, entity, divid, reload, action,
                           self._may_edit(entity), self._may_delete(entity),
                           extradata=extradata)

    def _may_edit(self, entity):
        return entity.cw_has_perm('update')

    def _may_delete(self, entity):
        return entity.cw_has_perm('delete')


class AutoClickAndEditFormView(EntityView):
    __regid__ = 'reledit'
    __select__ = non_final_entity() & match_kwargs('rtype')

    def entity_call(self, entity, rtype=None, role='subject',
                    reload=False, # controls reloading the whole page after change
                                  # boolean, eid (to redirect), or
                                  # function taking the subject entity & returning a boolean or an eid
                    action=None):
        """display field to edit entity's `rtype` relation on click"""
        assert rtype
        self._cw.add_css('cubicweb.form.css')
        self._cw.add_js('cubes.inlinedit.js', 'cubicweb.edition.js')
        self.entity = entity
        rschema = self._cw.vreg.schema[rtype]
        self._rules = rctrl.etype_get(self.entity.e_schema.type, rschema.type, role, '*')
        reload = self._compute_reload(rschema, role, reload)
        divid = build_divid(rtype, role, self.entity.eid)
        if rschema.final:
            self._handle_attribute(rschema, role, divid, reload, action)
        else:
            if self._is_composite():
                self._handle_composite(rschema, role, divid, reload, action)
            else:
                self._handle_relation(rschema, role, divid, reload, action)

    def _handle_attribute(self, rschema, role, divid, reload, action):
        rvid = self._rules.get('rvid', None)
        if rvid is not None:
            value = self._cw.view(rvid, entity=self.entity,
                                  rtype=rschema.type, role=role)
        else:
            value = self.entity.printable_value(rschema.type)
        if not self._should_edit_attribute(rschema):
            self.w(value)
            return
        value = value or self._compute_default_value(rschema, role)
        form_handler = self._cw.vreg['reledit'].select('relation-form-handler', self._cw,
                                                       entity=self.entity, rtype=rschema.type)
        form_handler.apply(self.w, value, self.entity, rschema, role, divid, reload, action)

    def _compute_value_editperm(self, rschema, role, rvid, **viewargs):
        related_rset = self.entity.related(rschema.type, role)
        if related_rset:
            value = self._cw.view(rvid, related_rset, role=role, **viewargs)
        else:
            value = self._compute_default_value(rschema, role)
        return value, self._should_edit_relation(rschema, role)

    def _handle_relation(self, rschema, role, divid, reload, action):
        rvid = self._rules.get('rvid', 'autolimited')
        value, permission = self._compute_value_editperm(rschema, role, rvid)
        if not permission:
            return self.w(value)
        form_handler = self._cw.vreg['reledit'].select('relation-form-handler', self._cw,
                                                       entity=self.entity, rtype=rschema.type)
        form_handler.apply(self.w, value, self.entity, rschema, role, divid,
                           reload, action)

    def _handle_composite(self, rschema, role, divid, reload, action):
        rvid = self._rules.get('rvid', 'edit-related-entity')
        value, permission = self._compute_value_editperm(rschema, role, rvid,
                                                         reload=reload, action=action,
                                                         container=self.entity.eid,
                                                         topleveldiv=divid,
                                                         rtype=rschema.type)
        form_handler = self._cw.vreg['reledit'].select('relation-form-handler', self._cw,
                                                       entity=self.entity, rtype=rschema.type)
        form_handler.apply(self.w, value, self.entity, rschema, role, divid,
                           reload, action, self._may_add_related(rschema, role), False)

    def _compute_reload(self, rschema, role, reload):
        ctrl_reload = self._rules.get('reload', reload)
        if callable(ctrl_reload):
            ctrl_reload = ctrl_reload(self.entity)
        if isinstance(ctrl_reload, int) and ctrl_reload > 1: # not True/False
            ctrl_reload = self._cw.build_url(ctrl_reload)
        return ctrl_reload

    def _compute_default_value(self, rschema, role):
        default = self._rules.get('novalue_label')
        if default is None:
            if self._rules.get('novalue_include_rtype'):
                default = self._cw._('<%s not specified>') % display_name(
                    self._cw, rschema.type, role)
            else:
                default = self._cw._('<not specified>')
        else:
            default = self._cw._(default)
        return xml_escape(default)

    def _is_composite(self):
        return self._rules.get('edit_target') == 'related'

    def _may_add_related(self, rschema, role):
        ttypes = rschema.targets(etype=self.entity.e_schema.type, role=role)
        if len(ttypes) > 1: # many etypes: we can't guess right
            return False
        rdef = rschema.role_rdef(self.entity.e_schema, ttypes[0], role)
        card = rdef.role_cardinality(role)
        if card in '?1':
            rset = self.entity.related(rschema, role)
            if len(rset):
                return False
        if role == 'subject':
            kwargs = {'fromeid': self.entity.eid}
        else:
            kwargs = {'toeid': self.entity.eid}
        return rdef.has_perm(self._cw, 'add', **kwargs)

    def _should_edit_attribute(self, rschema):
        entity = self.entity
        rdef = entity.e_schema.rdef(rschema)
        # check permissions
        if not entity.cw_has_perm('update'):
            return False
        rdef = entity.e_schema.rdef(rschema)
        return rdef.has_perm(self._cw, 'update', eid=entity.eid)

    should_edit_attributes = deprecated('[3.9] should_edit_attributes is deprecated,'
                                        ' use _should_edit_attribute instead',
                                        _should_edit_attribute)

    def _should_edit_relation(self, rschema, role):
        eeid = self.entity.eid
        perm_args = {'fromeid': eeid} if role == 'subject' else {'toeid': eeid}
        return rschema.has_perm(self._cw, 'add', **perm_args)

    should_edit_relations = deprecated('[3.9] should_edit_relations is deprecated,'
                                       ' use _should_edit_relation instead',
                                       _should_edit_relation)


class ReleditFormHandler(appobject.AppObject):
    __registry__ = 'reledit'
    __abstract__ = True

    _form_renderer_id = 'base'

    _onclick = (u"cw.inlinedit.loadInlineForm(%s);")
    _cancelclick = "cw.inlinedit.cleanupAfterCancel('%s', '%s')"

    # for both edit_rtype and edit_related
    _editzone = u'<img title="%(msg)s" src="%(logo)s" alt="%(msg)s"/>'
    _editzonemsg = _('click to edit this field')
    _editzonelogo = 'pen_icon.png'

    def _build_edit_zone(self):
        return self._editzone % {'msg' : xml_escape(_(self._cw._(self._editzonemsg))),
                                 'logo': xml_escape(self._cw.data_url(self._editzonelogo))}

    def _setup_form_arguments(self, form, event_args):
        for pname, pvalue in event_args.iteritems():
            if pname == 'reload':
                pvalue = json_dumps(pvalue)
            form.add_hidden('__reledit|' + pname, pvalue)

    def _setup_form_buttons(self, form, divid):
        cancel_callbackname = 'edit_related_form' if divid.startswith('none') else 'reledit_form'
        cancelclick = self._cancelclick % (divid, cancel_callbackname)
        if form.form_buttons: # edition, delete
            form_buttons = []
            for button in form.form_buttons:
                if not button.label.endswith('apply'):
                    if button.label.endswith('cancel'):
                        button = copy.deepcopy(button)
                        button.cwaction = None
                        button.onclick = cancelclick
                    form_buttons.append(button)
            form.form_buttons = form_buttons
        else: # base
            form.form_buttons = [SubmitButton(),
                                 Button(stdmsgs.BUTTON_CANCEL, onclick=cancelclick)]

    def wrap_form(self, divid, value, form, renderer,
                  _edit_related, add_related, _delete_related,
                  view_form_method):
        w = self.w
        with t.div(w, id='%s-reledit' % divid,
                   onmouseout="jQuery('#%s').addClass('hidden')" % divid,
                   onmouseover="jQuery('#%s').removeClass('hidden')" % divid,
                   Class='releditField'):
            with t.div(w, id='%s-value' % divid, Class='editableFieldValue'):
                w(value)
            form.render(renderer=renderer, w=w)
            with t.div(w, id=divid, Class='editableField hidden'):
                view_form_method()

class ReleditEntityFormHandler(ReleditFormHandler):
    __regid__ = 'entity-form-handler'
    __select__ = yes()
    _form_renderer_id = 'base'
    # ui side actions/buttons
    _deletezone = u'<img title="%(msg)s" src="%(logo)s" alt="%(msg)s"/>'
    _deletemsg = _('click to delete this value')
    _deletezonelogo = 'cancel.png'

    _action_formid = {'edit-related': 'edition',
                      'delete-related': 'deleteconf'}

    def apply(self, w, value, entity, divid, reload, action, edit_related=False,
              delete_related=False, extradata=None, **formargs):
        self.w = w
        form, renderer = self._build_form(entity, divid, reload, action,
                                          extradata=extradata, **formargs)
        self.view_form(divid, value, form, renderer, edit_related, delete_related)

    def _build_delete_zone(self):
        return self._deletezone % {'msg': xml_escape(self._cw._(self._deletemsg)),
                                   'logo': xml_escape(self._cw.data_url(self._deletezonelogo))}

    def _build_args(self, entity, reload, action, extradata=None):
        divid = 'none-none-%s' % (entity.eid)
        event_args = {'divid' : divid, 'eid' : entity.eid, 'reload' : reload,
                      'action': action, 'fname' : u'edit_related_form'}
        if extradata:
            event_args.update(extradata)
        return event_args

    def _build_renderer(self, entity):
        return self._cw.vreg['formrenderers'].select(
            self._form_renderer_id, self._cw, entity=entity,
            display_label=True, table_class='attributeForm',
            display_help=False, button_bar_class='buttonbar',
            display_progress_div=False)

    def _build_form(self, entity, divid, reload, action, extradata=None, **formargs):
        event_args = self._build_args(entity, reload, action, extradata)
        if not action or action == 'add-related':
            # the later is handled by the relation form
            form = _DummyForm()
            form.event_args = event_args
            return form, None
        formid = self._action_formid.get(action, 'base')
        form = self._cw.vreg['forms'].select(
            formid, self._cw, rset=entity.as_rset(), entity=entity,
            domid='%s-form' % divid, formtype='inlined',
            action=self._cw.build_url('validateform', __onsuccess='window.parent.cw.inlinedit.onSuccess'),
            cwtarget='eformframe', cssclass='releditForm',
            **formargs)
        # pass reledit arguments
        self._setup_form_arguments(form, event_args)
        # handle buttons
        self._setup_form_buttons(form, divid)
        form.event_args = event_args
        return form, self._build_renderer(entity)

    def wrap_form(self, divid, value, form, renderer,
                  _edit_related, _add_related, _delete_related,
                  view_form_method):
        w = self.w
        with t.div(w, id='%s-reledit' % divid,
                   onmouseout="jQuery('#%s').addClass('hidden')",
                   onmouseover="jQuery('#%s').removeClass('hidden')",
                   Class='editableFieldValue'):
            with t.div(w, id='%s-value' % divid,
                       Class='editableFieldValue'):
                w(value)
            form.render(w=w, renderer=renderer)
            with t.div(w, id=divid, Class='editableField hidden'):
                view_form_method()

    def _edit_action(self, divid, args):
        w = self.w
        args['action'] = 'edit-related'
        with t.div(w, id='%s-update' % divid,
                   onclick=xml_escape(self._onclick % json_dumps(args)),
                   title=self._cw._(self._editzonemsg),
                   Class='editableField'):
            w(self._build_edit_zone())

    def _del_action(self, divid, args):
        w = self.w
        args['action'] = 'delete-related'
        with t.div(w, id='%s-delete' % divid,
                   onclick=xml_escape(self._onclick % json_dumps(args)),
                   title=self._cw._(self._deletemsg),
                   Class="editableField"):
            w(self._build_delete_zone())

    def view_form(self, divid, value, form=None, renderer=None, edit_related=False, delete_related=False):
        def _view_form():
            args = form.event_args.copy()
            if edit_related:
                self._edit_action(divid, args)
            if delete_related:
                self._del_action(divid, args)
        self.wrap_form(divid, value, form, renderer, edit_related, delete_related, False, _view_form)

class ReleditRelationFormHandler(ReleditFormHandler):
    __select__ = yes()
    __registry__ = 'reledit'
    __regid__ = 'relation-form-handler'

    # ui side actions/buttons
    _addzone = u'<img title="%(msg)s" src="%(logo)s" alt="%(msg)s"/>'
    _addmsg = _('click to add a value')
    _addzonelogo = 'plus.png'

    _action_formid = {'edit-rtype': 'base',
                      'add-related': 'edition'}

    def apply(self, w, value, entity, rschema, role, divid, reload, action,
              add_related=False, edit_rtype=True, extradata=None, **formargs):
        self.w = w
        form, renderer = self._build_form(entity, rschema, role, divid, reload, action,
                                          extradata=None, **formargs)
        self.view_form(divid, value, form, renderer, add_related, edit_rtype)

    def _build_add_zone(self):
        return self._addzone % {'msg': xml_escape(self._cw._(self._addmsg)),
                                'logo': xml_escape(self._cw.data_url(self._addzonelogo))}

    def _build_args(self, entity, rtype, role, reload, action, extradata=None):
        divid = build_divid(rtype, role, entity.eid)
        event_args = {'divid' : divid, 'eid' : entity.eid, 'rtype' : rtype,
                      'reload' : reload, 'action': action,
                      'role' : role, 'fname' : u'reledit_form'}
        if extradata:
            event_args.update(extradata)
        return event_args

    def _prepare_form(self, entity, rschema, role, action):
        assert action in ('edit-rtype', 'add-related'), action
        if action == 'edit-rtype':
            return False, entity
        label = True
        # action == 'add'
        add_etype = rschema.targets(etype=entity.e_schema.type, role=role)[0]
        _new_entity = self._cw.vreg['etypes'].etype_class(add_etype)(self._cw)
        _new_entity.eid = self._cw.varmaker.next()
        edit_entity = _new_entity
        # XXX see forms.py ~ 276 and entities.linked_to method
        #     is there another way ?
        self._cw.form['__linkto'] = '%s:%s:%s' % (rschema, entity.eid, neg_role(role))
        return label, edit_entity

    def _build_renderer(self, related_entity, display_label):
        return self._cw.vreg['formrenderers'].select(
            self._form_renderer_id, self._cw, entity=related_entity,
            display_label=display_label,
            table_class='attributeForm' if display_label else '',
            display_help=False, button_bar_class='buttonbar',
            display_progress_div=False)

    def _build_form(self, entity, rschema, role, divid, reload, action,
                    extradata=None, **formargs):
        rtype = rschema.type
        event_args = self._build_args(entity, rtype, role, reload, action, extradata)
        if not action:
            form = _DummyForm()
            form.event_args = event_args
            return form, None
        assert action in ('edit-rtype', 'add-related'), action
        label, edit_entity = self._prepare_form(entity, rschema, role, action)
        formid = self._action_formid.get(action, 'base')
        form = self._cw.vreg['forms'].select(
            formid, self._cw, rset=edit_entity.as_rset(), entity=edit_entity,
            domid='%s-form' % divid, formtype='inlined',
            action=self._cw.build_url('validateform', __onsuccess='window.parent.cw.inlinedit.onSuccess'),
            cwtarget='eformframe', cssclass='releditForm',
            **formargs)
        # pass reledit arguments
        self._setup_form_arguments(form, event_args)
        # handle buttons
        self._setup_form_buttons(form, divid)
        form.event_args = event_args
        if formid == 'base':
            field = form.field_by_name(rtype, role, entity.e_schema)
            form.append_field(field)
        return form, self._build_renderer(edit_entity, label)

    def _add_action(self, divid, args):
        w = self.w
        args['action'] = 'add-related'
        with t.div(w, id='%s-add' % divid,
                   onclick=xml_escape(self._onclick % json_dumps(args)),
                   title=self._cw._(self._addmsg),
                   Class='editableField'):
            w(self._build_add_zone())

    def _edit_action(self, divid, args):
        w = self.w
        args['action'] = 'edit-rtype'
        with t.div(w, id='%s-update' % divid,
                   onclick=xml_escape(self._onclick % json_dumps(args)),
                   title=self._cw._(self._editzonemsg),
                   Class='editableField'):
            w(self._build_edit_zone())

    def view_form(self, divid, value, form=None, renderer=None, add_related=False, edit_rtype=True):
        def _view_form():
            args = form.event_args.copy()
            if edit_rtype:
                self._edit_action(divid, args)
            if add_related:
                self._add_action(divid, args)
        self.wrap_form(divid, value, form, renderer, False, add_related, False, _view_form)


def registration_callback(vreg):
    vreg.register_all(globals().values(), __name__)
    vreg.unregister(old_cw_reledit.ClickAndEditFormView)
    vreg.unregister(old_cw_reledit.AutoClickAndEditFormView)
