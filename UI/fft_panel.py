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