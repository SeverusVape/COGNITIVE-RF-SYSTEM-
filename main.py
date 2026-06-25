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
    QRectF,
    Qt
)

from PyQt6.QtTest import QTest

import pyqtgraph as pg

import SURVEY.survey_manager as survey
from SURVEY.survey_controller import SurveyController
from SDR.sdr_manager import SDRManager
from SDR.fft_processing import compute_fft
from SDR.detection import detect_peaks
from UTILS.config import *
from LOGGING.signal_logger import log_signals
from SURVEY.survey_manager import (
    add_survey_result,
    clear_survey,
    build_progress_bar,
    generate_frequencies,
    rank_frequencies,
    build_status_text,
    build_results_text
)

#SIGNALS --------->

from SIGNALS.signal_classifier import (
    classify_signal
)
from SIGNALS.signal_history import (
    update_signal_history
)

# UI -------->

from UI.heatmap_panel import (
    create_heatmap_panel
)
from UI.waterfall_panel import (
    create_waterfall_panel
)
from UI.fft_panel import (
    create_fft_panel
)
from UI.control_panel import create_control_widgets
from UI.survey_controls import create_survey_controls
from UI.signal_panel import (
    create_signal_panel,
    update_signal_panel
)

from UI.status_panel import (
    create_status_panel,
    update_status_panel
)
from UI.survey_panel import create_survey_panel

# POPUP -------->
from UI.survey_popup import (
    SurveyPopup
)


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

info_layout = QVBoxLayout()

(
    freq_label,
    freq_input,
    tune_button,
    survey_button,
    clear_survey_button,
    auto_tune_button
) = create_control_widgets()

frequency_display = QLabel(
    "100.0 MHz"
)

frequency_display.setAlignment(
    Qt.AlignmentFlag.AlignCenter
)

frequency_display.setStyleSheet(
    """
    font-size: 28px;
    font-weight: bold;
    color: white;
    """
)

(
    start_freq_input,
    stop_freq_input,
    step_freq_input,
    start_survey_button
) = create_survey_controls()

signals_label = create_signal_panel()
status_label = create_status_panel()
survey_label = create_survey_panel()

top_frequencies_label = QLabel(
    "PERSISTENT FREQUENCIES\n\n"
    "No survey data"
)

top_frequencies_label.setStyleSheet(
    """
    background-color: #111111;
    border: 1px solid #333333;
    padding: 8px;
    color: #00ff88;
    font-family: Courier New;
    """
)

# ==================================================
# LEFT CONTROL PANEL LAYOUT
# ==================================================

info_layout.addWidget(
    signals_label
)

info_layout.addWidget(
    status_label
)

info_layout.addWidget(
    top_frequencies_label
)

info_layout.addStretch()

survey_settings_label = QLabel(
    "SURVEY SETTINGS"
)

survey_settings_label.setStyleSheet(
    """
    font-size: 16px;
    font-weight: bold;
    color: white;
    """
)

control_layout.addWidget(
    survey_settings_label
)

control_layout.addSpacing(
    10
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

control_layout.addSpacing(
    15
)

control_layout.addWidget(
    start_survey_button
)

control_layout.addWidget(
    clear_survey_button
)

control_layout.addSpacing(
    20
)

control_layout.addWidget(
    QLabel("SURVEY RESULTS")
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
center_layout = QVBoxLayout()

tune_layout = QHBoxLayout()

tune_layout.addStretch()

tune_layout.addWidget(
    freq_label
)

tune_layout.addWidget(
    freq_input
)

tune_layout.addWidget(
    tune_button
)

tune_layout.addWidget(
    auto_tune_button
)

tune_layout.addStretch()

win = pg.GraphicsLayoutWidget()

center_layout.addWidget(
    frequency_display
)

center_layout.addLayout(
    tune_layout
)

center_layout.addWidget(
    win
)

main_layout.addLayout(
    center_layout,
    8
)

main_layout.addLayout(
    info_layout,
    2
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

fft_plot, curve = (
    create_fft_panel(
        win
    )
)

# ==================================================
# WATERFALL PLOT SETUP
# ==================================================

waterfall_plot, waterfall_img, colormap = (
    create_waterfall_panel(
        win
    )
)

# ==================================================
# HEAT MAP SETUP
# ==================================================

(
    heatmap_plot,
    heatmap_img,
    recommended_line
) = create_heatmap_panel(
    win,
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

smoothed_fft = None
occupancy_percent = 0
survey_popup = None
latest_survey_results_text = ""
last_survey_settings = None

# ==================================================
# SURVEY BUTTON FUNCTIONS
# ==================================================
def add_current_survey_point():

    add_survey_result(
        survey_label,
        float(freq_input.text()),
        occupancy_percent
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

        frequency_display.setText(
            f"{freq_mhz:.1f} MHz"
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

    COLOR_BLUE = "#2ab7ca"
    COLOR_GREEN = "#24b755"
    COLOR_YELLOW = "#f4b400"
    COLOR_RED = "#fe4a49"
    COLOR_EMPTY = "#333333"

    colored_bars = ""

    for i in range(1, 11):

        if i <= bars:

            if i <= 4:

                color = COLOR_BLUE

            elif i <= 7:

                color = COLOR_GREEN

            elif i <= 9:

                color = COLOR_YELLOW

            else:

                color = COLOR_RED

            colored_bars += (
                f'<span style="color:{color};">'
                '■'
                '</span>'
            )

        else:

            colored_bars += (
                f'<span style="color:{COLOR_EMPTY};">'
                '░'
                '</span>'
            )

    meter = (

        f'<span style="font-family: Courier New; color: #ffffff;">'

        f'[{colored_bars}]'

        f'</span>'

    )

    return occupancy, meter

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

    global smoothed_fft

    if smoothed_fft is None:

        smoothed_fft = power_db.copy()

    else:

        smoothed_fft = (
                0.9 * smoothed_fft +
                0.1 * power_db
        )

    curve.setData(
        freqs_mhz,
        smoothed_fft
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
        signals_label,
        peaks,
        classify_signal
    )

    update_status_panel(
        status_label,
        freq_input,
        SAMPLE_RATE,
        freqs_mhz,
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
# SURVEY AUTOMATION
# ==================================================

def open_survey_popup():

    if (
            survey_controller.latest_survey_results_text
            == ""
    ):
        print("No survey results available")
        return

    popup = SurveyPopup(
        survey_controller.latest_survey_results_text
    )

    popup.show()

    global popup_ref
    popup_ref = popup

# ==================================================
# SURVEY TIMER SETUP
# ==================================================
survey_timer = QTimer()

survey_controller = SurveyController(
    survey_timer,
    survey_label,
    top_frequencies_label,
    freq_input,
    start_freq_input,
    stop_freq_input,
    step_freq_input,
    heatmap_img,
    heatmap_plot,
    recommended_line,
    tune_frequency,
    lambda: occupancy_percent
)

# =========================================
# CONNECT SURVEY TIMER
# =========================================

survey_timer.timeout.connect(
        survey_controller.survey_step
    )
# ==================================================
# TIMER SETUP MAIN
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
    survey_controller.clear_current_survey
)

auto_tune_button.clicked.connect(
    survey_controller.auto_tune_best
)

start_survey_button.clicked.connect(
    survey_controller.start_survey
)

survey_label.mousePressEvent = (
    lambda event: open_survey_popup()
)

# ==================================================
# START APPLICATION
# ==================================================

app.exec()

# ==================================================
# CLEANUP
# ==================================================

sdr_manager.close()