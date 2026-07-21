import unittest

from UI.status_panel import (
    build_status_message_html
)
from UI.survey_panel import (
    SurveyStatusState,
    build_empty_survey_html,
    build_survey_notice_html,
    build_survey_progress_html,
    build_survey_status_html
)


class UIStatusHtmlTests(
        unittest.TestCase
):

    def test_status_message_escapes_device_error(self):
        status_html = build_status_message_html(
            "Connection error",
            "<USB unavailable>",
            tone="error"
        )

        self.assertIn(
            "&lt;USB unavailable&gt;",
            status_html
        )

        self.assertNotIn(
            "<USB unavailable>",
            status_html
        )

    def test_survey_notice_escapes_message(self):
        notice_html = build_survey_notice_html(
            "Invalid input",
            "Start < Stop",
            tone="error"
        )

        self.assertIn(
            "Start &lt; Stop",
            notice_html
        )

    def test_survey_progress_clamps_percentage(self):
        progress_html = build_survey_progress_html(
            frequency=100.0,
            current_point=1,
            total_points=5,
            progress_percent=120
        )

        self.assertIn(
            "100%",
            progress_html
        )

        self.assertIn(
            "1 / 5",
            progress_html
        )

    def test_recommendation_available_contains_frequency(self):
        status_html = build_survey_status_html(
            SurveyStatusState.RECOMMENDATION_AVAILABLE,
            recommended_frequency=90.0
        )

        self.assertIn(
            "90.0 MHz",
            status_html
        )

        self.assertIn(
            "RECOMMENDATION AVAILABLE",
            status_html
        )

    def test_persistent_receiver_status_copy(self):
        on_status = build_survey_status_html(
            SurveyStatusState.ON_RECOMMENDED_CHANNEL,
            current_frequency=88.0
        )
        off_status = build_survey_status_html(
            SurveyStatusState.OFF_RECOMMENDED_CHANNEL,
            current_frequency=125.0,
            recommended_frequency=88.0
        )

        self.assertIn(
            "ON RECOMMENDED CHANNEL",
            on_status
        )
        self.assertIn(
            "Current center: 88.0 MHz",
            on_status
        )
        self.assertIn(
            "OFF RECOMMENDED CHANNEL",
            off_status
        )
        self.assertIn(
            "Current center: 125.0 MHz",
            off_status
        )
        self.assertIn(
            "Recommended: 88.0 MHz",
            off_status
        )

    def test_temporary_auto_tune_status_copy(self):
        complete_status = build_survey_status_html(
            SurveyStatusState.AUTO_TUNE_COMPLETE,
            current_frequency=88.0
        )
        already_status = build_survey_status_html(
            SurveyStatusState.ALREADY_ON_RECOMMENDED_CHANNEL,
            current_frequency=88.0
        )
        unavailable_status = build_survey_status_html(
            SurveyStatusState.AUTO_TUNE_UNAVAILABLE
        )
        failed_status = build_survey_status_html(
            SurveyStatusState.AUTO_TUNE_FAILED,
            message="USB <error>"
        )

        self.assertIn("AUTO-TUNE COMPLETE", complete_status)
        self.assertIn(
            "Receiver tuned to 88.0 MHz.",
            complete_status
        )
        self.assertIn(
            "ALREADY ON RECOMMENDED CHANNEL",
            already_status
        )
        self.assertIn(
            "AUTO-TUNE UNAVAILABLE",
            unavailable_status
        )
        self.assertIn("AUTO-TUNE FAILED", failed_status)
        self.assertIn("USB &lt;error&gt;", failed_status)

    def test_empty_state_explains_next_action(self):
        empty_html = build_empty_survey_html()

        self.assertIn(
            "Run a survey",
            empty_html
        )


if __name__ == "__main__":
    unittest.main()
