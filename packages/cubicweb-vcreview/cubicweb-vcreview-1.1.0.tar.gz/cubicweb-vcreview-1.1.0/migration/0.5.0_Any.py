with dropped_constraints('InsertionPoint', 'lid', droprequired=True):
    add_attribute('InsertionPoint', 'lid')
    for ip in rql('Any X,I WHERE X is InsertionPoint, X id I').entities():
        ip.set_attributes(lid=int(ip.id))
commit()

drop_attribute('InsertionPoint', 'id')
sync_schema_props_perms('InsertionPoint')

# we have now insertion point on patch comment, needs +1 decay
rql('SET X lid LID+1 WHERE X is InsertionPoint, X lid LID')
commit()
