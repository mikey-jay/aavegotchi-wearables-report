import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

class GroupedBarChart:

    def __init__(self, df, x_column_name, y_column_name, series_column_name, series_colors):

        x_group_names = df[x_column_name].unique()
        series_names = df[series_column_name].unique()

        self._bar_containers = []

        # Set up plot
        self._fig, self._ax = plt.subplots()
        self._fig.set_size_inches(12,6)
        width = 0.8 / len(series_names)  # Width of each bar
        border_color = 'white'

        for series_index, series in enumerate(series_names):
            series_data = df[df[series_column_name] == series]
            bar_positions_x = np.arange(len(x_group_names)) + series_index * width
            for group_index, group in enumerate(x_group_names):
                group_data = series_data[series_data[x_column_name] == group]
                y_values = group_data[y_column_name]
                bars = self._ax.bar(bar_positions_x[group_index], y_values, width, color=series_colors[series], edgecolor=border_color)
                self._bar_containers.append(bars)
                
        # Set x-axis and y-axis labels and ticks
        self._ax.set_xlabel(x_column_name)
        self._ax.set_ylabel(y_column_name)
        self._ax.set_xticks(np.arange(len(x_group_names)) + 0.4)
        self._ax.set_xticklabels(x_group_names)

        # Create legend for series
        legend_handles = [plt.Rectangle((0,0),1,1, color=series_colors[series], edgecolor=border_color) for series in series_names]
        self._ax.legend(legend_handles, series_names)
    
    def annotate_bars(self, annotation_format='{:,.0f}', rotation=0):
        for bar_containers in self._bar_containers:
            for bar in bar_containers:
                height = bar.get_height()
                self._ax.annotate(annotation_format.format(height),
                xy=(bar.get_x() + bar.get_width() / 2, height + bar.get_y()),
                xytext=(0, 3), # 3 points vertical offset
                textcoords="offset points",
                ha='center', va='bottom', rotation=rotation)

    def set_title(self, title):
        return self._ax.set_title(title)

    def set_tick_params(self, **args):
        return self._ax.tick_params(**args)       

    def show(self):
        self._fig.show()

if __name__ == '__main__':
    matplotlib.use('TkAgg')
    sample_df = pd.DataFrame({'x': ['1', '2', '3', '4', '5', '1', '2', '3', '4', '5'], 'y': [0.1, 0.2, 0.3, 0.4, 0.5, 0.4, 0.3, 0.2, 0.1, 0.0], 'series': ['A', 'A', 'A', 'A', 'A', 'B', 'B', 'B', 'B', 'B']})
    series_colors = {'A': 'red', 'B': 'blue'}
    chart = GroupedBarChart(sample_df, 'x', 'y', 'series', series_colors)
    chart.annotate_bars('{:,.1f}')
    chart.show()
    input("Press enter to close the chart...")
