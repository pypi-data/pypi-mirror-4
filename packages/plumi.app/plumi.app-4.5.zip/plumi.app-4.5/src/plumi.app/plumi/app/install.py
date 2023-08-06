import logging

from hashlib import md5
from datetime import datetime
from StringIO import StringIO
from persistent.dict import PersistentDict
from DateTime import DateTime
from hashlib import sha1 as sha
from AccessControl import allow_module

from zope.location.interfaces import ISite
from zope.annotation.interfaces import IAnnotations
from zope.i18nmessageid import MessageFactory
from zope.component import getUtility , queryUtility
from zope.component import getMultiAdapter
from zope.app.container.interfaces import INameChooser

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.interfaces import IPropertiesTool
from Products.Five.component import enableSite
from Products.CMFPlone.interfaces import IPropertiesTool
from Products.CMFPlone.utils import base_hasattr

from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignmentMapping, ILocalPortletAssignmentManager
from plone.portlet.collection.collection import Assignment
from plone.registry import field as Field
from plone.registry import Record
from plone.registry.interfaces import IRegistry 
from plone.app.discussion.interfaces import ICommentingTool
from plone.app.discussion.interfaces import IConversation

from collective.transcode.star.interfaces import ITranscodeTool

from plumi.app.translations import createTranslations, deleteTranslations

allow_module('plumi.app.member_area.py')

_ = MessageFactory("plumi")


def app_installation_tasks(self, reinstall=False):
    """Custom Plumi setup code"""
    logger=logging.getLogger('plumi.app')
    logger.info('starting app_installation_tasks. self is %s' %self)
    portal=getToolByName(self,'portal_url').getPortalObject()
    setupRSS(portal, logger)
    setupCollections(portal, logger)

def publishObject(wftool,obj):
    logger=logging.getLogger('plumi.app')
    try:
        logger.info('publishing %s ' % obj)
        wftool.doActionFor(obj,action='publish')
    except WorkflowException:
        logger.error('caught workflow exception!')
        pass

