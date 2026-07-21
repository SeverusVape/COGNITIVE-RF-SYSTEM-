import pyqtgraph as pg

from UI.graph_style import (
    set_axis_label,
    style_plot
)

from UI.theme import GRAPH_GRID_ALPHA


def create_fft_panel(
        win
):

    fft_plot = win.addPlot()

    style_plot(
        fft_plot,
        "Real-time spectrum"
    )

    set_axis_label(
        fft_plot,
        "left",
        "Power",
        units="dB"
    )

    set_axis_label(
        fft_plot,
        "bottom",
        "Frequency",
        units="MHz"
    )

    fft_plot.showGrid(
        x=True,
        y=True,
        alpha=GRAPH_GRID_ALPHA
    )

    curve = fft_plot.plot(
        pen=pg.mkPen(
            color=(180, 0, 255),
            width=1
        )
    )

    return (
        fft_plot,
        curve
    )

# ==================================================
# PEAK MARKER UPDATE
# ==================================================
def update_peak_markers(
        fft_plot,
        peaks
):

    for item in fft_plot.items[:]:

        if isinstance(
            item,
            pg.TextItem
        ):

            fft_plot.removeItem(
                item
            )

        if isinstance(
            item,
            pg.ScatterPlotItem
        ):

            fft_plot.removeItem(
                item
            )

    for peak in peaks:
        freq, power = peak[:2]

        peak_marker = pg.ScatterPlotItem(
            [freq],
            [power + 2],
            symbol="t",
            size=14,
            brush=pg.mkBrush(
                0,
                220,
                140,
                255
            ),
            pen=pg.mkPen(
                color=(0, 220, 140, 100),
                width=3
            )
        )

        fft_plot.addItem(
            peak_marker
        )

        label = pg.TextItem(
            text=f"{freq:.1f} MHz",
            color="yellow"
        )

        label.setPos(
            freq,
            power + 5
        )

        fft_plot.addItem(
            label
        )
