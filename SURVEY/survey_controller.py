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
