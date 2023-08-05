from django.core import urlresolvers
from django.template.defaultfilters import slugify, truncatewords

from billy.core import mdb as db, settings
from .base import Document
from .metadata import Metadata


class Event(Document):

    collection = db.events

    @property
    def metadata(self):
        return Metadata.get_object(self[settings.LEVEL_FIELD])

    def bills(self):
        bills = []
        for bill in self['related_bills']:
            if 'bill_id' in bill:
                bills.append(bill['bill_id'])
        return db.bills.find({"_id": {"$in": bills}})

    def committees(self):
        committees = []
        for committee in self['participants']:
            if 'committee_id' in committee:
                committees.append(committee['committee_id'])
        return db.committees.find({"_id": {"$in": committees}})

    def get_absolute_url(self):
        slug = slugify(truncatewords(self['description'], 10))
        url = urlresolvers.reverse('event', args=[self[settings.LEVEL_FIELD],
                                                  self['_id']])
        return '%s%s/' % (url, slug)
