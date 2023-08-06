
if 'has_apycot_environment' in schema:
    rql('SET P source_repository REPO WHERE P has_apycot_environment PE, PE local_repository REPO, NOT P source_repository R')

    commit()
