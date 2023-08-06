import datetime
import time
import random
from mustachebox.backends import BaseBackend


def time_serie(**kwargs):
    """
    Render a time serie
    """
    resp = {2004: ['2004'],
            2005: ['2005'],
            2006: ['2006'],
            2007: ['2007']}

    for i in range(2):
        for k, v in resp.iteritems():
            v.append(int((random.random() * random.random()) * 10000))
        resp['label'] = ['year', 'sales', 'expenses']
    return resp


class Backend(BaseBackend):
    """
    A backend get data formated as mustache need them.
    - data : contain the data to be printed as graph
    - name : the graph name
    - template_name: the template to use for rendering
    """

    def area(self, **kwargs):
        """
        Render a graph area using google chart.

        The data are formated as follow ::

            {
                2004: ['2004', 7160, 546],
                2005: ['2005', 5654, 5435],
                2006: ['2006', 7656, 6545],
                2007: ['2007', 5435, 6545],
                'label': ['year', 'sales', 'expenses']
            }
        """
        self.template = 'area'
        return time_serie(**kwargs)

    def bar_chart(self, **kwargs):
        """
        Render a barchart graph using google chart.

        The data are formated as follow ::

            {
                2004: ['2004', 7160, 546],
                2005: ['2005', 5654, 5435],
                2006: ['2006', 7656, 6545],
                2007: ['2007', 5435, 6545],
                'label': ['year', 'sales', 'expenses']
            }
        """
        self.template = "barchart"
        return time_serie(**kwargs)

    def column_chart(self, **kwargs):
        """
        Render a barchart graph using google chart.

        The data are formated as follow ::

            {
                2004: ['2004', 7160, 546],
                2005: ['2005', 5654, 5435],
                2006: ['2006', 7656, 6545],
                2007: ['2007', 5435, 6545],
                'label': ['year', 'sales', 'expenses']
            }
        """
        self.template = 'columnchart'
        return time_serie(**kwargs)

    def pie_chart(self, **kwargs):
        """
        Define a generic pie chart using google chart

        The data are formated as follow::

            {'label': ['name', 'count'],
             'records': [
                             ['eat': 12],
                             ['read': 5],
                             ['work': 23],
                             ['sleep': 4],
                             ['wathc TV': 10]
                           ]
            }
        """
        self.template = "pie_chart"

        label = ['name', 'count']
        activities = []
        words = ['eat', 'read', 'work', 'sleep', 'watch TV']
        for elem in words:
            activities.append([elem, int(random.random() * 10)])

        return {'label': label, 'records': activities}

    def line_chart(self, **kwargs):
        """
        Define a generic line chart using D3js

        Data are formated as follow ::

            [
              {'date': 1107151200000,
               'value': 289
              },
              {'date': 1109743200000,
               'value': 766
              }
               <...>
            ]
        """
        response = []
        self.template = "line_chart"
        date = datetime.datetime(2005, 1, 1, 0, 0, 0)
        for i in range(1500):
            date += datetime.timedelta(days=2)
            response.append({
                'date': time.mktime(date.timetuple()) * 1000,
                'value': (i * 10) + int(random.random() * 1000)})
        return response

    def multiserie_linechart(self, **kwargs):
        """
        Define a multi-line graph using D3js

        data are formated as follow ::

            [
              {'date': 1109743200000,
              'value': 453,
              'serie': "serie1"
              },
              {'date': 1107151200000,
               'value': 435,
               'serie': "serie2",
              },
              ...
            ]
        """
        self.template = "multiline_chart"
        response = []
        for a in range(3):  # we render a 3 series chart
            date = datetime.datetime(2005, 1, 1, 0, 0, 0)
            for i in range(200):
                if a % 3 == 0:
                    mult = -10
                elif a % 2 == 0:
                    mult = 1
                else:
                    mult = 10
                date += datetime.timedelta(days=2)
                response.append({
                    'date': time.mktime(date.timetuple()) * 1000,
                    'value': (i * mult) + int(random.random() * 1000),
                    'serie': a})
        return response
