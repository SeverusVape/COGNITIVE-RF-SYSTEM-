import sys
import numpy as np

from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel
)

from PyQt6.QtCore import (
    QTimer,
    QRectF
)

import pyqtgraph as pg

from SDR.sdr_manager import SDRManager
from SDR.fft_processing import compute_fft
from SDR.detection import detect_peaks
from UTILS.config import *

from LOGGING.signal_logger import log_signals

from SURVEY.survey_manager import (
    add_survey_result,
    clear_survey
)

from UI.control_panel import create_control_widgets
from UI.survey_controls import create_survey_controls
from UI.signal_panel import create_signal_panel
from UI.status_panel import create_status_panel
from UI.survey_panel import create_survey_panel


# ==================================================
# SDR INITIALIZATION
# ==================================================
sdr_manager = SDRManager(
    SAMPLE_RATE,
    CENTER_FREQ,
    GAIN
)


# ==================================================
# QT APPLICATION SETUP
# ==================================================
app = QApplication(sys.argv)

pg.setConfigOption(
    "background",
    "k"
)

pg.setConfigOption(
    "foreground",
    "w"
)


# ==================================================
# MAIN WINDOW SETUP
# ==================================================
main_window = QWidget()

main_window.setWindowTitle(
    "Adaptive SDR Spectrum Analyzer"
)

main_layout = QHBoxLayout()


# ==================================================
# LEFT CONTROL PANEL SETUP
# ==================================================
control_layout = QVBoxLayout()

(
    freq_label,
    freq_input,
    tune_button,
    survey_button,
    clear_survey_button
) = create_control_widgets()

(
    start_freq_input,
    stop_freq_input,
    step_freq_input,
    start_survey_button
) = create_survey_controls()

signals_label = create_signal_panel()
status_label = create_status_panel()
survey_label = create_survey_panel()


# ==================================================
# LEFT CONTROL PANEL LAYOUT
# ==================================================
control_layout.addWidget(
    freq_label
)

control_layout.addWidget(
    freq_input
)

control_layout.addWidget(
    tune_button
)

control_layout.addWidget(
    survey_button
)

control_layout.addWidget(
    clear_survey_button
)

control_layout.addWidget(
    QLabel("----------------")
)

control_layout.addWidget(
    signals_label
)

control_layout.addWidget(
    QLabel("----------------")
)

control_layout.addWidget(
    status_label
)

control_layout.addWidget(
    QLabel("----------------")
)

control_layout.addWidget(
    QLabel("Start MHz")
)

control_layout.addWidget(
    start_freq_input
)

control_layout.addWidget(
    QLabel("Stop MHz")
)

control_layout.addWidget(
    stop_freq_input
)

control_layout.addWidget(
    QLabel("Step MHz")
)

control_layout.addWidget(
    step_freq_input
)

control_layout.addWidget(
    start_survey_button
)

control_layout.addWidget(
    survey_label
)

control_layout.addStretch()

main_layout.addLayout(
    control_layout,
    2
)


# ==================================================
# GRAPH AREA SETUP
# ==================================================
win = pg.GraphicsLayoutWidget()

main_layout.addWidget(
    win,
    6
)

main_window.setLayout(
    main_layout
)

main_window.resize(
    1400,
    900
)

main_window.show()


# ==================================================
# FFT PLOT SETUP
# ==================================================
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
        color=(148, 0, 211),
        width=2
    )
)


# ==================================================
# WATERFALL PLOT SETUP
# ==================================================
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


# ==================================================
# FREQUENCY AXIS SETUP
# ==================================================
freqs = np.fft.fftshift(
    np.fft.fftfreq(
        NUM_SAMPLES,
        d=1 / SAMPLE_RATE
    )
)

freqs = freqs + CENTER_FREQ

freqs_mhz = freqs / 1e6

waterfall_plot.setXRange(
    freqs_mhz[0],
    freqs_mhz[-1],
    padding=0
)


# ==================================================
# WATERFALL BUFFER SETUP
# ==================================================
waterfall = np.zeros(
    (
        WATERFALL_HISTORY,
        NUM_SAMPLES
    )
)

occupancy_percent = 0


# ==================================================
# SURVEY BUTTON FUNCTIONS
# ==================================================
def add_current_survey_point():

    add_survey_result(
        survey_label,
        float(freq_input.text()),
        occupancy_percent
    )


