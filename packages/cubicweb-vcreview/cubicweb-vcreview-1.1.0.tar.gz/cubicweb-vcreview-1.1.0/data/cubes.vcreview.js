/*
 *  :organization: Logilab
 *  :copyright: 2011 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
 *  :contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
 */


/* this function is called on to add activity from inlined form
 *
 * It calls the [add|eid]_activity method on the jsoncontroller and [re]load
 * only the view for the added or edited activity
 */

function addActivity(eid, parentcreated, context) {
    validateForm(
	'has_activityForm' + eid, null,
	function(result, formid, cbargs) {
	    if (parentcreated) {
		// reload the whole section
		reloadCtxComponentsSection(context, result[2].eid, eid);
	    } else {
		// only reload the activity component
		reload('vcreview_activitysection' + eid, 'vcreview.activitysection',
		       'ctxcomponents', null, eid);
	    };
	});
}
