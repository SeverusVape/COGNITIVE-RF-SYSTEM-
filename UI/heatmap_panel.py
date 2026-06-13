# UI/heatmap_panel.py

import pyqtgraph as pg

def create_heatmap_panel(
        win,
        colormap
):

    win.nextRow()

    heatmap_plot = win.addPlot(
        title="Survey Heat Map"
    )

    heatmap_plot.setMaximumHeight(
        180
    )

    heatmap_plot.hideAxis(
        "left"
    )

    heatmap_plot.hideAxis(
        "bottom"
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

    return (
        heatmap_plot,
        heatmap_img
    )