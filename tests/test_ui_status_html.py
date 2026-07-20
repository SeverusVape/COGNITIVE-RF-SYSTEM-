import unittest

from UI.status_panel import (
    build_status_message_html
)
from UI.survey_panel import (
    build_empty_survey_html,
    build_survey_complete_html,
    build_survey_notice_html,
    build_survey_progress_html
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

    def test_survey_complete_contains_recommendation(self):
        complete_html = build_survey_complete_html(
            recommended_frequency=90.0,
            points_scanned=5
        )

        self.assertIn(
            "90.0 MHz",
            complete_html
        )

        self.assertIn(
            "5 points scanned",
            complete_html
        )

    def test_empty_state_explains_next_action(self):
        empty_html = build_empty_survey_html()

        self.assertIn(
            "Run a survey",
            empty_html
        )


if __name__ == "__main__":
    unittest.main()
