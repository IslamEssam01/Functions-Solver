from matplotlib.axes import Axes
from matplotlib.axis import Axis
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.scale import LinearScale, register_scale
from matplotlib.backends.backend_qt import NavigationToolbar2QT as NavigationToolbar
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
import numpy as np
import mplcursors


class RestrictedLinearScale(LinearScale):
    """
    A custom linear scale that restricts the range of the axis to specified minimum and maximum values.
    """

    name = 'restricted_linear'

    def __init__(self, axis: Axis, min=-np.inf, max=np.inf):
        """
        Initialize the RestrictedLinearScale.

        Args:
            axis (Axis) : The axis to which this scale is applied.
            min (float): The minimum allowed value for the axis. Defaults to -∞.
            max (float): The maximum allowed value for the axis. Defaults to +∞.
        """

        super().__init__(axis)
        self.min = min
        self.max = max

    def limit_range_for_scale(self, vmin, vmax, minpos):
        """
        Restrict the range of the axis to the specified minimum and maximum values.

        Args:
            vmin (float): The current minimum value of the axis.
            vmax (float): The current maximum value of the axis.
            minpos (float): The minimum positive value (unused in this implementation).

        Returns:
            tuple: The new (vmin, vmax) range, clamped to the specified bounds.
        """
        return max(vmin, self.min), min(vmax, self.max)


register_scale(RestrictedLinearScale)


class PlotManager:
    """
    A class to manage the plotting of functions and their intersections on a matplotlib canvas.
    """

    def __init__(self, canvas: FigureCanvas, f1_color: str, f2_color: str):
        """
        Initialize the PlotManager.

        Args:
            canvas (FigureCanvas): The matplotlib canvas to draw on.
            f1_color (str): The color for the first function's plot.
            f2_color (str): The color for the second function's plot.
        """

        self.canvas: FigureCanvas = canvas
        self.figure: Figure = canvas.figure

        toolbar = NavigationToolbar(self.canvas)
        toolbar.hide()
        toolbar.pan()  # Enable pan mode by default

        self.canvas.mpl_connect('scroll_event', self.on_scroll)

        self.ax: Axes = self.figure.add_axes((0.005, 0.005, 0.98, 0.98))

        self.f1_color: str = f1_color
        self.f2_color: str = f2_color

        self.f1_line: Line2D | None = None
        self.f2_line: Line2D | None = None
        self.setup_plot()

    def setup_plot(self):
        """
        Set up the initial configuration of the plot (axes, grid, limits, etc.).
        """

        self.ax.grid(True)
        self.ax.axhline(0, color='black', linewidth=0.5)
        self.ax.axvline(0, color='black', linewidth=0.5)

        self.ax.set_xlim(-10, 10)
        self.ax.set_ylim(-10, 10)

        # Hide the top and right spines (borders)
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)

        # Configure tick parameters
        self.ax.xaxis.set_tick_params(
            bottom='on', top='off', direction='inout')
        self.ax.yaxis.set_tick_params(
            left='on', right='off', direction='inout')

        # Position the bottom and left spines at the origin (0,0)
        self.ax.spines['bottom'].set_position('zero')
        self.ax.spines['left'].set_position('zero')

        # Apply the custom restricted linear scale to the axes
        self.ax.set_xscale("restricted_linear", min=-100, max=100)
        self.ax.set_yscale("restricted_linear", min=-100, max=100)

    def update_plot(self, plot_data, intersection_points, f1_evaluator):
        """
        Update the plot with new data, including function plots and intersection points.

        Args:
            plot_data (dict): A dictionary containing x and y data for the functions.
            intersection_points (list): A list of x-coordinates of intersection points.
            f1_evaluator (callable): A function to evaluate the y-values of the first function.
        """

        self.ax.clear()
        self.setup_plot()

        if plot_data['x1'] is not None:
            self.f1_line, = self.ax.plot(
                plot_data['x1'], plot_data['y1'], color=self.f1_color)

        if plot_data['x2'] is not None:
            self.f2_line, = self.ax.plot(
                plot_data['x2'], plot_data['y2'], color=self.f2_color)

        if intersection_points and f1_evaluator:
            x_intersect = intersection_points
            y_intersect = list(map(f1_evaluator, x_intersect))
            y_center = float(np.mean(y_intersect))
            y_spread = max(abs(max(y_intersect) - y_center),
                           abs(min(y_intersect) - y_center))

            plot_data["ylim"][0] = int(y_center - max(y_spread * 2, 10))
            plot_data["ylim"][1] = int(y_center + max(y_spread * 2, 10))

            scatter = self.ax.scatter(
                x_intersect, y_intersect, color='black', zorder=5)
            cursor = mplcursors.cursor(
                scatter, hover=mplcursors.HoverMode.Transient)

            @cursor.connect("add")
            def _(sel):
                x = round(sel.target[0], 4)
                y = round(sel.target[1], 4)
                sel.annotation.set(text=f'({x}, {y})')
                sel.annotation.get_bbox_patch().set(fc="white", alpha=0.8)

        # Update the axis scales and limits based on the plot data
        self.ax.set_xscale("restricted_linear", min=min(-100, -
                                                        plot_data['x_scale_max_limit']), max=max(100, plot_data["x_scale_max_limit"]))
        self.ax.set_yscale("restricted_linear", min=min(-100, -
                                                        plot_data['y_scale_max_limit']-100), max=max(100, plot_data["y_scale_max_limit"]+100))

        self.ax.set_xlim(plot_data['xlim'][0], plot_data['xlim'][1])
        self.ax.set_ylim(plot_data['ylim'][0], plot_data['ylim'][1])

        self.canvas.draw_idle()

    def update_colors(self, f1_color: str, f2_color: str):
        """
        Update the colors of the function plots.

        Args:
            f1_color (str): The new color for the first function's plot.
            f2_color (str): The new color for the second function's plot.
        """
        self.f1_color = f1_color
        self.f2_color = f2_color

        # Update the colors of the existing plot lines
        if self.f1_line:
            self.f1_line.set_color(f1_color)
        if self.f2_line:
            self.f2_line.set_color(f2_color)

        self.canvas.draw_idle()  # Refresh the canvas to show the new colors

    def on_scroll(self, event):
        """
        Handle scroll events to zoom in or out of the plot.

        Args:
            event: The scroll event.
        """
        if event.inaxes:
            ax = event.inaxes
            cur_xlim = ax.get_xlim()
            cur_ylim = ax.get_ylim()

            xdata = event.xdata
            ydata = event.ydata

            scale_factor = 1.1

            # Adjust the scaling factor based on the scroll direction
            if event.button == 'up':
                scale_factor = 1.0 / scale_factor

            new_width = (cur_xlim[1] - cur_xlim[0]) * scale_factor
            new_height = (cur_ylim[1] - cur_ylim[0]) * scale_factor

            rel_x = (xdata - cur_xlim[0]) / (cur_xlim[1] - cur_xlim[0])
            rel_y = (ydata - cur_ylim[0]) / (cur_ylim[1] - cur_ylim[0])

            ax.set_xlim([xdata - new_width * rel_x,
                        xdata + new_width * (1-rel_x)])
            ax.set_ylim([ydata - new_height * rel_y,
                        ydata + new_height * (1-rel_y)])

            self.canvas.draw_idle()
