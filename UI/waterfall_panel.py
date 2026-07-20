import pyqtgraph as pg
from PyQt6.QtCore import QRectF
import numpy as np

from UTILS.frequency_axis import (
    build_frequency_edges
)

from UI.graph_style import (
    set_axis_label,
    style_plot
)


def create_waterfall_panel(
        win
):

    win.nextRow()

    waterfall_plot = win.addPlot()

    style_plot(
        waterfall_plot,
        "Signal waterfall"
    )

    waterfall_plot.setMaximumHeight(
        200
    )

    waterfall_plot.hideAxis(
        "left"
    )

    set_axis_label(
        waterfall_plot,
        "bottom",
        "Frequency",
        units="MHz"
    )

    waterfall_img = pg.ImageItem(
        axisOrder="row-major"
    )

    waterfall_plot.addItem(
        waterfall_img
    )

    colormap = pg.colormap.get(
        "viridis"
    )

    waterfall_img.setColorMap(
        colormap
    )

    return (
        waterfall_plot,
        waterfall_img,
        colormap
    )


def update_waterfall_panel(
        waterfall,
        waterfall_img,
        freqs_mhz,
        power_db,
        waterfall_history
):
    waterfall[:] = np.roll(
        waterfall,
        -1,
        axis=0
    )

    waterfall[-1, :] = power_db

    waterfall_img.setImage(
        waterfall,
        autoLevels=False
    )

    waterfall_img.setLevels(
        [
            10,
            60
        ]
    )

    left_edge, right_edge = (
        build_frequency_edges(
            freqs_mhz
        )
    )

    waterfall_img.setRect(
        QRectF(
            left_edge,
            0,
            right_edge - left_edge,
            waterfall_history
        )
    )
