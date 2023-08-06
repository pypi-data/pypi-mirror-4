"""Integration with eea.daviz
"""

from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from persistent.mapping import PersistentMapping
from zc.dict import OrderedDict
from zope.annotation.interfaces import IAnnotations
from zope.component import getMultiAdapter
import logging

logger = logging.getLogger("eea.indicators")


class SetDavizChart(BrowserView):
    """Edit the chart for a daviz presentation that's set as related

    We store the charts in an annotation on the context object;
    This annotation is an OrderedDict, where the keys are the UIDs
    of the daviz objects; As values we have OrderedDicts of
    chart_id:type_of_embed, where type_of_embed is either "live" or "preview"
    """

    def __call__(self):
        """info is a dict of uid:[list of chart ids] values
        """
        form = self.request.form
        uid = form.get("daviz_uid", "").strip()

        #this is a string like: 'chart_1=preview&chart_2=live'
        #from urlparse import parse_qs
        #cannot use parse_qs because it doesn't guarantee order
        req_charts = form.get("charts", "").strip()
        charts = []

        for pair in req_charts.split("&"):
            if pair:
                chart_id, embed = pair.split("=")
                charts.append((chart_id, embed))

        obj = self.context
        annot = IAnnotations(obj)

        if not 'DAVIZ_CHARTS' in annot:
            annot['DAVIZ_CHARTS'] = PersistentMapping()

        info = annot['DAVIZ_CHARTS'].get(uid)
        if not info:
            info = annot['DAVIZ_CHARTS'][uid] = OrderedDict()

        info.clear()
        info.update(charts)

        return "OK"


class GetDavizChart(BrowserView):
    """Get the chart for a daviz presentation that's set as related
    """

    def __call__(self):
        """Not usable standalone so we return self
        """
        return self

    def get_charts(self, uid):
        """return daviz charts as a dict of {chart_id:"preview|live"}
        """
        info = self.get_daviz().get(uid)
        if info:
            return info[1]  #only the charts
        return []

    def get_daviz(self):
        """Given an object, it will return the daviz+charts assigned

        It returns a mapping of
        <daviz uid A>:
            [daviz, (chart_id, chart title, embed_type, fallback_image)],
        <daviz uid B>:
            [daviz, (chart_id, chart title, embed_type, fallback_image)],
        """
        annot = IAnnotations(self.context).get('DAVIZ_CHARTS', {})

        uids_cat = getToolByName(self.context, 'uid_catalog')
        info = {}
        for uid in annot.keys():
            brains = uids_cat.searchResults(UID=uid)
            if not brains:
                logger.warning("Couldn't find visualization with UID %s" % uid)
                continue
            daviz = brains[0].getObject()
            tabs = getMultiAdapter((daviz, self.request),
                                   name="daviz-view.html").tabs

            annot_info = annot.get(uid, {})
            charts = []

            for chart_id in annot_info.keys():
                for tab in tabs:
                    if tab['name'] == chart_id:
                        #code = None #for the future, needs api in daviz
                        embed_type = annot_info[chart_id]
                        charts.append((chart_id, tab['title'], embed_type,
                                       tab['fallback-image']))
            info[uid] = (daviz, charts)

        return info


