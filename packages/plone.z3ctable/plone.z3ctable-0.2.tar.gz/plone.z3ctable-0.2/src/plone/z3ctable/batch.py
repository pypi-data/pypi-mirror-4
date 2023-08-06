from z3c.table import batch
from ZTUtils import make_query
from ZTUtils import url_query
from zope.i18n import translate

try:
    from plone.batching.utils import calculate_pagerange, calculate_pagenumber
    calculate_pagerange
    calculate_pagenumber
except ImportError:
    from Products.CMFPlone.PloneBatch import calculate_pagenumber
    from Products.CMFPlone.PloneBatch import calculate_pagerange

from Products.CMFPlone import PloneMessageFactory as _


LINK = '<a href="%(url)s">%(label)s</a>'


class PloneBatch(object):

    def __init__(self, batch, pagerange=7):
        self.batch = batch

        # Set up the total number of pages
        self.numpages = calculate_pagenumber(len(self.batch.sequence),
                                             self.batch.size)

        # Set up the current page number
        self.pagenumber = calculate_pagenumber(self.batch.start + 1,
                                               self.batch.size)

        # Set up pagerange for the navigation quick links
        self.pagerange, self.pagerangestart, self.pagerangeend = (
            calculate_pagerange(self.pagenumber, self.numpages, pagerange))

        # Set up the lists for the navigation: 4 5 [6] 7 8
        #  navlist is the complete list, including pagenumber
        #  prevlist is the 4 5 in the example above
        #  nextlist is 7 8 in the example above
        self.navlist = self.prevlist = self.nextlist = []
        if self.pagerange and self.numpages >= 1:
            self.navlist = range(self.pagerangestart, self.pagerangeend)
            self.prevlist = range(self.pagerangestart, self.pagenumber)
            self.nextlist = range(self.pagenumber + 1, self.pagerangeend)

    @property
    def showfirst(self):
        return not 1 in self.navlist

    @property
    def dotsafterfirst(self):
        return not 2 in self.navlist

    @property
    def dotsbeforelast(self):
        return not self.batch.total - 1 in self.navlist

    @property
    def showlast(self):
        return not self.batch.total in self.navlist


class BatchProvider(batch.BatchProvider):

    def update(self):
        self.plonebatch = PloneBatch(self.batch)

    def render(self):
        results = []

        header = u'<div class="listingBar">'
        results.append(header)

        results.extend(self.previousItemsLink())
        results.extend(self.nextItemsLink())
        results.extend(self.firstLink())
        results.extend(self.previousLinks())
        results.extend(self.current())
        results.extend(self.nextLinks())
        results.extend(self.lastLink())

        footer = u'</div>'
        results.append(footer)
        return u'\n'.join(results)

    def previousItemsLink(self):
        result = []
        if self.batch.previous:
            result.append('<span class="previous">')
            index = self.batch.index - 1
            numberitems = len(self.batches[index])
            label = '&laquo; '
            messageid = _(u'batch_previous_x_items',
                          default=u'Previous ${number} items',
                          mapping=dict(number=unicode(numberitems)))
            label += translate(messageid, context=self.request)
            url = self.makeUrl(index)
            link = self.makeLink(url, label)
            result.append(link)
            result.append('</span>')
        return result

    def nextItemsLink(self):
        result = []
        if self.batch.next:
            result.append('<span class="next">')
            index = self.batch.index + 1
            numberitems = len(self.batches[index])
            messageid = _(u'batch_next_x_items',
                          default=u'Next ${number} items',
                          mapping=dict(number=unicode(numberitems)))
            label = translate(messageid, context=self.request)
            label += ' &raquo;'
            url = self.makeUrl(index)
            link = self.makeLink(url, label)
            result.append(link)
            result.append('</span>')
        return result

    def makeLink(self, url, label):
        return LINK % dict(url=url, label=label)

    def makeUrl(self, index):
        batch = self.batches[index]
        query = {self.table.prefix + '-batchStart': batch.start,
                 self.table.prefix + '-batchSize': batch.size}
        querystring = make_query(query)
        base = url_query(self.request, omit=query.keys())
        return '%s&%s' % (base, querystring)

    def firstLink(self):
        result = []
        if self.plonebatch.showfirst:
            result.append(u'<span>')
            url = self.makeUrl(0)
            label = '1'
            result.append(self.makeLink(url, label))
            if self.plonebatch.dotsafterfirst:
                result.append(u'...')
            result.append(u'</span>')
        return result

    def previousLinks(self):
        result = []
        for number in self.plonebatch.prevlist:
            url = self.makeUrl(number - 1)
            label = str(number)
            result.append(self.makeLink(url, label))
        return result

    def current(self):
        return ['[%s]' % self.batch.number]

    def nextLinks(self):
        result = []
        for number in self.plonebatch.nextlist:
            url = self.makeUrl(number - 1)
            label = str(number)
            result.append(self.makeLink(url, label))
        return result

    def lastLink(self):
        result = []
        if self.plonebatch.showlast:
            result.append(u'<span>')
            if self.plonebatch.dotsbeforelast:
                result.append(u'...')
            url = self.makeUrl(self.batch.total - 1)
            label = str(self.batch.total)
            result.append(self.makeLink(url, label))
            result.append(u'</span>')
        return result
