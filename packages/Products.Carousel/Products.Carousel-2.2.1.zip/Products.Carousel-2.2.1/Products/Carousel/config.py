"""Common configuration constants
"""

PROJECTNAME = 'Carousel'

ADD_PERMISSIONS = {
    # -*- extra stuff goes here -*-
    'Carousel Banner': 'Carousel: Add Carousel Banner',
}

CAROUSEL_ID = 'carousel'

from Products.CMFCore.permissions import setDefaultRoles
setDefaultRoles('Carousel: Manage Carousel', ('Manager', 'Site Administrator'))
setDefaultRoles(ADD_PERMISSIONS['Carousel Banner'], ('Manager',))
