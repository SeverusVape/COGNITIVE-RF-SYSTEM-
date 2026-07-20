# UI/heatmap_panel.py

import pyqtgraph as pg

from UI.graph_style import (
    set_axis_label,
    style_plot
)


def create_heatmap_panel(
        win,
        colormap
):

    win.nextRow()

    heatmap_plot = win.addPlot()

    style_plot(
        heatmap_plot,
        "Survey occupancy history"
    )

    set_axis_label(
        heatmap_plot,
        "bottom",
        "Frequency",
        units="MHz"
    )

    set_axis_label(
        heatmap_plot,
        "left",
        "Survey run"
    )

    heatmap_plot.setMaximumHeight(
        230
    )

    heatmap_img = pg.ImageItem(
        axisOrder="row-major"
    )

    color_bar = pg.ColorBarItem(

        values=(0, 100),
        colorMap=colormap,
        orientation="horizontal",
        interactive=False,
        label="Occupancy (%)",
        width=7

    )

    heatmap_plot.addItem(
        heatmap_img
    )

    heatmap_img.setColorMap(
        colormap
    )

    color_bar.setImageItem(
        heatmap_img
    )

    color_bar.axis.setLabel(
        "Occupancy (%)"
    )

    recommended_line = pg.PlotDataItem(
        [],
        [],
        pen=pg.mkPen(
            color=(255, 0, 0),
            width=2,
            style=pg.QtCore.Qt.PenStyle.DashLine
        )
    )

    heatmap_plot.addItem(
        recommended_line
    )

    win.nextRow()
    win.addItem(
        color_bar
    )


    return (
        heatmap_plot,
        heatmap_img,
        recommended_line
    )
