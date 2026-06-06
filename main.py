import sys
import numpy as np

from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLineEdit,
    QLabel,
    QTextEdit
)


from PyQt6.QtCore import (QTimer, QRectF)
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

# Tune window
freq_input = QLineEdit()
freq_input.setText("100")
tune_button = QPushButton(
    "Tune"
)
survey_button = QPushButton(
    "Add Survey Point"
)

clear_survey_button = QPushButton(
    "Clear Survey"
)

# Signals window
signals_label = QTextEdit()
signals_label.setReadOnly(True)
signals_label.setText(
    "Detected Signals\n\nNone"
)
signals_label.setFixedHeight(100)

# Status window
status_label = QTextEdit()
status_label.setReadOnly(True)
status_label.setText(
    "Status\n\nStarting..."
)
status_label.setFixedHeight(200)

# Survey window
survey_label = QTextEdit()

survey_label.setReadOnly(
    True
)

survey_label.setText(
    "Survey Results\n"
)

survey_label.setFixedHeight(
    150
)

# Control layout all
control_layout.addWidget(
    freq_label
)

control_layout.addWidget(
    freq_input
)

control_layout.addWidget(tune_button)
control_layout.addWidget(survey_button)
control_layout.addWidget(clear_survey_button)

control_layout.addWidget(
    QLabel("----------------")
)

control_layout.addWidget(signals_label)
control_layout.addWidget(
    QLabel("----------------")
)

control_layout.addWidget(status_label)

control_layout.addWidget(
    QLabel("----------------")
)

control_layout.addWidget(
    survey_label
)
# Push controls to top
control_layout.addStretch()

# Add control panel to main layout
main_layout.addLayout(
    control_layout,
    2
)

# ---------------- GRAPH WINDOW ----------------
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

add_survey_result(
    survey_label,
    100,
    13
)

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

waterfall_plot.setMaximumHeight(200)

waterfall_plot.hideAxis(
    'left'
)

waterfall_plot.setLabel(
    'bottom',
    'Frequency',
    units='MHz'
)

waterfall_img = pg.ImageItem(
    axisOrder='row-major'
)

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

waterfall_plot.setXRange(
    freqs_mhz[0],
    freqs_mhz[-1],
    padding=0
)

# ---------------- WATERFALL BUFFER ----------------
waterfall = np.zeros(
    (
        WATERFALL_HISTORY,
        NUM_SAMPLES
    )
)

# ---------------- SURVEY FUNCTION --------------
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


# ---------------- UPDATE FUNCTION ----------------
def update():

    global occupancy_percent
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

    # Detect peaks and thresholds
    peaks, threshold = detect_peaks(
        power_db,
        freqs_mhz
    )

    log_signals(
        peaks
    )

    current_signals = set()

    occupied_bins = np.sum(
        power_db > threshold
    )

    occupancy_percent = (
        occupied_bins / len(power_db)
        ) * 100
# Occupancy bar
    bars = int(occupancy_percent / 10)

    meter = "[" + "■" * bars + "□" * (10 - bars) + "]"

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
    # SDR status
    status_text = (
        "Status\n\n"
        "RTL-SDR Connected\n"
        f"Center: {freq_input.text()} MHz\n"
        f"Sample Rate: {SAMPLE_RATE / 1e6:.3f} MSPS\n"
        f"Range: {freqs_mhz[0]:.3f} - {freqs_mhz[-1]:.3f} MHz\n"
        f"Signals Found: {len(peaks)}\n"
        f"Thresholds: {threshold:.1f} dB\n"
        f"Occupancy: {meter} {occupancy_percent:.0f}%\n"
    )

    status_label.setText(
        status_text
    )

    # Draw peaks
    for freq, power in peaks:

        peak_marker = pg.ScatterPlotItem(
            [freq],
            [power + 2],
            symbol='t',
            size=14,
            brush=pg.mkBrush(0, 220, 140, 255),
            pen=pg.mkPen(color=(0, 220, 140, 100), width=3)
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

    last_logged_signals = current_signals.copy()
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


# ---------------- TIMER ----------------
timer = QTimer()

timer.timeout.connect(
    update
)

timer.start(100)


# ---------------- BUTTONS CONNECTION ----------------
tune_button.clicked.connect(
    tune_frequency
)
survey_button.clicked.connect(
    add_current_survey_point
)

clear_survey_button.clicked.connect(
    clear_current_survey
)

# ---------------- START APPLICATION ----------------
app.exec()


# ---------------- CLEANUP ----------------
sdr_manager.close()