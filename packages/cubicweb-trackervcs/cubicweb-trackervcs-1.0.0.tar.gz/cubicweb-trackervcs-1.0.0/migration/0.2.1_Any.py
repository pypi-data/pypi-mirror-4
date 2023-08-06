pwf = rql('Workflow X WHERE X name "patch workflow"').get_entity(0, 0)
for trname in ('ask review', 'reject', 'fold'):
    tr = pwf.transition_by_name(trname)
    tr.set_permissions(('staff',), reset=False)

