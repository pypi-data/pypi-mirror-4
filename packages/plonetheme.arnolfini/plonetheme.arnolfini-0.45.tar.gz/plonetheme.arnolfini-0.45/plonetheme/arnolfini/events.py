

def mediaObjectAdded(ob, event):
    print "Media Object was added!"
    
    if not ob.checkCreationFlag():
        print "Creating the slideshow folder."
        ob.invokeFactory(type_name="Folder", id='slideshow', title='slideshow')
        
        folder = ob['slideshow']
        
        folder.reindexObject()
        try:
            folder.portal_workflow.doActionFor(folder, "publish", comment="Slideshow content automatically published")
        except:
            pass