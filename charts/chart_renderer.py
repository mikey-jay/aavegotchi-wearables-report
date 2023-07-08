import matplotlib.pyplot as plt
import numpy as np

class ChartRenderer:
    def __init__(self, chart_collection, chart_type='grouped_bar', colors=None, sort_func=None):
        self._charts = chart_collection
        self.bar_width = 0.8
        self.chart_type = chart_type
        self.colors = colors
        self.sort_func = sort_func if sort_func else sorted

    def _get_data_to_plot(self, chart):
        # Extract data from chart in a form that can be easily plotted
        names = []
        values = []
        labels = []
        for series in chart.get_series():
            for bar in series.get_bars():
                names.append(bar.get_name())
                values.append(bar.get_value())
                labels.append(series.get_name())
        return names, values, labels

    def _plot_grouped_bars(self, ax, names, values, labels, color_mapping):
        # Plot bars side by side
        name_set = self.sort_func(list(set(names)))
        label_set = self.sort_func(list(set(labels)))
        bar_width = self.bar_width / len(label_set)
        for i, label in enumerate(label_set):
            x = [name_set.index(name) + i * bar_width for name, lbl in zip(names, labels) if lbl == label]
            y = [value for value, lbl in zip(values, labels) if lbl == label]
            ax.bar(x, y, color=color_mapping[label], width=bar_width, label=label)

    def _plot_stacked_bars(self, ax, names, values, labels, color_mapping):
        # Plot stacked bars
        name_set = self.sort_func(list(set(names)))
        label_set = self.sort_func(list(set(labels)))
        bottom = np.zeros(len(name_set))
        for label in label_set:
            y = np.array([value for name, value, lbl in zip(names, values, labels) if lbl == label and name in name_set])
            ax.bar(name_set, y, bottom=bottom, color=color_mapping[label], label=label)
            bottom += y

    def _get_default_colors(self, count):
        # Generate colors dynamically based on number of unique labels
        cmap = plt.get_cmap('hsv')
        return [cmap(i) for i in np.linspace(0, 0.8, count)]

    def render(self):
        num_charts = len(self._charts.get_charts())
        fig, axs = plt.subplots(num_charts, figsize=(12, 6 * num_charts))
        if len(self._charts.get_charts()) == 1:
            axs = [axs]
        for i, chart in enumerate(self._charts.get_charts()):
            ax = axs[i]
            names, values, labels = self._get_data_to_plot(chart)
            series_count = len(set(labels))
            if self.colors is None:
                chart_colors = self._get_default_colors(series_count)
            else:
                chart_colors = self.colors
            color_mapping = {label: color for label, color in zip(sorted(list(set(labels))), chart_colors)}
            if self.chart_type == "grouped_bar":
                self._plot_grouped_bars(ax, names, values, labels, color_mapping)
            elif self.chart_type == "stacked_bar":
                self._plot_stacked_bars(ax, names, values, labels, color_mapping)
            ax.set_xticks(np.arange(len(set(names))))
            ax.set_xticklabels(sorted(list(set(names))))
            ax.set_title(chart.get_name())
            if series_count > 1:
                ax.legend()
        plt.tight_layout()
        plt.show()
