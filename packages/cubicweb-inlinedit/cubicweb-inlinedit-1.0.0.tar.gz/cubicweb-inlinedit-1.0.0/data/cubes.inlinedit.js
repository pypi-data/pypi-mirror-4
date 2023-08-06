cw.inlinedit = new Namespace('cw.inlinedit');

jQuery.extend(cw.inlinedit, {

    /* Unhides the part of inlinedit div containing the form
     * hides other parts
     */
    showInlineEditionForm: function (divid) {
        jQuery('#' + divid).hide();
        jQuery('#' + divid + '-value').hide();
        jQuery('#' + divid + '-form').show();
      },

    /* Hides and removes edition parts, incl. messages
     * show initial widget state
     */
    cleanupAfterCancel: function (divid, cbname) {
        jQuery('#appMsg').hide();
        jQuery('div.errorMessage').remove();
        var params = cw.inlinedit._formParams(divid + '-form', {fname: 'cancel_reledit'});
        var d = jQuery('#' + params.divid + '-reledit').loadxhtml(AJAX_BASE_URL, params, 'post');
        d.addCallback(function () { jQuery(cw).trigger('reledit.cancel-reloaded', params);});
    },

     _formidToFname: function (formid) {
         if (formid.startswith('none')) return 'edit_related_form';
         else return 'reledit_form';
     },
     /* Extract specific reledit parameter values
      * from the form. Takes a dict, fills it and returns it.
      */
     _formParams: function(formid, paramobj) {
          jQuery('#' + formid + ' input:hidden').each(function (elt) {
              var name = jQuery(this).attr('name');
              if (name && name.startswith('__reledit|')) {
                  paramobj[name.split('|')[1]] = this.value;
              }
          });
          return paramobj;
       },
    /* callback used on form validation success
     * refreshes the whole page or just the edited reledit zone
     * @param results: [status, ...]
     * @param formid: the dom id of the reledit form
     * @param cbargs: ...
     */
     onSuccess: function (results, formid, cbargs) {
        var fname = cw.inlinedit._formidToFname(formid);
        var params = cw.inlinedit._formParams(formid, {fname: fname});
        var reload = cw.evalJSON(params.reload);
        if (reload || (params.formid == 'deleteconf')) {
            if (typeof reload == 'string') {
                /* Sometimes we want to reload but the reledit thing
                 * updated a key attribute which was a component of the
                 * url
                 */
                document.location.href = reload;
                return;
            }
            else {
                document.location.reload();
                return;
            }
        }
        var reledit_div = params.divid + '-reledit';
        // on deletion we want to refresh the whole widget
        if (params.action == 'delete-related') {
          reledit_div = params.topleveldiv + '-reledit';
        }
        var d = jQuery('#' + reledit_div).loadxhtml(AJAX_BASE_URL, params, 'post');
        d.addCallback(function () { jQuery(cw).trigger('reledit.success-reloaded', params);});
        d.addErrback(function (err, req) {
            if (err.startsWith('--GONE--:')){
                cw.log('expected entity is gone, reloading the page');
                cw.log(err);
                document.location.reload();
                }
            });
    },

    loadInlineForm: function(args) {
        args['pageid'] = pageid;
        var divid = args['divid'];
        var d = jQuery('#' + divid + '-reledit').loadxhtml(AJAX_BASE_URL, args, 'post');
        d.addCallback(function () {
            jQuery(cw).trigger('reledit.inlineform-loaded');
            cw.inlinedit.showInlineEditionForm(divid);
        });
    }
});

var oldRemoteCallFailed = remoteCallFailed;

/* disable default callback for our gone exception

WE SHOULD USE 410 status instead
*/
remoteCallFailed = function(err, req) {
    cw.log(err);
    if (!err.startsWith('--GONE--:')){
        oldRemoteCallFailed(err, req);
    }
};
