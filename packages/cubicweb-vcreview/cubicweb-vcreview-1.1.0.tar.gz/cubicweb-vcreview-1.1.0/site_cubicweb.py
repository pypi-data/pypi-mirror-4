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

from cubicweb.mttransforms import ENGINE

from cubes.vcsfile.docparser import Diff2HTMLTransform

COMPONENT_CONTEXT = 'navcontentbottom'
def insert_point_callback(ipid, trdata, w):
    context = trdata.appobject
    cw = context._cw
    e_schema = getattr(context, 'e_schema', None)
    if e_schema is None:
        # not an entity
        return
    if 'point_of' not in e_schema.objrels:
        # no InsertionPoint on this entity
        return
    ipoint = cw.execute('InsertionPoint IP WHERE IP point_of X, X eid %(x)s, IP lid %(id)s',
                        {'x': context.eid, 'id': ipid})
    if ipoint:
        assert len(ipoint) == 1
        ipoint = ipoint.get_entity(0, 0)
        extra = {}
    else:
        ipoint = cw.vreg['etypes'].etype_class('InsertionPoint')(cw)
        ipoint.eid = cw.varmaker.next()
        extra = {'formparams': {'lid': ipid, 'point_of': context.eid}}
    w(u'<div id="%s%s">' % (COMPONENT_CONTEXT, ipoint.eid))
    for comp in cw.vreg['ctxcomponents'].poss_visible_objects(
        cw, rset=ipoint.cw_rset, entity=ipoint, context=COMPONENT_CONTEXT,
        __cache=None, **extra):
        if comp is not None:
            comp.render(w=w)
    w(u'</div>')

if Diff2HTMLTransform.name in ENGINE.transforms:
    ENGINE.remove_transform(Diff2HTMLTransform.name, 'text/x-diff')
ENGINE.add_transform(Diff2HTMLTransform(insert_point_callback))
