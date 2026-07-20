import unittest

from UI.survey_history_panel import (
    build_empty_survey_history_html,
    build_survey_history_html
)


class SurveyHistoryPanelTests(
        unittest.TestCase
):

    def test_history_describes_average_occupancy(self):
        history_html = build_survey_history_html(
            frequencies=[
                92.0,
                91.0
            ],
            average_occupancies=[
                15.4,
                12.8
            ],
            survey_count=3
        )

        self.assertIn(
            "SURVEY HISTORY",
            history_html
        )

        self.assertIn(
            "Average occupancy across 3 completed surveys",
            history_html
        )

        self.assertIn(
            "92.0 MHz",
            history_html
        )

        self.assertIn(
            "15.4%",
            history_html
        )

    def test_history_uses_singular_survey_context(self):
        history_html = build_survey_history_html(
            frequencies=[88.0],
            average_occupancies=[9.0],
            survey_count=1
        )

        self.assertIn(
            "1 completed survey",
            history_html
        )

    def test_empty_state_prompts_for_completed_survey(self):
        empty_html = build_empty_survey_history_html()

        self.assertIn(
            "Complete a survey to build history.",
            empty_html
        )


if __name__ == "__main__":
    unittest.main()
