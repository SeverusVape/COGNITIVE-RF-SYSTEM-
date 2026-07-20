from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QVBoxLayout,
    QWidget
)

import pyqtgraph as pg

from UI.theme import (
    GRAPH_AXIS_COLOR,
    GRAPH_AXIS_LINE_COLOR,
    GRAPH_PANEL_MARGINS,
    GRAPH_PANEL_STYLESHEET,
    GRAPH_TITLE_COLOR
)


AXIS_LABEL_STYLE = {
    "color": GRAPH_AXIS_COLOR,
    "font-size": "10pt"
}


def create_graph_canvas():
    panel = QWidget()

    panel.setObjectName(
        "graphPanel"
    )

    panel.setStyleSheet(
        GRAPH_PANEL_STYLESHEET
    )

    layout = QVBoxLayout(
        panel
    )

    layout.setContentsMargins(
        *GRAPH_PANEL_MARGINS
    )

    win = pg.GraphicsLayoutWidget()

    win.setObjectName(
        "graphCanvas"
    )

    win.ci.layout.setContentsMargins(
        6,
        6,
        6,
        6
    )

    win.ci.layout.setVerticalSpacing(
        8
    )

    layout.addWidget(
        win
    )

    return panel, win


def style_plot(
        plot,
        title
):
    plot.hideButtons()

    plot.setTitle(
        title,
        color=GRAPH_TITLE_COLOR,
        size="11pt"
    )

    tick_font = QFont()

    tick_font.setPointSize(
        9
    )

    for axis_name in (
            "left",
            "bottom"
    ):
        axis = plot.getAxis(
            axis_name
        )

        axis.setPen(
            pg.mkPen(
                GRAPH_AXIS_LINE_COLOR
            )
        )

        axis.setTextPen(
            pg.mkPen(
                GRAPH_AXIS_COLOR
            )
        )

        axis.setTickFont(
            tick_font
        )

        axis.setStyle(
            tickTextOffset=6
        )


def set_axis_label(
        plot,
        axis,
        text,
        units=None
):
    plot.setLabel(
        axis,
        text,
        units=units,
        **AXIS_LABEL_STYLE
    )
