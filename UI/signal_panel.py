from PyQt6.QtWidgets import (
    QTableWidget,
    QTableWidgetItem,
    QHeaderView
)

from PyQt6.QtCore import Qt

from PyQt6.QtGui import QFont

from SIGNALS.signal_history import (
    update_signal_history
)

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

    table.setFixedHeight(130)

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

    return table


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

        signal_type, strength, persistence = (
            classify_signal(
                power,
                freq,
                history_count
            )
        )

        if age_seconds < 60:
            age_text = f"{age_seconds}s"
        else:
            age_text = f"{age_seconds // 60}m"

        table.setItem(
            row,
            1,
            QTableWidgetItem(signal_type)
        )

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