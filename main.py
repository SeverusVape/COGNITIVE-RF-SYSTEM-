import sys
from collections import deque

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
from SDR.sdr_worker import SDRWorker
from SDR.fft_processing import compute_windowed_fft
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
    build_results_html
)

#SIGNALS --------->

from SIGNALS.signal_classifier import (
    classify_signal
)
from SIGNALS.signal_history import (
    update_signal_history,
    increment_history_update_count,
    prune_stale_history,
    reset_cycle_tracking
)
from SIGNALS.feature_extractor import FeatureStore
from SIGNALS.peak_confirmation import PeakConfirmer

# UI -------->

from UI.heatmap_panel import (
    create_heatmap_panel
)
from UI.waterfall_panel import (
    create_waterfall_panel,
    update_waterfall_panel
)
from UI.fft_panel import (
    create_fft_panel,
    update_peak_markers
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
from UI.theme import (
    SURVEY_CONTROL_PANEL_MARGINS,
    SURVEY_CONTROL_PANEL_SPACING,
    SURVEY_CONTROL_PANEL_STYLESHEET
)

from UTILS.occupancy import (
    calculate_occupancy
)
from UTILS.frequency_axis import (
    build_frequency_axis,
    build_frequency_edges
)
from UTILS.measurement_aggregation import (
    aggregate_measurements
)

# GLOBALS ----->
feature_store = FeatureStore()

peak_confirmer = PeakConfirmer(
    required_hits=PEAK_CONFIRMATION_REQUIRED_HITS,
    window_frames=PEAK_CONFIRMATION_WINDOW_FRAMES,
    tolerance_khz=PEAK_CONFIRMATION_TOLERANCE_KHZ
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
control_panel = QWidget()

control_panel.setObjectName(
    "surveyControlPanel"
)

control_panel.setStyleSheet(
    SURVEY_CONTROL_PANEL_STYLESHEET
)

control_layout = QVBoxLayout(
    control_panel
)

control_layout.setContentsMargins(
    *SURVEY_CONTROL_PANEL_MARGINS
)

control_layout.setSpacing(
    SURVEY_CONTROL_PANEL_SPACING
)

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
    decision_mode_combo,
    start_survey_button
) = create_survey_controls()

signals_panel, signals_table = create_signal_panel()
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
    signals_panel
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

survey_settings_label.setObjectName(
    "surveyPanelTitle"
)

survey_settings_subtitle = QLabel(
    "Configure scan range and "
    "recommendation strategy."
)

survey_settings_subtitle.setObjectName(
    "surveyPanelSubtitle"
)

survey_settings_subtitle.setWordWrap(
    True
)

start_frequency_label = QLabel(
    "Start frequency (MHz)"
)

stop_frequency_label = QLabel(
    "Stop frequency (MHz)"
)

step_frequency_label = QLabel(
    "Step size (MHz)"
)

decision_mode_label = QLabel(
    "Decision mode"
)

for field_label in (
        start_frequency_label,
        stop_frequency_label,
        step_frequency_label,
        decision_mode_label
):
    field_label.setObjectName(
        "surveyFieldLabel"
    )

survey_results_label = QLabel(
    "SURVEY RESULTS"
)

survey_results_label.setObjectName(
    "surveySectionTitle"
)

clear_survey_button.setObjectName(
    "surveySecondaryButton"
)

control_layout.addWidget(
    survey_settings_label
)

control_layout.addWidget(
    survey_settings_subtitle
)

control_layout.addSpacing(
    8
)

control_layout.addWidget(
    start_frequency_label
)

control_layout.addWidget(
    start_freq_input
)

control_layout.addWidget(
    stop_frequency_label
)

control_layout.addWidget(
    stop_freq_input
)

control_layout.addWidget(
    step_frequency_label
)

control_layout.addWidget(
    step_freq_input
)

control_layout.addSpacing(
    8
)

control_layout.addWidget(
    decision_mode_label
)

control_layout.addWidget(
    decision_mode_combo
)

control_layout.addSpacing(
    12
)

control_layout.addWidget(
    start_survey_button
)

control_layout.addWidget(
    clear_survey_button
)

control_layout.addSpacing(
    18
)

control_layout.addWidget(
    survey_results_label
)

control_layout.addWidget(
    survey_label
)

control_layout.addStretch()

main_layout.addWidget(
    control_panel,
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

waterfall_left, waterfall_right = (
    build_frequency_edges(
        freqs_mhz
    )
)

waterfall_plot.setXRange(
    waterfall_left,
    waterfall_right,
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
current_measurement = {
    "occupancy": 0,
    "max_power": 0,
    "average_power": 0
}
measurement_buffer = deque(
    maxlen=SURVEY_MEASUREMENT_BUFFER_SIZE
)
tune_error_active = False

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
def tune_frequency(
        show_status=True
):

    global freqs
    global freqs_mhz
    global tune_error_active
    global current_measurement

    tune_error_active = False

    try:

        freq_mhz = float(
            freq_input.text()
        )

        if (
                not np.isfinite(freq_mhz)
                or freq_mhz < MIN_CENTER_FREQ_MHZ
                or freq_mhz > MAX_CENTER_FREQ_MHZ
        ):
            tune_error_active = True

            status_label.setText(
                "SYSTEM STATUS\n\n"
                "INVALID FREQUENCY\n\n"
                f"Enter {MIN_CENTER_FREQ_MHZ}"
                f"–{MAX_CENTER_FREQ_MHZ} MHz."
            )
            return

        new_freq = freq_mhz * 1e6

        tune_error_active = True
        current_measurement = None
        measurement_buffer.clear()
        peak_confirmer.reset()

        if show_status:
            status_label.setText(
                "SYSTEM STATUS\n\n"
                "TUNING\n\n"
                f"Requested {freq_mhz:.1f} MHz."
            )

        if not sdr_worker.request_tune(new_freq):
            handle_tune_failure(
                new_freq,
                "SDR worker is not running."
            )

    except ValueError:
        tune_error_active = True

        status_label.setText(
            "SYSTEM STATUS\n\n"
            "INVALID FREQUENCY\n\n"
            "Enter a numeric frequency."
        )

    except Exception as error:
        tune_error_active = True

        status_label.setText(
            "SYSTEM STATUS\n\n"
            "TUNE ERROR\n\n"
            + str(error)
        )


def handle_tune_success(freq_hz):
    global freqs
    global freqs_mhz
    global tune_error_active

    freq_mhz = freq_hz / 1e6

    peak_confirmer.reset()

    freqs, freqs_mhz = build_frequency_axis(
        NUM_SAMPLES,
        SAMPLE_RATE,
        freq_hz
    )

    frequency_display.setText(
        f"{freq_mhz:.1f} MHz"
    )

    waterfall_left, waterfall_right = (
        build_frequency_edges(
            freqs_mhz
        )
    )

    waterfall_plot.setXRange(
        waterfall_left,
        waterfall_right,
        padding=0
    )

    waterfall_img.setRect(
        QRectF(
            waterfall_left,
            0,
            waterfall_right - waterfall_left,
            WATERFALL_HISTORY
        )
    )

    tune_error_active = False


def handle_tune_failure(
        freq_hz,
        message
):
    global tune_error_active
    global current_measurement

    tune_error_active = True
    current_measurement = None

    status_label.setText(
        "SYSTEM STATUS\n\n"
        "TUNE ERROR\n\n"
        + message
    )


def handle_sdr_error(message):
    global current_measurement

    current_measurement = None

    status_label.setText(
        "SYSTEM STATUS\n\n"
        "SDR NOT CONNECTED\n\n"
        + message
    )


def get_survey_measurement():
    return aggregate_measurements(
        list(
            measurement_buffer
        ),
        minimum_count=(
            SURVEY_MIN_MEASUREMENT_FRAMES
        )
    )


# ==================================================
# REAL-TIME SAMPLE PROCESSING
# ==================================================
def process_samples(samples):
    global occupancy_percent
    global current_measurement
    global smoothed_fft

    feature_store.prune_stale(
        FEATURE_MAX_AGE_SECONDS
    )

    prune_stale_history(
        SIGNAL_HISTORY_MAX_AGE_SECONDS
    )

    reset_cycle_tracking()
    increment_history_update_count()

    power_db = compute_windowed_fft(
        samples
    )

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

    raw_peaks, threshold = detect_peaks(
        power_db,
        freqs_mhz
    )

    peaks = peak_confirmer.update(
        raw_peaks
    )

    log_signals(
        peaks
    )

    occupancy_percent, meter = calculate_occupancy(
        power_db,
        threshold
    )

    displayed_threshold = float(
        np.median(
            threshold
        )
    )

    current_measurement = {
        "occupancy": round(float(occupancy_percent), 1),
        "max_power": round(float(np.max(power_db)), 1),
        "average_power": round(float(np.mean(power_db)), 1)
    }

    if not tune_error_active:
        measurement_buffer.append(
            current_measurement.copy()
        )

    update_signal_panel(
        signals_table,
        peaks,
        classify_signal,
        feature_store
    )

    if not tune_error_active:
        update_status_panel(
            status_label,
            freq_input,
            SAMPLE_RATE,
            freqs_mhz,
            peaks,
            displayed_threshold,
            meter,
            occupancy_percent
        )

    update_peak_markers(
        fft_plot,
        peaks
    )

    update_waterfall_panel(
        waterfall,
        waterfall_img,
        freqs_mhz,
        power_db,
        WATERFALL_HISTORY
    )


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
    decision_mode_combo,
    heatmap_img,
    heatmap_plot,
    recommended_line,
    lambda: tune_frequency(
        show_status=False
    ),
    get_survey_measurement,
    feature_store
)

# =========================================
# CONNECT SURVEY TIMER
# =========================================

survey_timer.timeout.connect(
        survey_controller.survey_step
    )
# ==================================================
# SDR WORKER SETUP
# ==================================================
sdr_worker = SDRWorker(
    SAMPLE_RATE,
    CENTER_FREQ,
    GAIN,
    NUM_SAMPLES
)

sdr_worker.samples_ready.connect(
    process_samples
)

sdr_worker.connection_error.connect(
    handle_sdr_error
)

sdr_worker.tune_succeeded.connect(
    handle_tune_success
)

sdr_worker.tune_failed.connect(
    handle_tune_failure
)

sdr_worker.start()


def begin_shutdown():
    survey_controller.begin_shutdown()
    sdr_worker.requestInterruption()


app.aboutToQuit.connect(
    begin_shutdown
)


# ==================================================
# BUTTON CONNECTIONS
# ==================================================
tune_button.clicked.connect(
    lambda: tune_frequency()
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
    lambda event:
    survey_controller.show_results_popup()
)

# ==================================================
# START APPLICATION
# ==================================================

app.exec()

# ==================================================
# CLEANUP
# ==================================================

sdr_worker.requestInterruption()

if not sdr_worker.wait(1000):
    sdr_worker.terminate()
    sdr_worker.wait()
