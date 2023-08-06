rql('SET R has_review False WHERE R has_review NULL', ask_confirm=True)
commit()
sync_schema_props_perms('has_review')

sync_schema_props_perms('patch_reviewer')
sync_schema_props_perms('patch_committer')
