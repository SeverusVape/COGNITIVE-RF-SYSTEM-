import sys
import numpy as np

from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLineEdit,
    QLabel
)

from PyQt6.QtCore import QTimer

import pyqtgraph as pg

from SDR.sdr_manager import SDRManager
from SDR.fft_processing import compute_fft
from SDR.detection import detect_peaks

from UTILS.config import *


# ---------------- SDR MANAGER ----------------
sdr_manager = SDRManager(
    SAMPLE_RATE,
    CENTER_FREQ,
    GAIN
)


# ---------------- QT APPLICATION ----------------
app = QApplication(sys.argv)

pg.setConfigOption(
    'background',
    'k'
)

pg.setConfigOption(
    'foreground',
    'w'
)


# ---------------- MAIN WINDOW ----------------
main_window = QWidget()

main_window.setWindowTitle(
    "Adaptive SDR Spectrum Analyzer"
)

# MAIN LAYOUT (LEFT PANEL + GRAPH AREA)
main_layout = QHBoxLayout()


# ---------------- CONTROL PANEL ----------------
control_layout = QVBoxLayout()

freq_label = QLabel(
    "Frequency (MHz)"
)

freq_input = QLineEdit()

freq_input.setText("100")

tune_button = QPushButton(
    "Tune"
)

control_layout.addWidget(
    freq_label
)

control_layout.addWidget(
    freq_input
)

control_layout.addWidget(
    tune_button
)

# Push controls to top
control_layout.addStretch()

# Add control panel to main layout
main_layout.addLayout(
    control_layout,
    1
)

# THEN add right-side controls

main_layout.addLayout(
    control_layout,
    1
)

# ---------------- GRAPH WINDOW ----------------
win = pg.GraphicsLayoutWidget()

main_layout.addWidget(
    win,
    8
)

main_window.setLayout(
    main_layout
)

main_window.resize(
    1400,
    900
)

main_window.show()


# ---------------- FFT PLOT ----------------
fft_plot = win.addPlot(
    title="Real-Time Spectrum"
)

fft_plot.setLabel(
    'left',
    'Power',
    units='dB'
)

fft_plot.setLabel(
    'bottom',
    'Frequency',
    units='MHz'
)

fft_plot.showGrid(
    x=True,
    y=True,
    alpha=0.3
)

curve = fft_plot.plot(
    pen=pg.mkPen(
        color=(148, 0, 211),
        width=2
    )
)


# ---------------- NEXT ROW ----------------
win.nextRow()


# ---------------- WATERFALL ----------------
waterfall_plot = win.addPlot(
    title="Waterfall"
)

waterfall_plot.hideAxis(
    'left'
)

waterfall_plot.setLabel(
    'bottom',
    'Frequency',
    units='MHz'
)

waterfall_img = pg.ImageItem()

waterfall_plot.addItem(
    waterfall_img
)

colormap = pg.colormap.get(
    'viridis'
)

waterfall_img.setColorMap(
    colormap
)


# ---------------- FREQUENCY AXIS ----------------
freqs = np.fft.fftshift(
    np.fft.fftfreq(
        NUM_SAMPLES,
        d=1 / SAMPLE_RATE
    )
)

freqs = freqs + CENTER_FREQ

freqs_mhz = freqs / 1e6


# ---------------- WATERFALL BUFFER ----------------
waterfall = np.zeros(
    (
        WATERFALL_HISTORY,
        NUM_SAMPLES
    )
)


# ---------------- TUNE FUNCTION ----------------
def tune_frequency():

    global freqs
    global freqs_mhz

    try:

        freq_mhz = float(
            freq_input.text()
        )

        new_freq = freq_mhz * 1e6

        sdr_manager.tune(
            new_freq
        )

        freqs = np.fft.fftshift(
            np.fft.fftfreq(
                NUM_SAMPLES,
                d=1 / SAMPLE_RATE
            )
        )

        freqs = freqs + new_freq

        freqs_mhz = freqs / 1e6

    except:

        print(
            "Invalid frequency"
        )


# ---------------- UPDATE FUNCTION ----------------
def update():

    global waterfall

    # SDR samples
    samples = sdr_manager.read_samples(
        NUM_SAMPLES
    )

    # FFT
    power_db = compute_fft(
        samples
    )

    # Update FFT
    curve.setData(
        freqs_mhz,
        power_db
    )

    # Remove old markers
    for item in fft_plot.items[:]:

        if isinstance(
            item,
            pg.TextItem
        ):
            fft_plot.removeItem(item)

        if isinstance(
            item,
            pg.ScatterPlotItem
        ):
            fft_plot.removeItem(item)

    # Detect peaks
    peaks = detect_peaks(
        power_db,
        freqs_mhz
    )

    # Draw peaks
    for freq, power in peaks:

        peak_marker = pg.ScatterPlotItem(
            [freq],
            [power + 2],
            symbol='t',
            size=14,
            brush='red',
            pen='white'
        )

        fft_plot.addItem(
            peak_marker
        )

        label = pg.TextItem(
            text=f"{freq:.1f} MHz",
            color='yellow'
        )

        label.setPos(
            freq,
            power + 5
        )

        fft_plot.addItem(
            label
        )

    # Update waterfall
    waterfall = np.roll(
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
        (10, 60)
    )


# ---------------- TIMER ----------------
timer = QTimer()

timer.timeout.connect(
    update
)

timer.start(100)


# ---------------- BUTTONS ----------------
tune_button.clicked.connect(
    tune_frequency
)


# ---------------- START APPLICATION ----------------
app.exec()


# ---------------- CLEANUP ----------------
sdr_manager.close()