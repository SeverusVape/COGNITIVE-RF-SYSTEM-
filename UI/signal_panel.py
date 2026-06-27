from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView
)

from PyQt6.QtCore import Qt

from PyQt6.QtGui import QFont
from PyQt6.QtGui import QColor

from SIGNALS.signal_history import (
    update_signal_history,
    get_occupancy_percent
)

from SIGNALS.feature_extractor import (
    FeatureStore,
    extract_features
)

feature_store = FeatureStore()

def create_signal_panel():

    table = QTableWidget()

    table.setColumnCount(4)

    table.setHorizontalHeaderLabels(
        [
            "Freq",
            "Type",
            "Str",
            "Age"
        ]
    )

    table.verticalHeader().setVisible(False)

    table.setEditTriggers(
        QTableWidget.EditTrigger.NoEditTriggers
    )

    table.setSelectionMode(
        QTableWidget.SelectionMode.NoSelection
    )

    table.setFocusPolicy(
        Qt.FocusPolicy.NoFocus
    )

    table.setShowGrid(False)

    table.verticalHeader().setDefaultSectionSize(
        24
    )

    table.setCornerButtonEnabled(
        False
    )

    table.horizontalHeader().setStyleSheet(
        """
        QHeaderView::section {
            background-color: #222222;
            color: white;
            border: none;
            padding: 4px;
            font-weight: bold;
        }
        """
    )

    table.setFixedHeight(110)
    table.horizontalHeader().setStretchLastSection(True)
    table.horizontalHeader().setSectionResizeMode(
        QHeaderView.ResizeMode.ResizeToContents
    )
    table.horizontalHeader().setStretchLastSection(
        True
    )
    table.setHorizontalScrollBarPolicy(
        Qt.ScrollBarPolicy.ScrollBarAlwaysOff
    )

    panel = QWidget()
    layout = QVBoxLayout(panel)
    layout.setSpacing(0)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.addWidget(table)
    legend = QLabel(
        "[ SIGNAL LEGEND ]\n"
        "W=Weak   M=Medium   S=Strong\n"
        "A=Active   P=Persistent   L=Long"
    )

    legend.setAlignment(
        Qt.AlignmentFlag.AlignCenter
    )

    legend.setStyleSheet(
        """
        QLabel {
            color: #3da5ff;
            background-color: #111111;
            border: 2px solid #0078ff;
            border-radius: 6px;
            padding: 8px;
            font-size: 10px;
            font-weight: bold;
        }
        """
    )
    layout.addWidget(legend)
    legend.setMaximumHeight(80)
    #panel.setMaximumHeight(150)
    return panel, table


def update_signal_panel(
        table,
        peaks,
        classify_signal
):
    table.setRowCount(
        len(peaks)
    )

    for row, (freq, power) in enumerate(peaks):
        table.setItem(
            row,
            0,
            QTableWidgetItem(
                f"{freq:.2f}"
            )
        )

        history_count, age_seconds = (
            update_signal_history(
                freq
            )
        )

        occupancy_percent = (
            get_occupancy_percent(
                freq
            )
        )

        feature = extract_features(
            frequency=freq,
            peak_power=power,
            average_power=power,
            bandwidth_khz=0.0,
            occupancy_percent=occupancy_percent,
            age_seconds=age_seconds,
            strength="",
            persistence=""
        )

        feature_store.update(
            feature
        )

        signal_type, strength, persistence = (
            classify_signal(
                power,
                freq,
                history_count
            )
        )

        feature.strength = strength
        feature.persistence = persistence

        if age_seconds < 60:
            age_text = f"{age_seconds}s"
        else:
            age_text = f"{age_seconds // 60}m"

        display_type = signal_type

        if persistence is not None:
            display_type += f" [{persistence}]"

        type_item = QTableWidgetItem(display_type)
        table.setItem(
            row,
            1,
            type_item
        )

        # COLORED ITEMS ================
        if "BC" in signal_type:
            type_item.setForeground(QColor("#00ff66"))

        elif signal_type == "NOAA":
            type_item.setForeground(QColor("#00ffff"))

        elif signal_type == "WX":
            type_item.setForeground(QColor("#66ffff"))

        elif "AIRBND" in signal_type:
            type_item.setForeground(QColor("#ffff00"))

        elif "2m" in signal_type:
            type_item.setForeground(QColor("#ff9900"))

        elif "70cm" in signal_type:
            type_item.setForeground(QColor("#ff66ff"))

        elif signal_type == "GMRS":
            type_item.setForeground(QColor("#ff4444"))
        # ==============================

        table.setItem(
            row,
            2,
            QTableWidgetItem(strength)
        )

        table.setItem(
            row,
            3,
            QTableWidgetItem(age_text)
        )

        for column in range(4):

            item = table.item(row, column)

            if item is not None:
                item.setTextAlignment(
                    Qt.AlignmentFlag.AlignCenter
                )