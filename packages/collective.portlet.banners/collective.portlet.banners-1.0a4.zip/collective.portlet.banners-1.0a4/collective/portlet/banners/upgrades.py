def null_upgrade_step(setup_tool):
    """
    This is a null upgrade. Use it when nothing happens
    """
    
    pass

def upgrade_10a1_to_10a2(setup_tool):
    """
    Reimport the properties tool profile.
    """
    
    profile_id = 'profile-collective.portlet.banners:default'
    step_id = 'propertiestool'
    setup_tool.runImportStepFromProfile(profile_id, step_id)