import logging
import datetime, pytz
import sys

from zope.component import adapts
from zope.interface import implements
from interfaces.plumivideo import IPlumiVideo
from interfaces.workflow import IPlumiWorkflow

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowException
from zope.component import getUtility
from plone.app.async.interfaces import IAsyncService

from zope import i18n
_ = i18n.MessageFactory("plumi")

class PlumiWorkflowAdapter(object):
    implements(IPlumiWorkflow)
    adapts(IPlumiVideo)

    def __init__(self, context):
        self.context = context
        self.async = getUtility(IAsyncService)

    def notifyOwnerVideoSubmitted(self):
        """ Email the owner of the submitted video """
        logger = logging.getLogger('plumi.content.adapters')
        #IPlumiVideo implementing objects only
        if IPlumiVideo.providedBy(self.context):

            obj_title=self.context.Title()
            creator=self.context.Creator()
            obj_url=self.context.absolute_url()
            membr_tool = getToolByName(self.context,'portal_membership')
            member = membr_tool.getMemberById(creator)
            urltool = getToolByName(self.context, 'portal_url')
            portal = urltool.getPortalObject()            
            mTo = member.getProperty('email',None)
            mFrom = portal.getProperty('email_from_address')
            mSubj = 'Your contribution : %s : was submitted for review.' % obj_title            
            if mTo is not None and mTo is not '':
                try:
                    mMsg = 'To: %s\n' % mTo
                    mMsg += 'From: %s\n' % mFrom
                    mMsg += 'Content-Type: text/plain; charset=utf-8\n\n'
                    mMsg += 'Hi %s \nYour contribution has been submitted for review before publishing on the site\n' % member.getProperty('fullname', creator)
                    mMsg += 'Title: %s\n\n' % obj_title
                    mMsg += '%s/view \n\n' % obj_url
                    #send email to object owner
                    logger.info('notifyOwnerVideoSubmitted , im %s - sending email to %s from %s ' % (self.context, mTo, mFrom) )
                    job = self.async.queueJob(sendMail, self.context, mMsg, mSubj)
                    print "job queued: %s" % job
                except Exception, e:
                    logger.error('Didnt actually send email! Something amiss with SecureMailHost. %s' % e)


    def notifyReviewersVideoSubmitted(self):
        """ Email the reviewers of the submitted video """
        logger = logging.getLogger('plumi.content.adapters')
        #IPlumiVideo implementing objects only
        if IPlumiVideo.providedBy(self.context):
            logger.info('notifyReviewersVideoSubmitted , im %s ' % self.context )
            obj_title=self.context.Title()
            obj_url=self.context.absolute_url()
            creator = self.context.Creator()
            membr_tool = getToolByName(self.context,'portal_membership')
            member=membr_tool.getMemberById(creator)
            creator_info = {'fullname':member.getProperty('fullname', 'Fullname missing'),
                            'email':member.getProperty('email', None)}

            #search for reviewers 
            reviewers = membr_tool.searchForMembers(roles=['Reviewer'])
            for reviewer in reviewers:
                memberId = reviewer.id
                try:
                    mTo = reviewer.getProperty('email',None)
                    urltool = getToolByName(self.context, 'portal_url')
                    portal = urltool.getPortalObject()
                    mFrom = portal.getProperty('email_from_address')
                    mSubj = '%s -- submitted for your review' % obj_title
                    mMsg = 'To: %s\n' % mTo
                    mMsg += 'From: %s\n' % mFrom
                    mMsg += 'Content-Type: text/plain; charset=utf-8\n\n'                    
                    mMsg += _('Item has been submitted for your review').encode('utf-8','ignore') + '\n'
                    mMsg += _('Please review the submitted content. ').encode('utf-8','ignore') + '\n\n'
                    mMsg += 'Title: %s\n\n' % obj_title
                    mMsg += '%s/view \n\n' % obj_url
                    mMsg += 'The contributor was %s\n\n' % creator_info['fullname']
                    mMsg += 'Email: %s\n\n' % creator_info['email']                    
                    logger.info('notifyReviewersVideoSubmitted , im %s . sending email to %s from %s ' % (self.context, mTo, mFrom) )
                    job = self.async.queueJob(sendMail, self.context, mMsg, mSubj)
                    print "job queued: %s" % job
                except Exception, e:
                    logger.error('Didnt actually send email to reviewer! Something amiss with SecureMailHost. %s' % e)


    def notifyReviewersVideoRejected(self):
        """ Email the reviewers of the rejected video """
        logger = logging.getLogger('plumi.content.adapters')
        #IPlumiVideo implementing objects only
        if IPlumiVideo.providedBy(self.context):
            logger.info('notifyReviewersVideoRejected , im %s ' % self.context )
            obj_title=self.context.Title()
            obj_url=self.context.absolute_url()
            creator = self.context.Creator()
            membr_tool = getToolByName(self.context,'portal_membership')
            member=membr_tool.getMemberById(creator)
            creator_info = {'fullname':member.getProperty('fullname', 'Fullname missing'),
                            'email':member.getProperty('email', None)}

            #search for reviewers 
            reviewers = membr_tool.searchForMembers(roles=['Reviewer'])
            for reviewer in reviewers:
                memberId = reviewer.id
                try:
                    mTo = reviewer.getProperty('email',None)
                    urltool = getToolByName(self.context, 'portal_url')
                    portal = urltool.getPortalObject()
                    mFrom = portal.getProperty('email_from_address')
                    mSubj = '%s -- has been rejected' % obj_title                
                    mMsg = 'To: %s\n' % mTo
                    mMsg += 'From: %s\n' % mFrom
                    mMsg += 'Content-Type: text/plain; charset=utf-8\n\n'                                  
                    mMsg += _('Item has been rejected..').encode('utf-8','ignore') + '\n'
                    mMsg += 'Title: %s\n\n' % obj_title
                    mMsg += '%s/view \n\n' % obj_url
                    mMsg += 'The contributor was %s\n\n' % creator_info['fullname']
                    mMsg += 'Email: %s\n\n' % creator_info['email']
                    logger.info('notifyReviewersVideoRejected , im %s . sending email to %s from %s ' % (self.context, mTo, mFrom) )
                    job = self.async.queueJob(sendMail, self.context, mMsg, mSubj)
                    print "job queued: %s" % job
                except Exception, e:
                    logger.error('Didnt actually send email to reviewer! Something amiss with SecureMailHost. %s' % e)

    def notifyReviewersVideoRetracted(self):
        """ Email the reviewers of the retracted video """
        logger = logging.getLogger('plumi.content.adapters')
        #IPlumiVideo implementing objects only
        if IPlumiVideo.providedBy(self.context):
            logger.info('notifyReviewersVideoRetracted , im %s ' % self.context )
            obj_title=self.context.Title()
            obj_url=self.context.absolute_url()
            creator = self.context.Creator()
            membr_tool = getToolByName(self.context,'portal_membership')
            member=membr_tool.getMemberById(creator)
            creator_info = {'fullname':member.getProperty('fullname', 'Fullname missing'),
                            'email':member.getProperty('email', None)}
            #search for reviewers 
            reviewers = membr_tool.searchForMembers(roles=['Reviewer'])
            for reviewer in reviewers:
                memberId = reviewer.id
                try:
                    mTo = reviewer.getProperty('email',None)
                    urltool = getToolByName(self.context, 'portal_url')
                    portal = urltool.getPortalObject()
                    mFrom = portal.getProperty('email_from_address')
                    mSubj = '%s -- has been retracted' % obj_title                
                    mMsg = 'To: %s\n' % mTo
                    mMsg += 'From: %s\n' % mFrom
                    mMsg += 'Content-Type: text/plain; charset=utf-8\n\n'
                    mMsg += _('Item has been retracted..').encode('utf-8','ignore') + '\n'
                    mMsg += 'Title: %s\n\n' % obj_title
                    mMsg += '%s/view \n\n' % obj_url
                    mMsg += 'The contributor was %s\n\n' % creator_info['fullname']
                    mMsg += 'Email: %s\n\n' % creator_info['email']
                    logger.info('notifyReviewersVideoRetracted , im %s . sending email to %s from %s ' % (self.context, mTo, mFrom) )
                    job = self.async.queueJob(sendMail, self.context, mMsg, mSubj)
                    print "job queued: %s" % job
                except Exception, e:
                    logger.error('Didnt actually send email to reviewer! Something amiss with SecureMailHost. %s' % e)

    def notifyOwnerVideoPublished(self):
        """ Email the owner of the published video """
        logger = logging.getLogger('plumi.content.adapters')
        #IPlumiVideo implementing objects only
        if IPlumiVideo.providedBy(self.context):
            logger.info('notifyOwnerVideoPublished, im %s ' % self.context )
            obj_title=self.context.Title()
            creator=self.context.Creator()
            obj_url=self.context.absolute_url()
            membr_tool = getToolByName(self.context,'portal_membership')
            member=membr_tool.getMemberById(creator)
            if not member:
                logger.error("Didnt actually send email to the author of %s as there doesn't seem to be one" % obj_url)
                return
            mTo = member.getProperty('email',None)
            if mTo is not None and mTo is not '':
                try:
                    mMsg = 'Hi %s \n' % member.getProperty('fullname', 'you')
                    mMsg += _('Your contribution has been accepted for publishing on the site').encode('utf-8','ignore') + '\n'
                    mMsg += 'Title: %s\n\n' % obj_title
                    mMsg += '%s/view \n\n' % obj_url
                    urltool = getToolByName(self.context, 'portal_url')
                    portal = urltool.getPortalObject()
                    mFrom = portal.getProperty('email_from_address')
                    mSubj = 'Your contribution : %s : was published.' % obj_title
                    #send email to object owner
                    logger.info('notifyOwnerVideoPublished , im %s - sending email to %s from %s ' % (self.context, mTo, mFrom) )
                    job = self.async.queueJob(sendMail, self.context, mMsg, mSubj)
                    print "job queued: %s" % job
                except Exception, e:
                    logger.error('Didnt actually send email! Something amiss with SecureMailHost. %s' % e)

    def notifyOwnerVideoRejected(self):
        """ Notify owner that the video is rejected """
        logger = logging.getLogger('plumi.content.adapters')
        #IPlumiVideo implementing objects only
        if IPlumiVideo.providedBy(self.context):
            logger.info('notifyOwnerVideoRejected, im %s ' % self.context )
            obj_title=self.context.Title()
            creator=self.context.Creator()
            obj_url=self.context.absolute_url()
            membr_tool = getToolByName(self.context,'portal_membership')
            member=membr_tool.getMemberById(creator)
            mTo = member.getProperty('email',None)
            if mTo is not None and mTo is not '':
                try:
                    urltool = getToolByName(self.context, 'portal_url')
                    portal = urltool.getPortalObject()
                    mFrom = portal.getProperty('email_from_address')
                    mRej = portal.getProperty('rejected_text',None)            
                    mMsg = 'Hi %s \n' % member.getProperty('fullname', 'you')
                    if mRej:
                        mMsg += mRej
                    else:
                        mMsg += _('Your contribution has been rejected ..').encode('utf-8','ignore') + '\n'
                
                    mMsg += 'Title: %s\n\n' % obj_title
                    mMsg += '%s/view \n\n' % obj_url
                    mSubj = 'Your contribution : %s : was rejected.' % obj_title
                    #send email to object owner
                    logger.info('notifyOwnerVideoRejected , im %s - sending email to %s from %s ' % (self.context, mTo, mFrom) )
                    job = self.async.queueJob(sendMail, self.context, mMsg, mSubj)
                    print "job queued: %s" % job
                except Exception, e:
                    logger.error('Didnt actually send email! Something amiss with SecureMailHost. %s' % e)

    def notifyOwnerVideoRetracted(self):
        """ Notify owner that the video is retracted """
        logger = logging.getLogger('plumi.content.adapters')
        #IPlumiVideo implementing objects only
        if IPlumiVideo.providedBy(self.context):
            logger.info('notifyOwnerVideoRetracted, im %s ' % self.context )
            obj_title=self.context.Title()
            creator=self.context.Creator()
            obj_url=self.context.absolute_url()
            membr_tool = getToolByName(self.context,'portal_membership')
            member=membr_tool.getMemberById(creator)
            mTo = member.getProperty('email',None)
            if mTo is not None and mTo is not '':
                try:
                    mMsg = 'Hi %s \n' % member.getProperty('fullname', 'you')
                    mMsg += _('Your contribution has been retracted ..').encode('utf-8','ignore') + '\n'
                    mMsg += 'Title: %s\n\n' % obj_title
                    mMsg += '%s/view \n\n' % obj_url
                    urltool = getToolByName(self.context, 'portal_url')
                    portal = urltool.getPortalObject()
                    mFrom = portal.getProperty('email_from_address')
                    mSubj = 'Your contribution : %s : was retracted.' % obj_title
                    #send email to object owner
                    logger.info('notifyOwnerVideoRetracted , im %s - sending email to %s from %s ' % (self.context, mTo, mFrom) )
                    job = self.async.queueJob(sendMail, self.context, mMsg, mSubj)
                    print "job queued: %s" % job
                except Exception, e:
                    logger.error('Didnt actually send email! Something amiss with SecureMailHost. %s' % e)

    def autoPublishOrHide(self):
        """ Implement auto publish or hide functionality. Returns TRUE if we submitted for review via workflow tool properly, or FALSE otherwise. """
        logger = logging.getLogger('plumi.content.adapters')
        worked = False
        #IPlumiVideo implementing objects only
        if IPlumiVideo.providedBy(self.context):
            logger.info('autoPublishOrHide , im %s ' % self.context )

            #Conditions XXX
            #check if our requirements are met then auto-submit this video.
            #basically, an attached video

            try:
                workflow = getToolByName(self.context, 'portal_workflow')
                state = workflow.getInfoFor(self.context,'review_state')
                if state == 'private':
                    workflow.doActionFor(self.context, 'show')
                state = workflow.getInfoFor(self.context,'review_state')
                #dont try to resubmit if already published.
                if not state == 'published':
                    workflow.doActionFor(self.context, 'submit')
                    worked = True
            except WorkflowException:
                worked = False
                pass
            #XXX if conditions arent met, hide the video
            # We arent implementing this by default in IPlumiVideo atm

        #return value
        return worked
    
def sendMail(context, msg, subj):
    context.MailHost.send(msg, subject=subj)
    print "mail sent"
