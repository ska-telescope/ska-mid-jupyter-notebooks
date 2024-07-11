"""Render the monitor e.a."""
from typing import Generic, Literal, OrderedDict, TypeVar

from bokeh.io import push_notebook, show
from bokeh.models import ColumnDataSource, LabelSet
from bokeh.plotting import figure

ItemStates = Literal["DISABLED", "BUSY", "ACTIVE", "OFFLINE"]

Colours = Literal[
    "darkmagenta",
    "yellow",
    "forestgreen",
    "pink",
    "red",
    "blue",
    "black",
    "white",
    "green",
    "orange",
    "grey",
]

state_mapping_to_clr: dict[ItemStates, Colours] = {
    "DISABLED": "darkmagenta",
    "BUSY": "yellow",
    "ACTIVE": "forestgreen",
    "OFFLINE": "pink",
}

BoxLabels = Literal[
    "On/Off",
    "Resources Assigned?",
    "Subarray Configured?",
    "Subarray Scanning?",
]

T = TypeVar("T", bound=str)
C = TypeVar("C", bound=str)


class LabeledBlock(Generic[T, C]):
    """Labels for blocks."""
    def __init__(self, text: T, colour: C) -> None:
        """
        Initialises LabeledBlock class
        :param text: text to be displayed
        :param colour: text colour
        """
        self.text = text
        self.colour = colour


class LabeledBoxesData(Generic[T, C]):
    """Labels for boxes full of data."""
    def __init__(
        self,
        x_position: list[float],
        y_position: list[float],
        square_labels: list[T],
        square_colours: list[C],
    ):
        """
        Initialise LabeledBoxesData class.

        :param x_position: list of x positions
        :param y_position: list of y positions
        :param square_labels: list of labels
        :param square_colours: list of colours
        """
        self.x_position = x_position
        self.y_position = y_position
        self.square_labels = square_labels
        self.square_colours = square_colours

    @property
    def as_dict(self) -> dict:
        """
        Get the data as a dictionary.

        :return: dictionary with positions, lables and colours
        """
        return {
            "x_position": self.x_position,
            "y_position": self.y_position,
            "square_labels": self.square_labels,
            "square_colours": self.square_colours,
        }


Name = TypeVar("Name", bound=str)
Value = TypeVar("Value", bound=str)


def _sample(start: float, end: float, number: int) -> list[float]:
    """
    Calculate the list of equidistant positions for number of items in a given range.

    The first item will always start with the start position and the end item will end on
    exactly the end position.

    :param start: the start position of the first item
    :param end: the position of the end item
    :param number: the quantity of items to be equally fitted in the range
    :return: the list of equidistant positions in the given start end range
    """
    assert end > start, "You must give a range in which the end is higher than the start"
    inner_points = number - 2
    sample_range = end - start

    def calc_pos(index: int) -> float:
        return round(distance * index + start, 2)

    if inner_points:
        distance = (sample_range) / (inner_points + 1)
        return [
            start,
            *[calc_pos(index) for index in range(1, number - 1)],
            end,
        ]
    else:
        return [start, end]


MonitoringItems = OrderedDict[Name, Value]


class MonitorPlot(Generic[Name, Value]):
    """Monitor the thickening plot."""
    def __init__(
        self,
        plot_width: int,
        plot_height: int,
        items: MonitoringItems[Name, Value],
        state_mapping_to_colour: dict[Value, Colours],
    ) -> None:
        """
        Initialise MonitorPlot class.

        :param plot_width: width of the plot
        :param plot_height: height of the plot
        :param items: items to be displayed
        :param state_mapping_to_colour: mapping of states to colours
        :return: None
        """
        self._state_mapping_to_clr = state_mapping_to_colour
        self._monitor_plot = figure(
            width=plot_width,
            height=plot_height,
            toolbar_location=None,
            x_range=(-0.5, 1.5),
            y_range=(-0.5, 1.5),
        )
        self._monitor_plot.axis.visible = False
        self._monitor_plot.grid.visible = False
        self._labeled_blocks = items
        number = len(items)
        self._monitor_source = ColumnDataSource(
            LabeledBoxesData(
                x_position=[0.5 for _ in range(len(items))],
                y_position=_sample(0, 1, number),
                square_labels=list(self._labeled_blocks.keys()),
                square_colours=self._colours_as_list,
            ).as_dict
        )
        self._labels = LabelSet(
            x="x_position",
            y="y_position",
            text="square_labels",
            x_offset=-200,
            y_offset=-10,
            background_fill_color="canvas",
            text_color="black",
            source=self._monitor_source,
        )
        self._handle = None

    @property
    def _colours_as_list(self) -> list[Colours]:
        """
        Get colours as list.

        :return: list of colours
        """
        return list(
            self._state_mapping_to_clr.get(value, "white")
            for value in self._labeled_blocks.values()
        )

    def _create_output(self) -> None:
        """Create output."""
        self._monitor_plot.square(
            x="x_position",
            y="y_position",
            size=20,
            color="square_colours",
            source=self._monitor_source,
        )
        self._monitor_plot.add_layout(self._labels)  # type: ignore

    def show(self) -> None:
        """Show output."""
        self._create_output()
        self._handle = show(self._monitor_plot, notebook_handle=True)

    def re_render(self) -> None:
        """Re-render plot."""
        self._create_output()
        push_notebook(handle=self._handle)

    def _update_data_source(self) -> None:
        """Update data source."""
        self._monitor_source.data["square_colours"] = self._colours_as_list

    def _set_box(self, box_name: Name, value: Value) -> None:
        """Set box."""
        self._labeled_blocks[box_name] = value
        self._update_data_source()
        self.re_render()
