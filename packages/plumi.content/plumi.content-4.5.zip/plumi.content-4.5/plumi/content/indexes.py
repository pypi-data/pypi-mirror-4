"""This package adds extensions to portal_catalog.
"""
import logging

from zope.component import getUtility
from zope.interface import providedBy, Interface
from zope.annotation.interfaces import IAnnotations
from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from plone.indexer.decorator import indexer

from collective.transcode.star.interfaces import ITranscodeTool
from plumi.content.interfaces import IPlumiVideo


@indexer(IPlumiVideo)
def hasImageAndCaption(object,**kw):
    logger=logging.getLogger('plumi.content.indexes')

    logger.debug('hasImageAndCaption - have %s ' % object )
    img = object.getThumbnailImage()
    #check that the image is set
    if img is not None and img is not '':
        caption = object.getThumbnailImageDescription() or u''
        md = {'image': True, 'caption': caption }
    else:
        md = {'image': False, 'caption': u''}

    logger.debug('hasImageAndCaption returning %s  . thumbnail object is %s' %
                 (md, object.getThumbnailImage()))
    return md

@indexer(IPlumiVideo)
def isTranscodedPlumiVideoObj(object,**kw):
    logger=logging.getLogger('plumi.content.indexes')
    logger.debug(' isTranscodedPlumiVideoObj - have %s ' % object )
    try:
        tt = getUtility(ITranscodeTool)
        return tt[object.UID()]['video_file']
    except:
        return

@indexer(IPlumiVideo)
def isPublishablePlumiVideoObj(object,**kw):
    logger=logging.getLogger('plumi.content.indexes')
    logger.debug(' isPublishablePlumiVideoObj - have %s ' % object )

    portal_workflow = getToolByName(object,'portal_workflow')
    portal_membership = getToolByName(object,'portal_membership')
    portal_contentlicensing = getToolByName(object,'portal_contentlicensing')

    #wf state
    item_state = portal_workflow.getInfoFor(object, 'review_state', '')
    #name of creator 
    member_name = object.Creator()
    #get the actual user object
    user = portal_membership.getMemberById(member_name)
    object.plone_log("Item %s by %s is in state %s. user is %s " % (object.absolute_url(), member_name, item_state,user))
    if user is None:
        object.plone_log("No matching members??")

    if user is not None and item_state == 'published':
        (url,length,type) = object.getFileAttribs()
        cclicense = portal_contentlicensing.getLicenseAndHolderFromObject(object)
        cclicense_text = portal_contentlicensing.DefaultSiteLicense[0]
        cclicense_url  = None
        if cclicense[1][1] != 'None':
                cclicense_text = cclicense[1][1]
        if cclicense[1][2] != 'None':
                cclicense_url  = cclicense[1][2]

        d = {
              'published':True,
              'item_title': object.Title(),
              'item_creator_email': user.getProperty('email',''),
              'item_creator_fullname':user.getProperty('fullname',''),
              'subject': object.Subject(),
              'item_rfc822_datetime': DateTime(object.Date()).rfc822(),
              'item_rfc3339_datetime': DateTime(object.Date()).HTML4(),
              'file_url': url,
              'file_length':length,
              'file_type':type,
              'item_url':object.absolute_url(),
              'license_text':cclicense_text,
              'license_url':cclicense_url
            }
    else:
        d = {'published': False }

    return d

@indexer(IPlumiVideo)
def videoDuration(object,**kw):
    logger=logging.getLogger('plumi.content.indexes')
    logger.debug('videoDuration - have %s ' % object )
    duration = object.plumiVideoDuration()
    logger.debug(' videoDuration returning %s  ' % (duration))
    return duration