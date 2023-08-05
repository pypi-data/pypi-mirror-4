from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
import json
from AccessControl import getSecurityManager

try:
    from collective.flowplayer.interfaces import IFlowPlayable
    FLOWPLAYER_EXISTS = True
except ImportError:
    FLOWPLAYER_EXISTS = False

class GetMediaShowItemView(BrowserView):
    """ Class that extracts relevant information for the slideshow
    """
    def getJSON(self):
        if hasattr(self.request, 'presentation'):
            presentation = self.request['presentation']
        else:
            presentation = "false"
        
        presentationMode = False
        
        if presentation.find("true") != -1:
            presentationMode = True
        
        callback = hasattr(self.request, 'callback') and 'json' + self.request['callback'] or None
        
        media = self.getMediaURL()
        mediaType = self.getMediaType()
        
        if hasattr(self.context, "title"):
            title = self.context.title
        elif hasattr(self.context, "Title"):
            title = self.context.Title()
        else:
            title = ""
        
        if presentationMode and hasattr(self.context, 'aq_explicit') and hasattr(self.context.aq_explicit, "getText"):
                description = self.context.getText()
        elif hasattr(self, "description"):
            description = self.context.description
        elif hasattr(self.context, "Description"):
            description = self.context.Description()
        else:
            description = ""
            
        type = self.context.portal_type
        
        #python to json encoding
        jsonStr = json.dumps({"title": title, "description":description, "type": type, "media": {"url": media, "type": mediaType}})
        
        #Manual encoding 
        #jsonStr = '{"title": "'+title+'", "description": "'+description+'", "type": "'+type+'", "media": {"url": "'+media+'", "type//" : "'+mediaType+'"}}'
        
        if callback is not None:
            return callback +'(' + jsonStr + ')'
        else:
            return jsonStr
        
    def sanitizeStringForJson(self, str):
        str = str.replace("\n", " ").replace('"', '\\"').replace("'", "\\'");
        return str
     
    def getMediaURL(self):
        """ finds and returns relevant leading media for the context item
        """
        item = self.context
        
        if(self.isVideo(item)):
            return item.absolute_url()
        
        if item.portal_type == 'Image':
            return item.absolute_url() + '/image_large'
        
        if item.portal_type == 'Link' and (item.remoteUrl.find("youtube.com") > -1 or item.remoteUrl.find("vimeo.com") > -1):
            return item.remoteUrl
        
        catalog = getToolByName(self.context, 'portal_catalog')
        plone_utils = getToolByName(self.context, 'plone_utils')
        path = '/'.join(item.getPhysicalPath())
        
        if plone_utils.isStructuralFolder(item):
            results = catalog.searchResults(path = {'query' : path,'depth' : 1 }, type = ['Image', 'File'], sort_on = 'getObjPositionInParent')
            if len(results) > 0:
                leadMedia = results[0]
                if leadMedia.portal_type == 'Image':
                    return leadMedia.getURL() + '/image_large'
                else:
                    return leadMedia.getURL()
            else:
                return ""
        else:
            #TODO: Add lead image support and News Item Image support
            return ""
        
    def getMediaType(self):
        """ Finds and returns the type of lead media
        """ 
        item = self.context
        
        try:
            if(self.isVideo(item)):
                return "Video"
            elif item.portal_type == 'Link' and item.remoteUrl.find("youtube.com") > -1:
                return "Youtube"
            elif item.portal_type == 'Link' and item.remoteUrl.find("vimeo.com") > -1:
                return "Vimeo"
            else:
                return "Image"
        except:
            if(self.isVideo(item)):
                return "Video"
            elif item.portal_type == 'Link' and item.getObject().remoteUrl.find("youtube.com") > -1:
                return "Youtube"
            elif item.portal_type == 'Link' and item.getObject().remoteUrl.find("vimeo.com") > -1:
                return "Vimeo"
            else:
                return "Image"
    
    
    def isVideo(self, item):
        if FLOWPLAYER_EXISTS:
            result = IFlowPlayable.providedBy(item)
        else:
            result = False
        return result
    
    
