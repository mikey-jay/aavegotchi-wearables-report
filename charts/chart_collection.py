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

class BarGroup:
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
        self._groups = []

    def add_group(self, group: BarGroup):
        self._groups.append(group)

    def get_name(self):
        return self._name

    def get_groups(self):
        return self._groups

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
    def __init__(self, df, category_column_name=None, values_column_name=None, group_by_column_name=None, agg_func=np.sum):
        self._df = df
        self._group_by_column_name = group_by_column_name
        self._category_column_name = category_column_name
        self._values_column_name = values_column_name
        self._agg_func = agg_func

    def build_chart(self, chart_name):
        # aggregate the data
        group_by_columns = [self._category_column_name]

        if self._group_by_column_name:
            group_by_columns.append(self._group_by_column_name)
            
        aggregated_df = self._df.groupby(group_by_columns).agg({self._values_column_name: self._agg_func}).reset_index()

        chart = BarChart(chart_name)

        # If no group_by_column_name is provided, create one group for all bars
        if self._group_by_column_name is None:
            group = BarGroup("Default")
            chart.add_group(group)
            for index, row in aggregated_df.iterrows():
                bar_name = row[self._category_column_name]
                bar_value = row[self._values_column_name]
                bar = Bar(bar_name, bar_value)
                group.add_bar(bar)

        else:
            for index, row in aggregated_df.iterrows():
                group_name = row[self._group_by_column_name]
                bar_name = row[self._category_column_name]
                bar_value = row[self._values_column_name]
                bar = Bar(bar_name, bar_value)

                # Check if group already exists
                group = next((g for g in chart.get_groups() if g.get_name() == group_name), None)
                if group is None:
                    # Create new group if it doesn't exist
                    group = BarGroup(group_name)
                    chart.add_group(group)

                group.add_bar(bar)
        
        return chart

if __name__ == '__main__':
    charts = ChartCollection('Test Charts')
    sample_df = pd.DataFrame({'x': ['1', '2', '3', '4', '5', '1', '2', '3', '4', '5'], 'y': [0.1, 0.2, 0.3, 0.4, 0.5, 0.4, 0.3, 0.2, 0.1, 0.0], 'group': ['A', 'A', 'A', 'A', 'A', 'B', 'B', 'B', 'B', 'B']})
    simple_chart = ChartBuilder(sample_df, category_column_name='x', values_column_name='y', group_by_column_name=None).build_chart('Simple Chart')
    grouped_chart = ChartBuilder(sample_df, category_column_name='x', values_column_name='y', group_by_column_name='group').build_chart('Grouped Chart')

    def print_chart(chart: BarChart):
        print(f'Chart: {chart.get_name()}')
        for group in chart.get_groups():
            group_name = group.get_name()
            for bar in group.get_bars():
                bar_name = bar.get_name()
                bar_value = bar.get_value()
                print(f'{group_name} - {bar_name} - {bar_value}')

    print_chart(simple_chart)
    print_chart(grouped_chart)

    charts.add_chart(simple_chart)
    charts.add_chart(grouped_chart)

    from chart_renderer import ChartRenderer
    renderer = ChartRenderer(charts, chart_type='grouped')
    renderer.render()