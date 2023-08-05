from plone.app.portlets.portlets import calendar
from Products.SimpleCalendarPortlet import SimpleCalendarPortletMessageFactory as _
from zope import schema
from zope.interface import implements
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class ISimpleCalendarPortlet(calendar.ICalendarPortlet):
    "A portlet that integrates with the SimpleCalendar."""

    title = schema.TextLine(title=_(u"title_title",
                                default=_(u"Portlet title")),
                        required=True,
                        default=_(u"Calendar"))

    calendar = schema.Tuple(title=_(u"Calendar"),
                         description=_(u"Select the calendar to get events from and link to."),
                         required=True,
                         value_type=schema.Choice(
                             vocabulary="Products.SimpleCalendarPortlet.vocabularies.SimpleCalendarVocabularyFactory")
                         )

class Assignment(calendar.Assignment):
    "Handles data managed through portlet editing."

    implements(ISimpleCalendarPortlet)

    title = "Calendar"
    calendar = None

    def __init__(self, title=None, calendar=None):
        if title is not None: self.title = title
        if calendar is not None: self.calendar = calendar

from plone.memoize.compress import xhtml_compress
from Acquisition import aq_inner
from zope.component import getMultiAdapter
from DateTime import DateTime

class Renderer(calendar.Renderer):

    _template = ViewPageTemplateFile('SimpleCalendar_calendar.pt')
    updated = False

    def render(self):
        return xhtml_compress(self._template())

    def getEventsForCalendar(self):
        context = aq_inner(self.context)
        year = self.year
        month = self.month
        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        navigation_root_path = portal_state.navigation_root_path()
        try:
            calendar = self.context.portal_catalog(UID=self.data.calendar)[0].getObject()
        except IndexError:
            # Oops, object has gone missing
            calendar = None
        try:
            #calendaring_root = calendar.getParentNode()
            review_state = calendar.getItem_states()
        except AttributeError:
            #calendaring_root = None
            review_state = None
        if not review_state:
            review_state = ('published',)
        weeks = self.calendar.getEventsForCalendar(month, year,
                                                   #path shouldn't be set now
                                                   #path='/'.join(calendar_root.getPhysicalPath()),
                                                   review_state=review_state)
        for week in weeks:
            for day in week:
                daynumber = day['day']
                if daynumber == 0:
                    continue
                day['is_today'] = self.isToday(daynumber)
                if day['event']:
                    cur_date = DateTime(year, month, daynumber)
                    localized_date = [self._ts.ulocalized_time(cur_date, context=context, request=self.request)]
                    day['eventstring'] = '\n'.join(localized_date+[' %s' %
                        self.getEventString(e) for e in day['eventslist']])
                    day['date_string'] = '%s-%s-%s' % (year, month, daynumber)
        return weeks        

from plone.app.portlets.portlets import base
from zope.formlib.form import Fields

   
class AddForm(calendar.AddForm):
    form_fields = Fields(ISimpleCalendarPortlet)
    label = _(u"Add SimpleCalendar portlet")
    description = _(u"This portlet shows events from SimpleCalendar")

    def create(self):
        return Assignment(title=data.get("title"), calendar=data.get("calendar"))

class EditForm(base.EditForm):
    form_fields = Fields(ISimpleCalendarPortlet)
    label = _(u"Add SimpleCalendar portlet")
    description = _(u"This portlet shows events from SimpleCalendar")
