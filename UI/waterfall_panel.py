import pyqtgraph as pg
from PyQt6.QtCore import QRectF
import numpy as np

def create_waterfall_panel(
        win
):

    win.nextRow()

    waterfall_plot = win.addPlot(
        title="Waterfall"
    )

    waterfall_plot.setMaximumHeight(
        200
    )

    waterfall_plot.hideAxis(
        "left"
    )

    waterfall_plot.setLabel(
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

    waterfall_img.setRect(
        QRectF(
            freqs_mhz[0],
            0,
            freqs_mhz[-1] - freqs_mhz[0],
            waterfall_history
        )
    )