def setupCollections(portal, logger):
    """
       Collections for display 
       latestvideos / featured-videos / news-and-events
    """

    wftool = getToolByName(portal,'portal_workflow')

    #The front page, @@featured_videos_homepage, contains
    #links to 'featured-videos' which is a smart folder containing
    #all the videos with keyword 'featured' and 'lastestvideos'
    #which is a smart folder of the latest videos. this method will
    #simply install them.

    # Items to deploy on install.
    items = (dict(id      = 'featured-videos',
                  title   = _(u'Featured Videos'),
                  desc    = _(u'Videos featured by the editorial team.'),
                  layout  = "video_listing_view",
                  exclude = True),

             dict(id      = 'latestvideos',
                  title   = _(u'Latest Videos'),
                  desc    = _(u''),
                  layout  = "video_listing_view",
                  exclude = False),

             dict(id      = 'recent_comments',
                  title   = _(u'Recent Comments'),
                  desc    = _(u'Recent comments.'),
                  layout  = "folder_listing",
                  exclude = True),

            )

    # Items creation
    for item in items:
        try:
            canon = getattr(portal, item['id'])
            deleteTranslations(canon)
            portal.manage_delObjects([item['id']])
        except:
            ## This is nasty to silence it all
            pass

        # We create the element
        portal.invokeFactory('Topic',
                           id = item['id'],
                           title = item['title'],
                           description = item['desc'].translate({}))

        fv = getattr(portal, item['id'])
 

        # We change its ownership and wf status
        publishObject(wftool, fv)

        # Filter results to ATEngageVideo
        # Have to use the name of the Title (and ATEngageVideo will be 
        #    re-named by configATEngageVideo to Video!)
        # this will actually use ALL objects with title 'Video', which 
        #    means atm, ATEngageVideo and ATVideo
        type_criterion = fv.addCriterion('Type', 'ATPortalTypeCriterion')
        if item['id'] is 'recent_comments':
            type_criterion.setValue( ("Comment") )
            sort_crit = fv.addCriterion('created',"ATSortCriterion")
            right = getUtility(IPortletManager, name='plone.rightcolumn')
            rightColumnInThisContext = getMultiAdapter((portal, right), IPortletAssignmentMapping)
            urltool  = getToolByName(portal, 'portal_url')
            commentsCollectionPortlet = Assignment(header=u"Recent Comments",
                                        limit=5,
                                        target_collection = '/'.join(urltool.getRelativeContentPath(portal.recent_comments)),
                                        random=False,
                                        show_more=True,
                                        show_dates=True)
          
    
            def saveAssignment(mapping, assignment):
                chooser = INameChooser(mapping)
                mapping[chooser.chooseName(None, assignment)] = assignment
            if not rightColumnInThisContext.has_key('recent-comments'):
                saveAssignment(rightColumnInThisContext, commentsCollectionPortlet)
          
    
            def saveAssignment(mapping, assignment):
                chooser = INameChooser(mapping)
                mapping[chooser.chooseName(None, assignment)] = assignment
            if not rightColumnInThisContext.has_key('recent-comments'):
                saveAssignment(rightColumnInThisContext, commentsCollectionPortlet)

        else:
            type_criterion.setValue("Video")
            sort_crit = fv.addCriterion('effective',"ATSortCriterion")

        sort_crit.setReversed(True)

        ## add criteria for showing only published videos
        state_crit = fv.addCriterion('review_state', 'ATListCriterion')
        if item['id'] is 'featured-videos':
            state_crit.setValue(['featured'])
        elif item['id'] is 'news_and_events':
            state_crit.setValue(['published'])
        else:
            state_crit.setValue(['published','featured'])

        if item['exclude'] is True:
            fv.setExcludeFromNav(True)

        if item['layout'] is not None:
            fv.setLayout(item['layout'])

        fv.reindexObject()



def plumi30to31(context, logger=None):

    catalog = getToolByName(context, 'portal_catalog')
    workflow_tool = getToolByName(context,'portal_workflow')

    # Migrate callouts
    callouts = catalog(portal_type='PlumiCallOut')
    for c in callouts:
        # Migrate callout dates
        callout=c.getObject()
        closing = callout.getClosingDate()
        if closing:
            callout.setExpirationDate(closing)
            callout.reindexObject()

        # Migrate callout workflow
        from_state = workflow_tool.getInfoFor(callout,'review_state', wf_id='plone_workflow')
        current_state = workflow_tool.getInfoFor(callout, 'review_state', wf_id='plumi_workflow')
        if current_state != from_state:
            changeWorkflowState(callout, from_state, False)

    # Migrate events
    events = catalog(portal_type='Event')
    for e in events:
        # Migrate event workflow
        event=e.getObject()
        from_state = workflow_tool.getInfoFor(event,'review_state', wf_id='plone_workflow')
        current_state = workflow_tool.getInfoFor(event, 'review_state', wf_id='plumi_workflow')
        if current_state != from_state:
            changeWorkflowState(event, from_state, False)
    # Migrate news
    news = catalog(portal_type='News Item')
    for n in news:
        # Migrate news workflow
        new=n.getObject()
        from_state = workflow_tool.getInfoFor(new,'review_state', wf_id='plone_workflow')
        current_state = workflow_tool.getInfoFor(new, 'review_state', wf_id='plumi_workflow')
        if current_state != from_state:
            changeWorkflowState(new, from_state, False)


    # Migrate Videos
    videos = catalog(portal_type='PlumiVideo')
    tt = getUtility(ITranscodeTool)
    pprop = getUtility(IPropertiesTool)
    config = getattr(pprop, 'plumi_properties', None)
    tok = 0
    fok = 0


    for video in videos:
        # Migrate video annotations
        obj = video.getObject()
        UID = obj.UID()
        if not UID:
            continue
        data = StringIO(obj.getField('video_file').get(obj).data)
        md5sum = md5(data.read()).hexdigest()
        annotations = IAnnotations(obj)
        transcode_profiles = annotations.get('plumi.transcode.profiles', {})
        for profile_name in transcode_profiles.keys():
            profile = transcode_profiles[profile_name]
            path = profile.get('path', None)
            if not path:
                continue
            address = config.videoserver_address
            objRec = tt.get(UID, None)
            if not objRec:
                tt[UID] = PersistentDict()

            fieldRec = tt[UID].get('video_file', None)
            if not fieldRec:
                tt[UID]['video_file']=PersistentDict()
            tt[UID]['video_file'][profile_name] = PersistentDict({'jobId' : None, 'address' : address,'status' : 'ok', 'start' : datetime.now(), 'md5' : md5sum, 'path': path,})
        if transcode_profiles:
            del annotations['plumi.transcode.profiles']

        # Migrate video workflow
        from_state = workflow_tool.getInfoFor(obj,'review_state', wf_id='plone_workflow')
        current_state = workflow_tool.getInfoFor(obj, 'review_state', wf_id='plumi_workflow')
        if current_state != from_state:
            changeWorkflowState(obj, from_state, False)

    # Migrated featured state
    wf = getToolByName(context, 'portal_workflow')
    featured = catalog(Subject='featured')
    for f in featured:
        try:
            obj = f.getObject()
            wf.doActionFor(obj, 'feature')
             # Map changes to the catalogs
            obj.reindexObject(idxs=['allowedRolesAndUsers', 'review_state'])
        except Exception, e:
            print "Could not feature %s" % obj

