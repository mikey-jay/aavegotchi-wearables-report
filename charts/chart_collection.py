from typing import List
import pandas as pd
import numpy as np

class Bar:
    def __init__(self, name, value):
        self._name = name
        self._value = value

    def get_name(self):
        return self._name

    def get_value(self):
        return self._value

class BarSeries:
    def __init__(self, name):
        self._name = name
        self._bars = []

    def add_bar(self, bar: Bar):
        self._bars.append(bar)

    def get_name(self):
        return self._name

    def get_bars(self):
        return self._bars

class BarChart:
    def __init__(self, name):
        self._name = name
        self._series = []

    def add_series(self, series: BarSeries):
        self._series.append(series)

    def get_name(self):
        return self._name

    def get_series(self):
        return self._series

class ChartCollection:
    def __init__(self, name):
        self._name = name
        self._charts = []

    def add_chart(self, chart: BarChart):
        self._charts.append(chart)

    def get_name(self):
        return self._name

    def get_charts(self):
        return self._charts
    
class ChartBuilder:
    def __init__(self, df, category_column_name=None, values_column_name=None, series_column_name=None, agg_func=np.sum):
        self._df = df
        self._series_column_name = series_column_name
        self._category_column_name = category_column_name
        self._values_column_name = values_column_name
        self._agg_func = agg_func

    def build_chart(self, chart_name):
        # aggregate the data
        series_columns = [self._category_column_name]

        if self._series_column_name:
            series_columns.append(self._series_column_name)
            
        aggregated_df = self._df.groupby(series_columns).agg({self._values_column_name: self._agg_func}).reset_index()

        chart = BarChart(chart_name)

        # If no series_column_name is provided, create one series for all bars
        if self._series_column_name is None:
            series = BarSeries("Default")
            chart.add_series(series)
            for index, row in aggregated_df.iterrows():
                bar_name = row[self._category_column_name]
                bar_value = row[self._values_column_name]
                bar = Bar(bar_name, bar_value)
                series.add_bar(bar)

        else:
            for index, row in aggregated_df.iterrows():
                series_name = row[self._series_column_name]
                bar_name = row[self._category_column_name]
                bar_value = row[self._values_column_name]
                bar = Bar(bar_name, bar_value)

                # Check if series already exists
                series = next((g for g in chart.get_series() if g.get_name() == series_name), None)
                if series is None:
                    # Create new series if it doesn't exist
                    series = BarSeries(series_name)
                    chart.add_series(series)

                series.add_bar(bar)
        
        return chart

if __name__ == '__main__':
    charts = ChartCollection('Test Charts')
    sample_df = pd.DataFrame({'x': ['1', '2', '3', '4', '5', '1', '2', '3', '4', '5'], 'y': [0.1, 0.2, 0.3, 0.4, 0.5, 0.4, 0.3, 0.2, 0.1, 0.0], 'series': ['A', 'A', 'A', 'A', 'A', 'B', 'B', 'B', 'B', 'B']})
    simple_chart = ChartBuilder(sample_df, category_column_name='x', values_column_name='y', series_column_name=None).build_chart('Simple Chart')
    grouped_chart = ChartBuilder(sample_df, category_column_name='x', values_column_name='y', series_column_name='series').build_chart('Grouped Chart')

    charts.add_chart(simple_chart)
    charts.add_chart(grouped_chart)

    from chart_renderer import ChartRenderer
    renderer = ChartRenderer(charts, chart_type='grouped_bar')
    renderer.render()