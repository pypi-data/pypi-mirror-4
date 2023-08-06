"""views for Project entities

:organization: Logilab
:copyright: 2006-2011 LOGILAB S.A. (Paris, FRANCE), license is LGPL.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"
_ = unicode

from logilab.common.decorators import monkeypatch

from cubicweb.predicates import is_instance
from cubicweb.view import EntityView
from cubicweb.web import uicfg
from cubicweb.web.views import baseviews, tableview

from cubes.tracker.views import fixed_orderby_rql, version as tracker


_pvs = uicfg.primaryview_section
for attr in ('progress_target', 'progress_done', 'progress_todo'):
    _pvs.tag_attribute(('Version', attr), 'hidden')

tracker.VersionPrimaryView.tabs.append(_('forge.version.burndown_tab'))

idx = tracker.VersionTicketsTable.columns.index('in_state')
tracker.VersionTicketsTable.columns.insert(idx+1, 'load')
tracker.VersionTicketsTable.columns.insert(idx+2, 'load_left')
tracker.VersionTicketsTable.columns.append('tags')
tracker.VersionTicketsTable.column_renderers['tags'] = tableview.RelationColRenderer(role='object')

@monkeypatch(tracker.VersionPrimaryTab)
def tickets_rql(self):
    # prefetch everything we can for optimization
    return ('Any T,TTI,TT,TP,TD,TDF,TCD,TMD,TL,TLL,S,SN %s WHERE '
            'T title TTI, T type TT, T priority TP, '
            'T description TD, T description_format TDF, '
            'T creation_date TCD, T modification_date TMD, '
            'T load TL, T load_left TLL, '
            'T in_state S, S name SN, '
            'T %s V, V eid %%(x)s'
            % (fixed_orderby_rql(self.SORT_DEFS), self.TICKETS_RELATION))


class VersionProgressTableView(tracker.VersionProgressTableView):
    column_renderers = tracker.VersionProgressTableView.column_renderers.copy()
    column_renderers['cost'] = column_renderers['cost'].copy()
    column_renderers['cost'].header = _('load')


# we don't want IDownloadable oneline view for version
class VersionOneLineView(baseviews.OneLineView):
    __select__ = is_instance('Version')


class VersionBurndownChartTab(EntityView):
    __regid__ = 'forge.version.burndown_tab'
    __select__ = EntityView.__select__ & is_instance('Version')
    rql = ('Any X,CD,L,LL WHERE X load L, X load_left LL, '
           'X creation_date CD, X done_in V, V eid %(x)s')

    def cell_call(self, row, col, view=None):
        version = self.cw_rset.entities().next()
        alt = self._cw._('Burn Down Chart')
        self.w('<h3>%s</h3>' % alt)
        # the following rql is useful to detect ticket created directly in a
        # done state (validation pending, resolved, deprecated or rejected). In
        # this case, graph is probably wrong.
        ticketcls = self._cw.vreg['etypes'].etype_class('Ticket')
        rset = self._cw.execute(
            'Any T GROUPBY T  WHERE T done_in V, V eid %%(v)s, '
            'T in_state S, NOT S name IN (%s), TR wf_info_for T '
            'HAVING COUNT(TR)=0' % ','.join('"%s"' % st for st in ticketcls.OPEN_STATES),
           {'v': version.eid})
        if rset:
            self.w(u'<div class="needsvalidation">%s</div>'
                   % self._cw._("Some tickets don't have a regular workflow, "
                                "the graph may be wrong."))
        tickets_rset = self._cw.execute(self.rql, {'x': self.cw_rset[row][col]})
        if tickets_rset:
            self.wview('burndown_chart', tickets_rset, width=800, height=500)


def registration_callback(vreg):
    vreg.register_all(globals().values(), __name__, (VersionProgressTableView,))
    vreg.register_and_replace(VersionProgressTableView,
                              tracker.VersionProgressTableView)
