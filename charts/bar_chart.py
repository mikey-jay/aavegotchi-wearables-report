import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from typing import List
from matplotlib.figure import Figure

class BarChartCategory:
    """
    Class to hold values and metadata for a category of a bar chart.
    """

    def __init__(self, name, values):
        self._name = name
        self._values = values

    def get_values(self):
        return self._values
    
    def get_name(self):
        return self._name
    
class BarChartDataManager:
    """
    Class to perform data aggregation for a bar chart.
    """

    def __init__(self, df: pd.DataFrame, category_column_name: str, values_column_name: str, aggregator=np.sum):
        self._df = pd.DataFrame(df)
        self._category_column_name = category_column_name
        self._values_column_name = values_column_name
        self._aggregator = aggregator

    def get_categories(self) -> List[BarChartCategory]:
        aggregated_df = self._get_aggregated_dataframe()
        categories = []
        for category_name, aggregated_values in list(zip(aggregated_df[self._category_column_name], aggregated_df[self._values_column_name])):
            categories.append(BarChartCategory(category_name, aggregated_values))
        return categories

    def _get_aggregated_dataframe(self, df: pd.DataFrame=None, group_by_column_name: str=None, values_column_name: str=None, aggregator=None) -> BarChartCategoryGroup:
        if df is None:
            df = self._df
        if group_by_column_name is None:
            group_by_column_name = self._category_column_name
        if values_column_name is None:
            values_column_name = self._values_column_name
        if aggregator is None:
            aggregator = self._aggregator
        aggregated_groups = df[group_by_column_name].unique()
        aggregated_values = []
        for group in aggregated_groups:
            aggregated_values.append(aggregator(df[df[group_by_column_name] == group][values_column_name]))
        aggregated_df = pd.DataFrame({ group_by_column_name: aggregated_groups, values_column_name: aggregated_values })
        return aggregated_df

    def _get_values_for_column(self, column_name) -> pd.Series:
        return self._df[column_name]
    
    def _get_values_for_column_unique(self, column_name) -> pd.Series:
        return self._get_values_for_column(column_name).unique()

class BarChart:
    """
    Class to hold information about a bar chart.
    """    
    def __init__(self, data_manager: BarChartDataManager, title=None):
        self._data_manager = data_manager
        self._title = title

    def get_categories(self) -> List[BarChartCategory]:
        return self._data_manager.get_categories()
    
    def get_title(self):
        return self._title

class BarChartDisplayHandler:
    """
    Class to display bar charts using pyplot.
    """
    def __init__(self):
        # set vertical spacing between charts
        self._hspace = 0.5
        pass

    def display_charts(self, charts: List[BarChart]):
        fig, axes = plt.subplots(len(charts), 1)
        fig.subplots_adjust(hspace=self._hspace)
        for i, chart in enumerate(charts):
            ax: plt.Axes = axes[i]
            ax.set_title(chart.get_title())
            ax.set_adjustable
            for category in chart.get_categories():
                ax.bar(category.get_name(), category.get_values())
        fig.show()

class BarChartManager:
    """
    Class to orchestrate the creation and display of bar charts.
    """
    def __init__(self):
        self._charts = []
    
    def add_chart(self, df: pd.DataFrame, category_column_name: str, values_column_name: str, aggregator=np.sum, title=None):
        data_manager = BarChartDataManager(df, category_column_name, values_column_name, aggregator)
        chart = BarChart(data_manager, title=title)
        self._charts.append(chart)

    def display_all_charts(self):
        display_handler = BarChartDisplayHandler()
        display_handler.display_charts(self._charts)

if __name__ == '__main__':
    sample_df = pd.DataFrame({'x': ['1', '2', '3', '4', '5', '1', '2', '3', '4', '5'], 'y': [0.1, 0.2, 0.3, 0.4, 0.5, 0.4, 0.3, 0.2, 0.1, 0.0], 'group': ['A', 'A', 'A', 'A', 'A', 'B', 'B', 'B', 'B', 'B']})
    chart_manager = BarChartManager()
    chart_manager.add_chart(sample_df, 'x', 'y', title='Simple Chart 1')
    chart_manager.add_chart(sample_df, 'x', 'y', title='Simple Chart 2')
    chart_manager.display_all_charts()
    input("Press enter to close the chart...")