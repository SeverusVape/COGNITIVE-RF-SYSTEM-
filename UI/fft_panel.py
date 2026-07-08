import pyqtgraph as pg

def create_fft_panel(
        win
):

    fft_plot = win.addPlot(
        title="Real-Time Spectrum"
    )

    fft_plot.setLabel(
        "left",
        "Power",
        units="dB"
    )

    fft_plot.setLabel(
        "bottom",
        "Frequency",
        units="MHz"
    )

    fft_plot.showGrid(
        x=True,
        y=True,
        alpha=0.3
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

    for freq, power, bandwidth_khz in peaks:

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
