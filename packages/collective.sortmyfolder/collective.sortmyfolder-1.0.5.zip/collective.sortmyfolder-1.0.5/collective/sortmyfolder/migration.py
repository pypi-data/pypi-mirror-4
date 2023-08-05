PROFILE_ID = 'profile-collective.sortmyfolder:default'


def run_actions_step(context):
    context.runImportStepFromProfile(PROFILE_ID, 'actions')
