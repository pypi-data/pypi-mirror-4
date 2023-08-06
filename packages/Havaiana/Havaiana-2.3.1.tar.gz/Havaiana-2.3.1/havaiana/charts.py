import pygal

from pygal.style import Style

havaiana_style = Style(
    background='#1BA7B4',
    plot_background='#3CB9C6',
    foreground='#ffffff',
    foreground_light='#ffffff',
    foreground_dark='#444444',
    opacity='.6',
    opacity_hover='.9',
    transition='400ms ease-in',
    colors=('#DF6E1E', '#AD1D28', '#4D3A7D', '#48CA38', '#27666D'))

class Chart(object):
    def __init__(self, title):
        self.title = title
        self.chart = None


class LineChart(Chart):
    def __init__(self, title, line_name, width, height):
        Chart.__init__(self, title)
        self.chart = pygal.Line(style=havaiana_style, width=width,
                                height=height, explicit_size=True)
        self.line_name = line_name

    def render(self, data):
        labels, points = self.get_data(data)
        self.chart.title = self.title
        self.chart.x_labels = labels
        self.chart.add(self.line_name, points)
        return self.chart.render(True)
