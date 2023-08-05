def deleteDefaultContent(p):
    """Deletes default contents
    """
    existing = p.objectIds()
    itemsToDelete = ['Members', 'news', 'events', 'front-page', ]
    for item in itemsToDelete:
        if item in existing:
            p.manage_delObjects(item)
            print u"adi.init-INSTALL-INFO: Deleted %s" %(item)
        else:
            print u"adi.init-INSTALL-INFO: Skipped deletion of %s, doesn't exists." %(item)

def addSimpleContent(p):
    """ Add some sample content
    """
    existing = p.objectIds()
    contentIds = ['go-to-welcome', 'welcome', 'about', 'contact']
    contentExeptions = ['go-to-welcome','contact']
    for contentId in contentIds:
        contentTitle = str.capitalize(contentId)
        contentChild = contentId+'-info'
        if contentId not in existing:
            # general content population
            if contentId not in contentExeptions:
                p.invokeFactory(type_name="Folder", id=contentId, title=contentTitle)
                contekst = p[contentId]
                contekst.invokeFactory(type_name="Document", id=contentChild, title=contentTitle)
                contekst.setDefaultPage(contentChild)

            if contentId is 'go-to-welcome':      
                p.invokeFactory(type_name="Link", id=contentId, title=contentId, remoteUrl="./welcome")
                p.setDefaultPage(contentId)
            if contentId is 'contact':
                p.invokeFactory(type_name="Folder", id=contentId, title=contentTitle)
                p.contact.setLayout(contentChild) # TODO: replace contact with contentId
            print u"adi.init-INSTALL-INFO: Created %s" %(contentId)
        else:
            print u"adi.init-INSTALL-INFO: Skipped creation of %s, exists already." %(contentId)
    print u"adi.init-INSTALL-INFO: *** Installation finished ***"

def setupVarious(context):

 # Ordinarily, GenericSetup handlers check for the existence of XML files.
 # Here, we are not parsing an XML file, but we use this text file as a
 # flag to check that we actually meant for this import step to be run.
 # The file is found in profiles/default.

    portal = context.getSite()

    if context.readDataFile('adi.samplecontent.marker.txt') is None:
        return

# Add additional setup code here
    deleteDefaultContent(portal)
    addSimpleContent(portal)
