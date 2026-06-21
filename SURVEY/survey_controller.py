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