def plumi31to311(context, logger=None):

    catalog = getToolByName(context, 'portal_catalog')
    commenttool = queryUtility(ICommentingTool)
    # Reindex comments
    videos = catalog(portal_type='PlumiVideo')
    comments = 0
    for video in videos:
        obj = video.getObject()
        conversation = IConversation(obj)
        for r in conversation.getThreads():
            comment_obj = r['comment']
            commenttool.reindexObject(comment_obj)
            comments = comments + 1
    print str(comments) + 'comments updated in videos'

    callouts = catalog(portal_type='PlumiCallOut')
    comments = 0
    for callout in callouts:
        obj = callout.getObject()
        conversation = IConversation(obj)
        for r in conversation.getThreads():
            comment_obj = r['comment']
            commenttool.reindexObject(comment_obj)
            comments = comments + 1
    print str(comments) + 'comments updated in callouts'

    news = catalog(portal_type='News Item')
    comments = 0
    for news_item in news:
        obj = news_item.getObject()
        conversation = IConversation(obj)
        for r in conversation.getThreads():
            comment_obj = r['comment']
            commenttool.reindexObject(comment_obj)
            comments = comments + 1
    print str(comments) + 'comments updated in news'

    events = catalog(portal_type='Event')
    comments = 0
    for event in events:
        obj = event.getObject()
        conversation = IConversation(obj)
        for r in conversation.getThreads():
            comment_obj = r['comment']
            commenttool.reindexObject(comment_obj)
            comments = comments + 1
    print str(comments) + 'comments updated in events'


def plumi311to4(context, logger=None):

    root = getToolByName(context, 'portal_url')
    portal = root.getPortalObject()
    catalog = getToolByName(context, 'portal_catalog')
    log = portal.plone_log
    users = context.acl_users.getUsers()
    for user in users:
        user.setProperties(wysiwyg_editor = 'TinyMCE')

