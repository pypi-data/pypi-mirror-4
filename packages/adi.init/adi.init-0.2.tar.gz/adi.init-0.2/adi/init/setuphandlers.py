def deletePloneFolders(p):
    """Delete the standard Plone stuff that we don't need
    """
# Delete standard Plone stuff..
    existing = p.objectIds()
    itemsToDelete = ['Members', 'news', 'events', 'front-page']
    for item in itemsToDelete:
        if item in existing:
            p.manage_delObjects(item)


def setupVarious(context):

 # Ordinarily, GenericSetup handlers check for the existence of XML files.
 # Here, we are not parsing an XML file, but we use this text file as a
 # flag to check that we actually meant for this import step to be run.
 # The file is found in profiles/default.

    portal = context.getSite()

    if context.readDataFile('adi.init.marker.txt') is None:
        return

# Add additional setup code here
    deletePloneFolders(portal)

