import numpy as np

from PyQt6.QtCore import QRectF
from PyQt6.QtTest import QTest

import SURVEY.survey_manager as survey

from SURVEY.survey_manager import (
    clear_survey,
    build_progress_bar,
    generate_frequencies,
    rank_frequencies,
    build_status_text,
    build_results_text,
    get_best_frequency
)

from UI.survey_popup import SurveyPopup


class SurveyController:

    def __init__(
            self,
            survey_timer,
            survey_label,
            freq_input,
            start_freq_input,
            stop_freq_input,
            step_freq_input,
            heatmap_img,
            heatmap_plot,
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

        self.tune_frequency_callback = tune_frequency_callback
        self.get_occupancy_callback = get_occupancy_callback

        self.survey_popup = None
        self.latest_survey_results_text = ""
        self.last_survey_settings = None
        self.occupancy_percent = 0

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

        recommended_frequency, recommended_occupancy = (
            get_best_frequency(
                survey.survey_results
            )
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

            sorted_results = rank_frequencies(
                survey.survey_results
            )

            recommended_frequency, recommended_occupancy = (
                get_best_frequency(
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
                recommended_occupancy
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

        current_occupancy = (
            self.get_occupancy_callback()
        )

        survey.survey_results[frequency] = round(
            float(current_occupancy),
            1
        )

        survey.current_survey_index += 1