class MediaShowListingView(BrowserView):
    """ Class that extracts relevant information for the slideshow
    """
    
    def getJSON(self):    
        #--- Checking for recursive mode
        if hasattr(self.request, 'recursive'):
            recursive = self.request['recursive']
        else:
            recursive = "false"
        
        recursiveMode = False
        
        if recursive.find("true") != -1:
            recursiveMode = True
        #---
        
        callback = hasattr(self.request, 'callback') and 'json' + self.request['callback'] or None
        jsonStr = ""
        
        item = self.context     
        
        catalog = getToolByName(self.context, 'portal_catalog')
        plone_utils = getToolByName(self.context, 'plone_utils')
        path = '/'.join(item.getPhysicalPath())
        
        if item.portal_type == "Folder" or (item.restrictedTraverse('@@plone').isStructuralFolder()  and (item.portal_type != "Topic" and item.portal_type != "Collection") and item.portal_type != "Category Navigator"):
            if not recursiveMode:
                results = catalog.searchResults(path = { 'query' : path, 'depth' : 1 }, sort_on = 'getObjPositionInParent')
            else:
                results = catalog.searchResults(path = { 'query' : path}, sort_on = 'getObjPositionInParent')
        elif item.portal_type == "Topic":
            if item.limitNumber:
                results = catalog.searchResults(item.buildQuery())[:item.itemCount]
            else:
                results = catalog.searchResults(item.buildQuery())
        elif item.portal_type == "Collection":
            results = item.queryCatalog()
                
        #TODO: This next part was made for porseleinplaats website to work with the category navigator and Object type
        #it is a hack and should be revised. the whole query string should be parsed into the search.
        #also found a problem where User objects get a wrong Image media url.
        elif item.portal_type == "Category Navigator" and (hasattr(self.request, 'Subject') or hasattr(self.request, 'Creator')):
            if hasattr(self.request, 'Subject'):
                results = catalog.searchResults(Subject = self.request['Subject'])
            elif hasattr(self.request, 'Creator'):
                results = catalog.searchResults(Creator = self.request['Creator'], portal_type = 'Object')
        else:
            results = []
         
        
        resultArray = []
        
        #Python to JSON encoding
        if not recursiveMode:
            for res in results:
                if self.getMediaURL(res.getObject()) != "" and res.getObject() != self.context:
                    resultArray.append({"url": res.getURL(), "UID": res["UID"]})
        else:
            for res in results:
                if self.getMediaURL(res.getObject()) != "" and res.getObject() != self.context and res.portal_type != 'Folder':
                    resultArray.append({"url": res.getURL(), "UID": res["UID"]})
        
        jsonStr = json.dumps(resultArray[:100])
        
        if callback is not None:
            return callback +'(' + jsonStr + ')'
        else:
            return jsonStr 
        
        
    def getMediaURL(self, item):
        """ finds and returns relevant leading media for the given item
        """
        if(self.isVideo(item)):
            return item.absolute_url()
            
        if item.portal_type == 'Link' and (item.remoteUrl.find("youtube.com") > -1 or item.remoteUrl.find("vimeo.com") > -1):
            return item.remoteUrl
        
        if item.portal_type == 'Image':
            return item.absolute_url()
        
        catalog = getToolByName(self.context, 'portal_catalog')
        plone_utils = getToolByName(self.context, 'plone_utils')
        path = '/'.join(item.getPhysicalPath())
        
        if plone_utils.isStructuralFolder(item):
            results = catalog.searchResults(path = {'query' : path,'depth' : 1 }, type = ['Image', 'File', 'Link'], sort_on = 'getObjPositionInParent')
            if len(results) > 0:
                leadMedia = results[0]
                if leadMedia.portal_type == 'Image':
                    return leadMedia.getURL() + '/image_large'
                elif leadMedia.portal_type == 'Link':
                    try:
                        return leadMedia.remoteUrl
                    except:
                        return leadMedia.getObject().remoteUrl
                else:
                    return leadMedia.getURL()
            else:
                return ""
        else:
            #TODO: Add lead image support and News Item Image support
            return ""
        
    def isVideo(self, item):
        if FLOWPLAYER_EXISTS:
            result = IFlowPlayable.providedBy(item)
        else:
            result = False
        return result
    
    def canView(self, object):
        permission = "View"
        try:
          if not object.acquiredRolesAreUsedBy( permission ):
            for p in object.rolesOfPermission( permission ):
              if p['selected']:
                if p['name'] in user.getRoles():
                  return 1
          else:
           return 1
        except:
            pass
        return 0

