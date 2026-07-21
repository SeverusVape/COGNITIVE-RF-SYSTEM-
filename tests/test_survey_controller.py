import unittest
from unittest.mock import Mock, patch

import SURVEY.survey_manager as survey
from SURVEY.survey_controller import (
    SURVEY_STATUS_TIMEOUT_MS,
    SurveyController
)
from UI.survey_panel import SurveyStatusState


class SurveyControllerStatusTests(unittest.TestCase):

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
        self.controller.get_center_frequency_callback = Mock(
            return_value=None
        )
        self.controller.feature_store = Mock()
        self.controller.pending_auto_tune_frequency = None
        self.controller.status_revision = 0
        self.controller.status_timer = Mock()
        self.controller.survey_timer = Mock()
        self.controller.survey_timer.isActive.return_value = False

        self.previous_best_frequency = survey.best_frequency
        survey.best_frequency = None
        self.addCleanup(
            setattr,
            survey,
            "best_frequency",
            self.previous_best_frequency
        )

    @patch(
        "SURVEY.survey_controller.show_survey_status"
    )
    def test_no_survey_data_state(
            self,
            show_survey_status
    ):
        self.controller._show_persistent_status()

        show_survey_status.assert_called_once_with(
            self.controller.survey_label,
            SurveyStatusState.NO_SURVEY_DATA
        )

    @patch(
        "SURVEY.survey_controller.show_survey_status"
    )
    def test_recommendation_available_without_confirmed_center(
            self,
            show_survey_status
    ):
        survey.best_frequency = 88.0

        self.controller._show_persistent_status()

        show_survey_status.assert_called_once_with(
            self.controller.survey_label,
            SurveyStatusState.RECOMMENDATION_AVAILABLE,
            recommended_frequency=88.0
        )

    @patch(
        "SURVEY.survey_controller.show_survey_status"
    )
    def test_manual_tune_on_recommendation(
            self,
            show_survey_status
    ):
        survey.best_frequency = 88.0
        self.controller.get_center_frequency_callback.return_value = (
            88e6
        )

        self.controller.handle_tune_success(
            88e6
        )

        show_survey_status.assert_called_once_with(
            self.controller.survey_label,
            SurveyStatusState.ON_RECOMMENDED_CHANNEL,
            current_frequency=88.0,
            recommended_frequency=88.0
        )

    @patch(
        "SURVEY.survey_controller.show_survey_status"
    )
    def test_manual_tune_off_recommendation(
            self,
            show_survey_status
    ):
        survey.best_frequency = 88.0
        self.controller.get_center_frequency_callback.return_value = (
            125e6
        )

        self.controller.handle_tune_success(
            125e6
        )

        show_survey_status.assert_called_once_with(
            self.controller.survey_label,
            SurveyStatusState.OFF_RECOMMENDED_CHANNEL,
            current_frequency=125.0,
            recommended_frequency=88.0
        )

    @patch(
        "SURVEY.survey_controller.show_survey_status"
    )
    def test_survey_tune_success_preserves_progress_status(
            self,
            show_survey_status
    ):
        self.controller.survey_timer.isActive.return_value = True
        survey.best_frequency = None

        self.controller.handle_tune_success(
            89e6
        )

        show_survey_status.assert_not_called()

    @patch(
        "SURVEY.survey_controller.show_survey_status"
    )
    def test_auto_tune_success_returns_to_persistent_state(
            self,
            show_survey_status
    ):
        survey.best_frequency = 88.0
        self.controller.pending_auto_tune_frequency = 88.0
        self.controller.get_center_frequency_callback.return_value = (
            88e6
        )

        self.controller.handle_tune_success(
            88e6
        )

        show_survey_status.assert_called_once_with(
            self.controller.survey_label,
            SurveyStatusState.AUTO_TUNE_COMPLETE,
            current_frequency=88.0
        )
        self.controller.status_timer.start.assert_called_once_with(
            SURVEY_STATUS_TIMEOUT_MS
        )

        revision = self.controller.status_revision
        self.controller._finish_temporary_status(
            revision
        )

        self.assertEqual(
            show_survey_status.call_args_list[-1].args[1],
            SurveyStatusState.ON_RECOMMENDED_CHANNEL
        )

    @patch(
        "SURVEY.survey_controller.show_survey_status"
    )
    @patch(
        "SURVEY.survey_controller.make_decision"
    )
    def test_auto_tune_already_on_recommendation(
            self,
            make_decision,
            show_survey_status
    ):
        make_decision.return_value = {
            "frequency": 88.0
        }
        self.controller.get_center_frequency_callback.return_value = (
            88e6
        )

        with patch.dict(
                survey.survey_results,
                {88.0: 10.0},
                clear=True
        ):
            self.controller.auto_tune_best()

        show_survey_status.assert_called_once_with(
            self.controller.survey_label,
            SurveyStatusState.ALREADY_ON_RECOMMENDED_CHANNEL,
            current_frequency=88.0
        )
        self.controller.tune_frequency_callback.assert_not_called()

    @patch(
        "SURVEY.survey_controller.show_survey_status"
    )
    def test_auto_tune_unavailable(
            self,
            show_survey_status
    ):
        with patch.dict(
                survey.survey_results,
                {},
                clear=True
        ):
            self.controller.auto_tune_best()

        show_survey_status.assert_called_once_with(
            self.controller.survey_label,
            SurveyStatusState.AUTO_TUNE_UNAVAILABLE
        )

    @patch(
        "SURVEY.survey_controller.show_survey_status"
    )
    def test_auto_tune_failure(
            self,
            show_survey_status
    ):
        survey.best_frequency = 88.0
        self.controller.pending_auto_tune_frequency = 88.0

        self.controller.handle_auto_tune_failure(
            88e6,
            "Unable to tune SDR."
        )

        show_survey_status.assert_called_once_with(
            self.controller.survey_label,
            SurveyStatusState.AUTO_TUNE_FAILED,
            message="Unable to tune SDR."
        )

    @patch(
        "SURVEY.survey_controller.show_survey_status"
    )
    def test_receiver_error_cancels_temporary_feedback(
            self,
            show_survey_status
    ):
        survey.best_frequency = 88.0
        self.controller.pending_auto_tune_frequency = 88.0
        self.controller._show_temporary_status(
            SurveyStatusState.AUTO_TUNE_COMPLETE,
            current_frequency=88.0
        )
        stale_revision = self.controller.status_revision

        self.controller.handle_receiver_error()
        call_count = show_survey_status.call_count

        self.controller._finish_temporary_status(
            stale_revision
        )

        self.assertIsNone(
            self.controller.pending_auto_tune_frequency
        )
        self.assertEqual(
            show_survey_status.call_count,
            call_count
        )
        self.assertEqual(
            show_survey_status.call_args.args[1],
            SurveyStatusState.RECOMMENDATION_AVAILABLE
        )

    @patch(
        "SURVEY.survey_controller.show_survey_status"
    )
    def test_newer_tune_cancels_temporary_transition(
            self,
            show_survey_status
    ):
        survey.best_frequency = 88.0
        self.controller.get_center_frequency_callback.return_value = (
            88e6
        )
        self.controller._show_temporary_status(
            SurveyStatusState.AUTO_TUNE_COMPLETE,
            current_frequency=88.0
        )
        stale_revision = self.controller.status_revision

        self.controller.get_center_frequency_callback.return_value = (
            125e6
        )
        self.controller.handle_tune_success(
            125e6
        )
        call_count = show_survey_status.call_count

        self.controller._finish_temporary_status(
            stale_revision
        )

        self.assertEqual(
            show_survey_status.call_count,
            call_count
        )
        self.assertEqual(
            show_survey_status.call_args.args[1],
            SurveyStatusState.OFF_RECOMMENDED_CHANNEL
        )

    def test_clear_survey_cancels_temporary_message(self):
        self.controller.survey_timer = Mock()
        self.controller.survey_results_button = Mock()
        self.controller.survey_popup = None
        self.controller.heatmap_img = Mock()
        self.controller.top_frequencies_label = Mock()
        self.controller.last_survey_settings = (88.0, 92.0, 1.0)
        survey.best_frequency = 88.0

        self.controller._show_temporary_status(
            SurveyStatusState.AUTO_TUNE_COMPLETE,
            current_frequency=88.0
        )
        stale_revision = self.controller.status_revision

        self.controller.clear_current_survey()
        render_count = (
            self.controller.survey_label.setHtml.call_count
        )

        self.controller._finish_temporary_status(
            stale_revision
        )

        self.assertIsNone(survey.best_frequency)
        self.assertEqual(
            self.controller.survey_label.setHtml.call_count,
            render_count
        )
        self.assertIn(
            "NO SURVEY DATA",
            self.controller.survey_label.setHtml.call_args.args[0]
        )

    @patch(
        "SURVEY.survey_controller.show_survey_status"
    )
    @patch(
        "SURVEY.survey_controller.build_results_html",
        return_value="report"
    )
    @patch(
        "SURVEY.survey_controller.make_decision"
    )
    def test_survey_completion_sets_active_recommendation(
            self,
            make_decision,
            build_results_html,
            show_survey_status
    ):
        self.controller.survey_timer = Mock()
        self.controller.survey_results_button = Mock()
        self.controller._update_heatmap_and_history = Mock()
        self.controller.auto_tune_best = Mock()
        make_decision.return_value = {
            "frequency": 88.0,
            "occupancy": 10.0
        }

        with patch.dict(
                survey.survey_results,
                {88.0: 10.0},
                clear=True
        ), patch.dict(
                survey.survey_metrics,
                {88.0: {}},
                clear=True
        ):
            self.controller._handle_survey_completion()

        self.assertEqual(survey.best_frequency, 88.0)
        show_survey_status.assert_called_once_with(
            self.controller.survey_label,
            SurveyStatusState.RECOMMENDATION_AVAILABLE,
            recommended_frequency=88.0
        )
        self.controller.auto_tune_best.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
