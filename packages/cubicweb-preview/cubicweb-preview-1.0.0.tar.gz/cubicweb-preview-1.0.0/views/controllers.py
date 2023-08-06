"""cube-specific forms/views/actions/components

:organization: SecondWeb
:copyright: 2007-2010 SECOND WEB S.A.S. (Paris, FRANCE), license is LGPL v2.
:contact: http://www.secondweb.fr/ -- mailto:contact@secondweb.fr
:license: GNU Lesser General Public License, v2.1 - http://www.gnu.org/licenses
"""

from os import path as osp

from logilab.common.registry import yes

from cubicweb import NoSelectableObject, ValidationError
from cubicweb.utils import json
from cubicweb.web import Redirect
from cubicweb.web.views.basecontrollers import FormValidatorController, _validation_error

from cubes.preview.utils import preview_dir


class PreviewController(FormValidatorController):
    __select__ = FormValidatorController.__select__ & yes()

    def _extract_typed_edited_eids(self):
        eids = self._cw.form.get('eid')
        if isinstance(eids, basestring):
            eids = [eids]
        eidmap = self._cw.data.get('eidmap', {})
        out = []
        for eid in eids:
            try:
                out.append(int(eidmap.get(eid, eid)))
            except:
                continue
        return out

    def _validate_form(self):
        """ commit-less _validate_form """
        # XXX make the version in cw accept an opt. param
        #     to tell it not to commit ?
        req = self._cw
        try:
            ctrl = req.vreg['controllers'].select('edit', req=req)
        except NoSelectableObject:
            return (False, {None: req._('not authorized')}, None)
        try:
            ctrl.publish(None)
        except ValidationError, ex:
            return (False, _validation_error(req, ex), ctrl._edited_entity)
        except Redirect, ex:
            if ctrl._edited_entity:
                ctrl._edited_entity.complete()
            return (True, ex.location, ctrl._edited_entity)
        except Exception, ex:
            req.cnx.rollback()
            req.exception('unexpected error while validating form')
            return (False, req._(str(ex).decode('utf-8')), ctrl._edited_entity)
        return (False, '???', None)

    def publish(self, rset=None):
        """ sketch of the control flow for both modes (python & js)
        newtab:
        * preview button clicked
        * postForm (invokes controller)
        * PreviewController.publish
        * if not ok: standard trampoline (handleFormValidationResponse)
        * preview_trampoline -> passes html stream
        * rePostFormForPreview -> stores stream into form, form.target = '_blank'
        * postForm
        * PreviewController.publish: grabs html stream from form -> templated stream
        inline:
        * preview button clicked
        * postForm
        * PreviewController.publish
        * if not ok:  standard trampoline (handleFormValidationResponse)
        * preview_trampoline -> passes html fragment
        * handleInlinePreview: appends html fragment
        """
        form = self._cw.form
        # handle cancel action
        if '__redirect_path' not in form:
            eids = self._extract_typed_edited_eids()
            if eids:
                form['__redirectpath'] = eids[0]
        if '__action_preview' in form:
            form['__action_apply'] = form.pop('__action_preview', 'button_preview')
            self._cw.json_request = True
            try:
                status, args, entity = self._validate_form()
                domid = form.get('__domid', 'entityForm')
                if not status: # error, do the standard thing
                    return self.response(domid, status, args, entity)
                preview_mode = form.get('__preview_mode')
                if preview_mode == 'newtab':
                    preview_html = form.get('__preview_html')
                    if preview_html:
                        return preview_html
                stream = self._build_preview_stream(entity, preview_mode)
                return self._preview_trampoline(domid, stream, preview_mode)
            finally:
                self._cw.cnx.rollback()
        else:
            return super(PreviewController, self).publish(rset)

    def _preview_trampoline(self, domid, stream, preview_mode):
        self._cw.set_content_type('text/html')
        jsfunction = 'rePostFormForPreview' if preview_mode == 'newtab' else 'handleInlinePreview'
        return  """<script type="text/javascript">
var html = %s;
window.parent.%s('%s', html);
</script>""" % (json.dumps(stream).replace('/', r'\/'), jsfunction, domid)

    def _build_local_filename(self, idwnl_adapter):
        directory = preview_dir(self._cw.vreg.config)
        filename = '_'.join([str(self._cw.user.eid), str(idwnl_adapter.entity.eid),
                             idwnl_adapter.download_file_name()])
        return osp.join(directory, filename)

    def _handle_downloadables(self):
        # handle downloadable entities created within hooks
        # XXX we need precommit() for operations, too
        eids = self._extract_typed_edited_eids()
        prev_ents = {}
        self._cw.data['preview_entities'] = prev_ents
        for eid in eids:
            entity = self._cw.entity_from_eid(eid)
            adapter = entity.cw_adapt_to('IDownloadable')
            if adapter:
                filename = self._build_local_filename(adapter)
                self.info('PreviewController : saving file %s', filename)
                open(filename, 'w').write(adapter.download_data())
                prev_ents[adapter.entity.eid] = filename

    def _build_preview_stream(self, entity=None, preview_mode='inline'):
        self._handle_downloadables()
        rql = self._cw.form.get('__preview_rql')
        if rql:
            rset = self._cw.execute(rql)
        else:
            rset = entity.as_rset()
        self._cw.form['vid'] = vid = self._cw.form.get('__preview_vid', 'primary')
        self.info('previewing rset %s with vid %s', rset, vid)
        if preview_mode == 'inline':
            view = self._cw.vreg['views'].select(vid, self._cw, rset=rset)
            return view.render()
        # template: delegate construction to view controller
        ctrl = self._cw.vreg['controllers'].select('view', req=self._cw, appli=self.appli)
        return ctrl.publish(entity.as_rset())