def clear_current_survey():

    clear_survey(
        survey_label
    )


# ==================================================
# FREQUENCY TUNING FUNCTION
# ==================================================
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

        waterfall_plot.setXRange(
            freqs_mhz[0],
            freqs_mhz[-1],
            padding=0
        )

        waterfall_img.setRect(
            QRectF(
                freqs_mhz[0],
                0,
                freqs_mhz[-1] - freqs_mhz[0],
                WATERFALL_HISTORY
            )
        )

    except Exception as e:

        print(
            f"Invalid frequency: {e}"
        )


# ==================================================
# OCCUPANCY CALCULATION
# ==================================================
def calculate_occupancy(
    power_db,
    threshold
):

    occupied_bins = np.sum(
        power_db > threshold
    )

    occupancy = (
        occupied_bins / len(power_db)
    ) * 100

    bars = int(
        occupancy / 10
    )

    meter = (
        "[" +
        "■" * bars +
        "□" * (10 - bars) +
        "]"
    )

    return occupancy, meter


# ==================================================
# SIGNAL PANEL UPDATE
# ==================================================
def update_signal_panel(
    peaks
):

    signal_text = "Detected Signals\n\n"

    if len(peaks) == 0:

        signal_text += "None"

    else:

        for freq, power in peaks:

            if power > 60:

                strength = "Strong"

            elif power > 45:

                strength = "Medium"

            else:

                strength = "Weak"

            signal_text += (
                f"{freq:.2f} MHz  "
                f"{strength}\n"
            )

    signals_label.setText(
        signal_text
    )


# ==================================================
# STATUS PANEL UPDATE
# ==================================================
def update_status_panel(
    peaks,
    threshold,
    meter,
    occupancy
):

    status_text = (
        "Status\n\n"
        "RTL-SDR Connected\n"
        f"Center: {freq_input.text()} MHz\n"
        f"Sample Rate: {SAMPLE_RATE / 1e6:.3f} MSPS\n"
        f"Range: {freqs_mhz[0]:.3f} - {freqs_mhz[-1]:.3f} MHz\n"
        f"Signals Found: {len(peaks)}\n"
        f"Thresholds: {threshold:.1f} dB\n"
        f"Occupancy: {meter} {occupancy:.0f}%\n"
    )

    status_label.setText(
        status_text
    )


# ==================================================
# PEAK MARKER UPDATE
# ==================================================
def update_peak_markers(
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

    for freq, power in peaks:

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


# ==================================================
# WATERFALL UPDATE
# ==================================================
def update_waterfall(
    power_db
):

    global waterfall

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

    waterfall_img.setRect(
        QRectF(
            freqs_mhz[0],
            0,
            freqs_mhz[-1] - freqs_mhz[0],
            WATERFALL_HISTORY
        )
    )

    waterfall_img.setLevels(
        (10, 60)
    )


# ==================================================
# REAL-TIME SDR UPDATE LOOP
# ==================================================
def update():

    global occupancy_percent

    samples = sdr_manager.read_samples(
        NUM_SAMPLES
    )

    power_db = compute_fft(
        samples
    )

    curve.setData(
        freqs_mhz,
        power_db
    )

    peaks, threshold = detect_peaks(
        power_db,
        freqs_mhz
    )

    log_signals(
        peaks
    )

    occupancy_percent, meter = calculate_occupancy(
        power_db,
        threshold
    )

    update_signal_panel(
        peaks
    )

    update_status_panel(
        peaks,
        threshold,
        meter,
        occupancy_percent
    )

    update_peak_markers(
        peaks
    )

    update_waterfall(
        power_db
    )


# ==================================================
# TIMER SETUP
# ==================================================
timer = QTimer()

timer.timeout.connect(
    update
)

timer.start(
    100
)


# ==================================================
# BUTTON CONNECTIONS
# ==================================================
tune_button.clicked.connect(
    tune_frequency
)

survey_button.clicked.connect(
    add_current_survey_point
)

clear_survey_button.clicked.connect(
    clear_current_survey
)


# ==================================================
# START APPLICATION
# ==================================================
app.exec()


# ==================================================
# CLEANUP
# ==================================================
sdr_manager.close()