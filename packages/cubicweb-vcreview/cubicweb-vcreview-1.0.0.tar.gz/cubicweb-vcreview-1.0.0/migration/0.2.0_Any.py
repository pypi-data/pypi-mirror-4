pwf = rql('Workflow X WHERE X name "patch workflow"').get_entity(0, 0)
fdeleted = pwf.transition_by_name('file deleted')
fdeleted.set_permissions(('managers',), reset=False)
