import unittest
from unittest.mock import Mock, patch

import SURVEY.survey_manager as survey
from SURVEY.survey_controller import SurveyController


class SurveyControllerAutoTuneTests(unittest.TestCase):

    def setUp(self):
        self.controller = SurveyController.__new__(
            SurveyController
        )
        self.controller.freq_input = Mock()
        self.controller.survey_label = Mock()
        self.controller.decision_mode_combo = Mock()
        self.controller.decision_mode_combo.currentText.return_value = (
            "Smart Recommendation"
        )
        self.controller.recommended_line = Mock()
        self.controller.heatmap_plot = Mock()
        self.controller.tune_frequency_callback = Mock()
        self.controller.feature_store = Mock()

    @patch(
        "SURVEY.survey_controller.show_survey_notice"
    )
    @patch(
        "SURVEY.survey_controller.make_decision"
    )
    def test_auto_tune_reports_already_at_recommendation(
            self,
            make_decision,
            show_survey_notice
    ):
        self.controller.freq_input.text.return_value = "88.0"
        make_decision.return_value = {
            "frequency": 88.0
        }

        with patch.dict(
                survey.survey_results,
                {88.0: 10.0},
                clear=True
        ):
            self.controller.auto_tune_best()

        show_survey_notice.assert_called_once_with(
            self.controller.survey_label,
            "Already at recommendation",
            "Receiver center is already 88.0 MHz.",
            tone="success"
        )
        self.controller.tune_frequency_callback.assert_not_called()

    @patch(
        "SURVEY.survey_controller.show_survey_notice"
    )
    @patch(
        "SURVEY.survey_controller.make_decision"
    )
    def test_auto_tune_reports_tune_request(
            self,
            make_decision,
            show_survey_notice
    ):
        self.controller.freq_input.text.return_value = "100.0"
        make_decision.return_value = {
            "frequency": 88.0
        }

        with patch.dict(
                survey.survey_results,
                {88.0: 10.0},
                clear=True
        ):
            self.controller.auto_tune_best()

        self.controller.freq_input.setText.assert_called_once_with(
            "88.0"
        )
        show_survey_notice.assert_called_once_with(
            self.controller.survey_label,
            "Auto-tune requested",
            "Tuning receiver to 88.0 MHz.",
            tone="info"
        )
        self.controller.tune_frequency_callback.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
