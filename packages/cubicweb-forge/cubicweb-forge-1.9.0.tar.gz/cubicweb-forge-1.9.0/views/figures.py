"""forge figures views

:organization: Logilab
:copyright: 2006-2009 LOGILAB S.A. (Paris, FRANCE), license is LGPL.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"
_ = unicode

from cubicweb.predicates import is_instance
from cubicweb.view import EntityView
from cubicweb.web.views.plots import FlotPlotWidget

def cumsum(data):
    output = []
    lastsum = 0
    for date, variations in data:
        var = sum(variations)
        lastsum += var
        output.append( (date, lastsum) )
    return output

# ONE_DAY_IN_MS = 1000 * 3600 * 24
#
# def lowpass_filter(data, rc=ONE_DAY_IN_MS * 7):
#     """http://en.wikipedia.org/wiki/Low-pass_filter#Digital_simulation"""
#     output = []
#     lastdate, lastvalue = data[0]
#     for date, value in data[1:]:
#         dt = (datetime2ticks(date) - datetime2ticks(lastdate))
#         alpha =  dt / (rc + dt)
#         lastvalue = lastvalue + alpha * (value - lastvalue)
#         lastdate = date
#         output.append( (date, lastvalue) )
#     return output
#
# def compute_trend(todo_loads):
#     trend = lowpass_filter(todo_loads)
#     slope = (trend[-1][1] - trend[-2][1]) / (datetime2ticks(trend[-1][0]) - datetime2ticks(trend[-2][0]))
#     if slope < -ONE_DAY_IN_MS:
#         eta = datetime.fromtimestamp(datetime2ticks(trend[-1][0]) + trend[-1][1] / slope / 1000)
#         trend.append( (eta, 0) )
#     return trend

class TicketBurndownView(EntityView):
    __regid__ = "burndown_chart"
    __select__ = is_instance('Ticket')
    title = _('burn down chart')

    def build_plot_data(self):
        """compute the total loads and remaining loads for all the
        ticket state transition dates.

        Return the list of dates to be plotted, and the list of points
        """
        total_loads = {}
        todo_loads = {}
        for ticket in self.cw_rset.entities():
            history = ticket.state_history()
            creation_date = history[0][0]
            load = ticket.corrected_load()
            total_loads.setdefault(creation_date, []).append(load)
            for date, is_open in history:
                todo_loads.setdefault(date, []).append(is_open and load or -load)
        plots = [cumsum(sorted(todo_loads.items())),
                 cumsum(sorted(total_loads.items()))]
        # plots.insert(0, compute_trend(plots[0]))
        return plots


    def call(self, start=None, end=None, width=None, height=None):
        form = self._cw.form
        width = width or form.get('width', 500)
        height = height or form.get('height', 400)
        plotwidget = FlotPlotWidget(['todo', 'total'], self.build_plot_data(),
                                    timemode=True)
        plotwidget.render(self._cw, width, height, w=self.w)
