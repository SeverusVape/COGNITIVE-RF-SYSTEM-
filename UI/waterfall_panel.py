import pyqtgraph as pg

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