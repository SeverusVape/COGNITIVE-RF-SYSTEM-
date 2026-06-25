import numpy as np
import pyqtgraph as pg

from PyQt6.QtCore import QRectF
from PyQt6.QtTest import QTest

import SURVEY.survey_manager as survey

from SURVEY.survey_manager import (
    clear_survey,
    build_progress_bar,
    generate_frequencies,
    rank_frequencies,
    build_status_text,
    build_results_text
)

from SURVEY.decision_engine import (
    make_decision,
)

from UI.survey_popup import SurveyPopup


class SurveyController:

    def __init__(
            self,
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
            tune_frequency_callback,
            get_occupancy_callback
    ):
        self.survey_timer = survey_timer
        self.survey_label = survey_label
        self.freq_input = freq_input

        self.start_freq_input = start_freq_input
        self.stop_freq_input = stop_freq_input
        self.step_freq_input = step_freq_input

        self.heatmap_img = heatmap_img
        self.heatmap_plot = heatmap_plot
        self.recommended_line = recommended_line

        self.tune_frequency_callback = tune_frequency_callback
        self.get_occupancy_callback = get_occupancy_callback

        self.survey_popup = None
        self.latest_survey_results_text = ""
        self.last_survey_settings = None
        self.occupancy_percent = 0

        self.top_frequencies_label = (
            top_frequencies_label
        )

        self.recommended_text = pg.TextItem(
            color="red"
        )

        self.recommended_arrow = pg.TextItem(
            color="red"
        )

        self.recommended_text.setAnchor(
            (0.5, 0)
        )

        self.recommended_arrow.setAnchor(
            (0.5, 0)
        )

        self.heatmap_plot.addItem(
            self.recommended_text
        )

        self.heatmap_plot.addItem(
            self.recommended_arrow
        )

        self.recommended_text.hide()
        self.recommended_arrow.hide()

        self.decision_mode = "FREE"
        self.decision_mode_combo = (
            decision_mode_combo
        )

    def clear_current_survey(self):
        self.survey_timer.stop()

        survey.survey_frequencies = []
        survey.survey_results.clear()
        survey.current_survey_index = 0


        clear_survey(
            self.survey_label
        )

    def auto_tune_best(self):

        current_frequency = float(
            self.freq_input.text()
        )

        if len(survey.survey_results) == 0:
            print(
                "No survey results"
            )

            return

        mode_text = self.decision_mode_combo.currentText()

        if mode_text == "Find Free Channel":
            self.decision_mode = "FREE"

        elif mode_text == "Find Active Signal":
            self.decision_mode = "ACTIVE"
        else:
            self.decision_mode = "SMART"

        recommended_frequency, recommended_occupancy = (
            make_decision(
                self.decision_mode,
                survey.survey_results
            )
        )

        heatmap_height = max(
            1,
            len(survey.heatmap_history)
        )

        self.recommended_line.setData(
            [recommended_frequency, recommended_frequency],
            [0, heatmap_height]
        )

        self.recommended_text.setText(
            "RCMND"
        )

        self.recommended_arrow.setText(
            "▼"
        )


        text_y = heatmap_height * 1.22
        arrow_y = heatmap_height * 1.13

        self.recommended_text.setPos(
            recommended_frequency,
            text_y
        )

        self.recommended_arrow.setPos(
            recommended_frequency,
            arrow_y
        )

        self.recommended_text.show()

        self.recommended_arrow.show()

        self.heatmap_plot.setYRange(
            0,
            heatmap_height * 1.25,
            padding=0
        )

        if abs(
                current_frequency
                -
                recommended_frequency
        ) < 0.1:
            print(
                "Already on best frequency"
            )

            return

        self.freq_input.setText(
            str(recommended_frequency)
        )

        self.tune_frequency_callback()

        print(
            "Recommended:",
            recommended_frequency,
            recommended_occupancy
        )

    def start_survey(self):

        # clean survey state
        survey.survey_frequencies = []
        survey.survey_results.clear()
        survey.current_survey_index = 0

        current_survey_settings = (
            float(self.start_freq_input.text()),
            float(self.stop_freq_input.text()),
            float(self.step_freq_input.text())
        )

        if (
                self.last_survey_settings is not None
                and
                current_survey_settings
                !=
                self.last_survey_settings
        ):
            survey.heatmap_history.clear()

            print(
                "Survey range changed - history cleared"
            )

        self.last_survey_settings = (
            current_survey_settings
        )

        start_mhz = current_survey_settings[0]
        stop_mhz = current_survey_settings[1]
        step_mhz = current_survey_settings[2]

        survey.survey_frequencies = (
            generate_frequencies(
                start_mhz,
                stop_mhz,
                step_mhz
            )
        )

        self.survey_label.setText(
            f"SURVEY STATUS\n\n"
            f"Frequency:\n"
            f"{survey.survey_frequencies[0]:.1f} MHz\n\n"
            f"Point:\n"
            f"0 / {len(survey.survey_frequencies)}\n\n"
            f"Progress:\n"
            f"0%"
        )

        self.survey_timer.start(
            3000
        )

    def survey_step(self):

        if survey.current_survey_index >= len(
                survey.survey_frequencies
        ):
            self.survey_timer.stop()

            print(
                "Survey Complete"
            )

            mode_text = self.decision_mode_combo.currentText()

            if mode_text == "Find Free Channel":

                self.decision_mode = "FREE"

            elif mode_text == "Find Active Signal":

                self.decision_mode = "ACTIVE"

            else:

                self.decision_mode = "SMART"

            sorted_results = rank_frequencies(
                survey.survey_results
            )

            recommended_frequency, recommended_occupancy = (
                make_decision(
                    self.decision_mode,
                    survey.survey_results
                )
            )

            print(
                "Best:",
                recommended_frequency,
                recommended_occupancy
            )

            occupancies = []

            for freq in survey.survey_frequencies:
                occupancies.append(
                    survey.survey_results[freq]
                )

            survey.heatmap_history.append(
                occupancies
            )

            if len(survey.heatmap_history) > 100:
                survey.heatmap_history.pop(0)

            heatmap_data = np.array(
                survey.heatmap_history
            )

            average_by_frequency = np.mean(
                heatmap_data,
                axis=0
            )

            top_indices = np.argsort(
                average_by_frequency
            )[-3:][::-1]

            persistent_text = (
                "MOST ACTIVE (HISTORY)\n\n"
            )

            for rank, index in enumerate(
                    top_indices,
                    start=1
            ):
                freq = survey.survey_frequencies[
                    index
                ]

                avg_occ = round(
                    average_by_frequency[index],
                    1
                )

                persistent_text += (
                    f"{rank}. "
                    f"{freq:.1f} MHz   "
                    f"{avg_occ}%\n"
                )

            self.top_frequencies_label.setText(
                persistent_text
            )

            self.heatmap_img.setImage(
                heatmap_data,
                autoLevels=False
            )

            self.heatmap_img.setRect(
                QRectF(
                    min(survey.survey_frequencies),
                    0,
                    max(survey.survey_frequencies)
                    -
                    min(survey.survey_frequencies),
                    len(survey.heatmap_history)
                )
            )

            self.heatmap_img.setLevels(
                (
                    np.min(heatmap_data),
                    np.max(heatmap_data)
                )
            )

            self.heatmap_img.setRect(
                QRectF(
                    survey.survey_frequencies[0],
                    0,
                    survey.survey_frequencies[-1]
                    - survey.survey_frequencies[0],
                    len(survey.heatmap_history)
                )
            )

            self.heatmap_plot.setLabel(
                "bottom",
                "Frequency",
                units="MHz"
            )

            highest_frequency = sorted_results[0][0]
            highest_occupancy = sorted_results[0][1]

            average_occupancy = round(
                sum(survey.survey_results.values())
                / len(survey.survey_results),
                1
            )

            points_scanned = len(
                survey.survey_results
            )

            results_text = build_results_text(
                sorted_results,
                points_scanned,
                average_occupancy,
                recommended_frequency,
                recommended_occupancy,
                self.decision_mode
            )

            self.latest_survey_results_text = (
                results_text
            )

            self.survey_popup = SurveyPopup(
                self.latest_survey_results_text
            )

            self.auto_tune_best()

            progress_bar = build_progress_bar(
                100
            )

            self.survey_label.setText(
                "SURVEY STATUS\n\n"
                "✓ COMPLETE\n\n"

                f"RECOMMENDED:\n\n"
                f"{recommended_frequency:.1f} MHz\n\n"

                f"Points:\n"
                f"{len(survey.survey_results)}\n\n"

                "Progress:\n"
                f"{progress_bar}\n"
                "100%\n\n"

                "[ VIEW RESULTS ]\n"
            )


            print(
                "Popup prepared"
            )

            print(
                "Results text generated"
            )

            print(
                "Average occupancy:",
                average_occupancy
            )

            print(
                "Heatmap rows:",
                len(survey.heatmap_history)
            )

            return

        frequency = survey.survey_frequencies[
            survey.current_survey_index
        ]

        progress_percent = int(
            (survey.current_survey_index + 1)
            / len(survey.survey_frequencies)
            * 100
        )

        progress_bar = build_progress_bar(
            progress_percent
        )

        print(
            "Survey point:",
            survey.current_survey_index + 1,
            "/",
            len(survey.survey_frequencies)
        )

        survey_text = build_status_text(
            frequency,
            survey.current_survey_index + 1,
            len(survey.survey_frequencies),
            progress_percent,
            progress_bar
        )

        self.survey_label.setText(
            survey_text
        )

        self.freq_input.setText(
            str(frequency)
        )

        self.tune_frequency_callback()

        QTest.qWait(
            500
        )

        measurement = (
            self.get_occupancy_callback()
        )

        current_occupancy = measurement[
            "occupancy"
        ]

        survey.survey_results[frequency] = round(
            float(current_occupancy),
            1
        )

        survey.survey_metrics[frequency] = measurement

        # TEST CHECK
        print(
            frequency,
            survey.survey_metrics[frequency]
        )

        survey.current_survey_index += 1