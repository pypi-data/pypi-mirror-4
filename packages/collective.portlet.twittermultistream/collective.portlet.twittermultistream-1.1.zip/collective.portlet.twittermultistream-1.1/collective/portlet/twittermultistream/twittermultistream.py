import logging
import json
import urllib
import time
import datetime

from zope import schema
from zope import interface
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.memoize import ram
from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from collective.portlet.twittermultistream import messageFactory as _

logger = logging.getLogger('collective.portlet.twittermultistream')


class ITwitterMultiStream(IPortletDataProvider):
    """A portlet which display last tweet from each account"""

    header = schema.TextLine(title=_(u"Header"))
    accounts = schema.List(title=_(u"Accounts"),
                   value_type=schema.ASCIILine(title=_(u"Twitter account")))
    timeout = schema.Int(title=_(u'Feed reload timeout'),
                        description=_(u'Time in minutes after which the feed should be reloaded.'),
                        required=True,
                        default=100)


class Assignment(base.Assignment):
    """Portlet assignment."""

    interface.implements(ITwitterMultiStream)

    def __init__(self, header=None, accounts=None, timeout=100):
        self.header = header
        self.accounts = accounts
        self.timeout = timeout

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return "TwitterMultiStream: %s" % self.header


def _get_tweets_cachekey(method, self):
    return ('-'.join(self.data.accounts), time.time() // (60 * 60))


class Renderer(base.Renderer):
    """Portlet renderer"""

    render = ViewPageTemplateFile('twittermultistream.pt')

    @ram.cache(_get_tweets_cachekey)
    def get_tweets(self):
        tweets = []
        accounts = self.data.accounts
        get_url = "https://twitter.com/users/%s.json"
        for account in accounts:
            account_url = get_url % account
            account_info = None
            try:
                account_info = json.loads(urllib.urlopen(account_url).read())
                if "errors" in account_info:
                    continue
                if 'status' in account_info:
                    self.update_time(account_info)
                #we keep all information
                tweets.append(account_info)
            except IOError:
                continue
            # the tweet text is in account_info['status']['text']
        return tweets

    def update_time(self, tweet):
        time_format = '%a %b %d %H:%M:%S +0000 %Y'
        created_at = tweet['status']['created_at']
        created_at_dt = datetime.datetime.strptime(created_at, time_format)
        tweet['status']['created_at_datetime'] = created_at_dt.strftime('%Y-%m-%dT%H:%M:%SZ')
        return tweet


class AddForm(base.AddForm):
    """Portlet add form."""
    form_fields = form.Fields(ITwitterMultiStream)

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):
    """Portlet edit form."""
    form_fields = form.Fields(ITwitterMultiStream)
