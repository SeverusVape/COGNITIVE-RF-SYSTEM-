import unittest
from unittest.mock import Mock, patch

import SURVEY.survey_manager as survey
from SURVEY.survey_controller import (
    SURVEY_STATUS_TIMEOUT_MS,
    SurveyController
)
from UI.survey_panel import SurveyStatusState
from UTILS.config import SURVEY_SETTLING_DELAY_MS


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
        self.controller.survey_active = False
        self.controller.shutting_down = False
        self.controller.status_revision = 0
        self.controller.status_timer = Mock()
        self.controller.survey_timer = Mock()
        self.controller.survey_timer.isActive.return_value = False

        self.previous_best_frequency = survey.best_frequency
        self.previous_survey_frequencies = list(
            survey.survey_frequencies
        )
        self.previous_survey_results = dict(
            survey.survey_results
        )
        self.previous_survey_metrics = dict(
            survey.survey_metrics
        )
        self.previous_survey_index = (
            survey.current_survey_index
        )

        survey.best_frequency = None
        survey.survey_frequencies = []
        survey.survey_results.clear()
        survey.survey_metrics.clear()
        survey.current_survey_index = 0

        self.addCleanup(
            self._restore_survey_state
        )

    def _restore_survey_state(self):
        survey.best_frequency = self.previous_best_frequency
        survey.survey_frequencies = (
            self.previous_survey_frequencies
        )
        survey.survey_results.clear()
        survey.survey_results.update(
            self.previous_survey_results
        )
        survey.survey_metrics.clear()
        survey.survey_metrics.update(
            self.previous_survey_metrics
        )
        survey.current_survey_index = (
            self.previous_survey_index
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
        self.controller.survey_timer.isActive.return_value = False
        self.controller.survey_active = True
        survey.survey_frequencies = [89.0]
        survey.current_survey_index = 0
        survey.best_frequency = None

        self.controller.handle_tune_success(
            89e6
        )

        show_survey_status.assert_not_called()
        self.controller.survey_timer.start.assert_called_once_with(
            SURVEY_SETTLING_DELAY_MS
        )

    def test_unrelated_tune_confirmation_does_not_start_settling(self):
        self.controller.survey_active = True
        self.controller.survey_timer.isActive.return_value = False
        survey.survey_frequencies = [89.0]
        survey.current_survey_index = 0

        self.controller.handle_tune_success(
            125e6
        )

        self.controller.survey_timer.start.assert_not_called()

    def test_survey_step_requests_tune_without_measuring(self):
        self.controller.survey_active = True
        self.controller.get_occupancy_callback = Mock()
        survey.survey_frequencies = [88.0]
        survey.current_survey_index = 0

        self.controller.survey_step()

        self.controller.freq_input.setText.assert_called_once_with(
            "88.0"
        )
        self.controller.tune_frequency_callback.assert_called_once_with()
        self.controller.get_occupancy_callback.assert_not_called()

    @patch(
        "SURVEY.survey_controller.build_feature_snapshot",
        return_value={}
    )
    def test_measurement_is_stored_before_next_tune(
            self,
            build_feature_snapshot
    ):
        self.controller.survey_active = True
        self.controller.get_occupancy_callback = Mock(
            return_value={
                "occupancy": 12.5,
                "max_power": 55.0,
                "average_power": 24.0
            }
        )
        self.controller.survey_step = Mock()
        survey.survey_frequencies = [88.0, 89.0]
        survey.current_survey_index = 0

        self.controller.collect_survey_measurement()

        self.assertEqual(
            survey.survey_results[88.0],
            12.5
        )
        self.assertIn(
            88.0,
            survey.survey_metrics
        )
        self.assertEqual(
            survey.current_survey_index,
            1
        )
        self.controller.survey_step.assert_called_once_with()

    @patch(
        "SURVEY.survey_controller.build_feature_snapshot",
        return_value={}
    )
    def test_final_measurement_completes_before_another_tune(
            self,
            build_feature_snapshot
    ):
        self.controller.survey_active = True
        self.controller.get_occupancy_callback = Mock(
            return_value={
                "occupancy": 8.0,
                "max_power": 50.0,
                "average_power": 20.0
            }
        )
        self.controller._handle_survey_completion = Mock()
        self.controller.survey_step = Mock()
        survey.survey_frequencies = [88.0]
        survey.current_survey_index = 0

        self.controller.collect_survey_measurement()

        self.assertEqual(
            survey.survey_results[88.0],
            8.0
        )
        self.assertEqual(
            survey.current_survey_index,
            1
        )
        self.controller._handle_survey_completion.assert_called_once_with()
        self.controller.survey_step.assert_not_called()

    @patch(
        "SURVEY.survey_controller.show_survey_notice"
    )
    def test_survey_tune_failure_stops_sequence(
            self,
            show_survey_notice
    ):
        self.controller.survey_active = True

        self.controller.handle_auto_tune_failure(
            88e6,
            "Unable to tune SDR."
        )

        self.assertFalse(
            self.controller.survey_active
        )
        self.controller.survey_timer.stop.assert_called()
        show_survey_notice.assert_called_once_with(
            self.controller.survey_label,
            "Survey tune failed",
            "Unable to tune SDR.",
            tone="error"
        )

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
        self.controller.get_occupancy_callback = Mock()
        self.controller.survey_active = True
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
        self.controller.collect_survey_measurement()

        self.assertIsNone(survey.best_frequency)
        self.assertFalse(self.controller.survey_active)
        self.controller.get_occupancy_callback.assert_not_called()
        self.assertEqual(
            self.controller.survey_label.setHtml.call_count,
            render_count
        )
        self.assertIn(
            "NO SURVEY DATA",
            self.controller.survey_label.setHtml.call_args.args[0]
        )

    def test_shutdown_cancels_pending_survey_sequence(self):
        self.controller.survey_active = True

        self.controller.begin_shutdown()

        self.assertTrue(self.controller.shutting_down)
        self.assertFalse(self.controller.survey_active)
        self.controller.survey_timer.stop.assert_called()

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
