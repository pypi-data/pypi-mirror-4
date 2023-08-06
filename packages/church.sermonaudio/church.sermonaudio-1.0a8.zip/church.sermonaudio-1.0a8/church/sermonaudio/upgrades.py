
from Products.CMFCore.utils import getToolByName

default_profile = 'profile-church.sermonaudio:default'

def upgrade_to_100(context):
    print "Upgrading to 100"
    context.runImportStepFromProfile(default_profile, 'catalog')
