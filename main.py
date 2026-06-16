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

from PyQt6.QtTest import QTest

import pyqtgraph as pg

import SURVEY.survey_manager as survey
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
    build_results_text,
    heatmap_history
)
from SIGNALS.signal_classifier import (
    classify_signal
)
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

info_layout.addWidget(
    signals_label
)

info_layout.addWidget(
    survey_label
)

info_layout.addWidget(
    status_label
)

info_layout.addStretch()

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
    clear_survey_button
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

heatmap_plot, heatmap_img = (
    create_heatmap_panel(
        win,
        colormap
    )
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

    global survey_timer

    survey_timer.stop()
    survey.survey_frequencies = []
    survey.survey_results = {}
    survey.current_survey_index = 0

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

def start_survey():

    global survey_frequencies
    global current_survey_index
    global survey_results
    global heatmap_history
    global heatmap_history
    # clean the array
    survey_frequencies = []
    survey_results = {}
    current_survey_index = 0

    heatmap_history.clear()

    start_mhz = float(
        start_freq_input.text()
    )

    stop_mhz = float(
        stop_freq_input.text()
    )

    step_mhz = float(
        step_freq_input.text()
    )

    survey_frequencies = (
        generate_frequencies(
            start_mhz,
            stop_mhz,
            step_mhz
        )
    )

    survey_label.setText(
        f"SURVEY STATUS\n\n"
        f"Frequency:\n"
        f"{survey_frequencies[0]:.1f} MHz\n\n"
        f"Point:\n"
        f"0 / {len(survey_frequencies)}\n\n"
        f"Progress:\n"
        f"0%"
    )



    survey_timer.start(
        3000
    )


# ==================================================
# SURVEY TIMER SETUP
# ==================================================
survey_timer = QTimer()


def survey_step():

    global current_survey_index
    global survey_frequencies
    global survey_timer
    global occupancy_percent
    global survey_results

    if current_survey_index >= len(
            survey_frequencies
    ):
        survey_timer.stop()

        print(
            "Survey Complete"
        )

        sorted_results = rank_frequencies(
            survey_results
        )

        occupancies = []

        for freq in survey_frequencies:
            occupancies.append(
                survey_results[freq]
            )

        heatmap_history.append(
            occupancies
        )

        heatmap_data = np.array(
            heatmap_history
        )

        heatmap_img.setImage(
            heatmap_data
        )

        heatmap_img.setRect(
            QRectF(
                survey_frequencies[0],
                0,
                survey_frequencies[-1]
                - survey_frequencies[0],
                1
            )
        )

        heatmap_plot.setLabel(
            "bottom",
            "Frequency",
            units="MHz"
        )

        best_frequency = sorted_results[0][0]
        best_occupancy = sorted_results[0][1]

        average_occupancy = round(
            sum(survey_results.values())
            / len(survey_results),
            1
        )

        points_scanned = len(
            survey_results
        )

        results_text = build_results_text(
            sorted_results,
            points_scanned,
            average_occupancy,
            best_frequency,
            best_occupancy
        )


        survey_label.setText(
            results_text
        )

        return

    frequency = survey_frequencies[
        current_survey_index
    ]

    progress_percent = int(
        (current_survey_index + 1)
        / len(survey_frequencies)
        * 100
    )

    progress_bar = build_progress_bar(
        progress_percent
    )

    survey_text = build_status_text(
        frequency,
        current_survey_index + 1,
        len(survey_frequencies),
        progress_percent,
        progress_bar
    )

    survey_label.setText(
        survey_text
    )

    freq_input.setText(
        str(frequency)
    )

    tune_frequency()

    QTest.qWait(
        500
    )

    survey_results[frequency] = round(
        float(occupancy_percent), 1
    )

    current_survey_index += 1

# =========================================
# CONNECT SURVEY TIMER
# =========================================

survey_timer.timeout.connect(
        survey_step
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
    clear_current_survey
)

start_survey_button.clicked.connect(
    start_survey
)

# ==================================================
# START APPLICATION
# ==================================================

app.exec()

# ==================================================
# CLEANUP
# ==================================================

sdr_manager.close()