def plumi4to41(context, logger=None):
    # add html5 field to transcode.star registry
    registry = getUtility(IRegistry)
    html5_field = Field.Choice(title = u'Choose video embed method',
                               description=u"Choose if you would like to use just the HTML5 video tag, or Flash (Flowplayer) or if you would like to use HTML5 with Flowplayer as failback for browsers that don't support the HTML5 video tag",
                               values = ['HTML5 video tag', 'HTML5 Flash fallback', 'Flash - Flowplayer'],
                               default = "HTML5 Flash fallback",
                              )
    html5_record = Record(html5_field)
    registry.records['collective.transcode.star.interfaces.ITranscodeSettings.html5'] = html5_record

    #update user favorite folders
    users = context.acl_users.getUsers()
    pm = context.portal_membership
    addable_types = ['Link']
    for user in users:
        mf =  pm.getHomeFolder(user.getId())
        try:
            favs = mf.Favorites
            if base_hasattr(favs, 'setConstrainTypesMode'):
                favs.setConstrainTypesMode(1)
                favs.setImmediatelyAddableTypes(addable_types)
                favs.setLocallyAllowedTypes(addable_types)
        except:
            pass


def plumi41to411(context, logger=None):
    AllVideos=context.portal_catalog(portal_type='PlumiVideo',sort_on='Date',sort_order='reverse')
    logger=logging.getLogger('plumi.app')
    logger.info('All videos: %s ' % len(AllVideos))

    for video in AllVideos:
        try:
            trans = video.isTranscodedPlumiVideoObj
            if dict(trans)['low']['status'] == 0:
                logger.info("%s already transcoded. Moving on" % video.id)
                continue
        except:
            logger.info("error checking transcoding status for %s" % video.id)

        try:
            VideoObj=video.getObject()
            logger.info("transcoding %s" % video.id)
            tt = getUtility(ITranscodeTool)
            tt.add(VideoObj, force=True, profiles=['low'])
        except:
            logger.info('Some Error In Transcoded')
            logger.info(VideoObj.id)
     
    logger.info('success')

        
        

def changeWorkflowState(content, state_id, acquire_permissions=False,
                        portal_workflow=None, **kw):
    """Change the workflow state of an object
    @param content: Content obj which state will be changed
    @param state_id: name of the state to put on content
    @param acquire_permissions: True->All permissions unchecked and on riles and
                                acquired
                                False->Applies new state security map
    @param portal_workflow: Provide workflow tool (optimisation) if known
    @param kw: change the values of same name of the state mapping
    @return: None
    """

    if portal_workflow is None:
        portal_workflow = getToolByName(content, 'portal_workflow')

    # Might raise IndexError if no workflow is associated to this type
    wf_def = portal_workflow.getWorkflowsFor(content)[0]
    wf_id= wf_def.getId()

    wf_state = {
        'action': None,
        'actor': None,
        'comments': "Setting state to %s" % state_id,
        'review_state': state_id,
        'time': DateTime(),
        }

    # Updating wf_state from keyword args
    for k in kw.keys():
        # Remove unknown items
        if not wf_state.has_key(k):
            del kw[k]
    if kw.has_key('review_state'):
        del kw['review_state']
    wf_state.update(kw)

    portal_workflow.setStatusOf(wf_id, content, wf_state)

    if acquire_permissions:
        # Acquire all permissions
        for permission in content.possible_permissions():
            content.manage_permission(permission, acquire=1)
    else:
        # Setting new state permissions
        wf_def.updateRoleMappingsFor(content)

    # Map changes to the catalogs
    content.reindexObject(idxs=['allowedRolesAndUsers', 'review_state'])
    return

def setupRSS(portal, logger):
    #turn on RSS site wide
    portal_syn = getToolByName(portal,'portal_syndication',None)
    try:
        portal_syn.enableSyndication(portal)
    except Exception, e:
        #throws exceptdions if already enabled!
        pass

    # turn it on in default_member_content
    # need to loop over all folders inside this folder
    default_member_content = getattr(portal,'default_member_content',None)
    for thing in default_member_content.objectValues():
        try:
            portal_syn.enableSyndication(thing)
        except:
            #throws exceptions if already enabled!
            pass


#        createTranslations(portal,fv)

