# UI/heatmap_panel.py

import pyqtgraph as pg

def create_heatmap_panel(
        win,
        colormap
):

    win.nextRow()

    heatmap_plot = win.addPlot(
        title="Survey Occupancy Map"
    )



    heatmap_plot.setLabel(
        "bottom",
        "Frequency",
        units="MHz"
    )

    heatmap_plot.setLabel(
        "left",
        "Survey #"
    )

    heatmap_plot.setMaximumHeight(
        230
    )

    heatmap_img = pg.ImageItem(
        axisOrder="row-major"
    )

    heatmap_plot.addItem(
        heatmap_img
    )

    heatmap_img.setColorMap(
        colormap
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


    return (
        heatmap_plot,
        heatmap_img,
        recommended_line
    )