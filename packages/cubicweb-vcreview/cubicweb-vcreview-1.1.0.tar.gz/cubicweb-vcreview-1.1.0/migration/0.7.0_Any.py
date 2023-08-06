import os

with dropped_constraints('Patch', 'patch_name', droprequired=True):
    add_attribute('Patch', 'patch_name')
    i = 0
    for row in rql('Patch P'):
        patch_eid = row[0]
        patch = session.entity_from_eid(patch_eid)
        directory, filename = rql('Any D,F ORDERBY R DESC LIMIT 1 '
                                  'WHERE P eid %(e)s, P patch_revision VC, VC from_revision REV, REV revision R, VC content_for VF, VF directory D, VF name F',
                                  {'e': patch_eid})[0]
        path = os.path.join(directory or '', filename)
        patch.set_attributes(patch_name=path)
        i += 1
        if i % 100 == 0:
            commit(ask_confirm=False)

commit()
