import numpy as np

from PyQt6.QtCore import QTimer, QRectF
from PyQt6.QtTest import QTest

import SURVEY.survey_manager as survey

from SURVEY.survey_manager import (
    clear_survey,
    generate_frequencies,
    rank_frequencies,
    build_results_html
)

from SURVEY.decision_engine import (
    build_feature_snapshot,
    make_decision,
)

from UI.survey_popup import SurveyPopup
from UI.survey_history_panel import (
    show_empty_survey_history,
    update_survey_history
)
from UI.survey_panel import (
    SurveyStatusState,
    show_survey_notice,
    show_survey_progress,
    show_survey_status
)


SURVEY_STATUS_TIMEOUT_MS = 2500


class SurveyController:

    def __init__(
            self,
            survey_timer,
            survey_label,
            survey_results_button,
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
            get_occupancy_callback,
            get_center_frequency_callback,
            feature_store,
    ):
        self.survey_timer = survey_timer
        self.survey_label = survey_label
        self.survey_results_button = (
            survey_results_button
        )
        self.freq_input = freq_input

        self.start_freq_input = start_freq_input
        self.stop_freq_input = stop_freq_input
        self.step_freq_input = step_freq_input

        self.heatmap_img = heatmap_img
        self.heatmap_plot = heatmap_plot
        self.recommended_line = recommended_line

        self.tune_frequency_callback = tune_frequency_callback
        self.get_occupancy_callback = get_occupancy_callback
        self.get_center_frequency_callback = (
            get_center_frequency_callback
        )

        self.survey_popup = None
        self.latest_survey_results_html = ""

        self.survey_results_button.setVisible(
            False
        )
        self.last_survey_settings = None
        self.occupancy_percent = 0
        self.shutting_down = False
        self.pending_auto_tune_frequency = None
        self.status_revision = 0

        self.status_timer = QTimer()
        self.status_timer.setSingleShot(
            True
        )

        self.feature_store = feature_store

        self.top_frequencies_label = (
            top_frequencies_label
        )

        self.decision_mode = "FREE"
        self.decision_mode_combo = (
            decision_mode_combo
        )

    def begin_shutdown(self):
        self.shutting_down = True
        self.survey_timer.stop()
        self._cancel_status_transition()

    def show_results_popup(self):
        if self.latest_survey_results_html == "":
            return

        if self.survey_popup is not None:
            self.survey_popup.close()

        self.survey_popup = SurveyPopup(
            self.latest_survey_results_html
        )

        self.survey_popup.showMaximized()

    def auto_tune_best(self):
        self._cancel_status_transition()

        if len(survey.survey_results) == 0:
            self._show_temporary_status(
                SurveyStatusState.AUTO_TUNE_UNAVAILABLE
            )
            return

        mode_text = self.decision_mode_combo.currentText()

        if mode_text == "Find Free Channel":
            self.decision_mode = "FREE"

        elif mode_text == "Find Active Signal":
            self.decision_mode = "ACTIVE"
        else:
            self.decision_mode = "SMART"

        recommendation = make_decision(

            self.decision_mode,
            survey.survey_results,
            survey.survey_metrics,
            survey.heatmap_history,
            self.feature_store

        )

        recommended_frequency = recommendation[
            "frequency"
        ]

        if recommended_frequency is None:
            self._show_temporary_status(
                SurveyStatusState.AUTO_TUNE_UNAVAILABLE,
                message=(
                    "No valid recommended frequency is available."
                )
            )
            return

        survey.best_frequency = recommended_frequency

        heatmap_height = max(
            1,
            len(survey.heatmap_history)
        )

        self.recommended_line.setPos(
            recommended_frequency
        )

        self.recommended_line.show()

        self.heatmap_plot.setYRange(
            0,
            heatmap_height * 1.25,
            padding=0
        )

        confirmed_frequency_hz = (
            self.get_center_frequency_callback()
        )

        if confirmed_frequency_hz is not None:
            confirmed_frequency_mhz = (
                confirmed_frequency_hz / 1e6
            )

            if abs(
                    confirmed_frequency_mhz
                    - recommended_frequency
            ) < 0.1:
                self._show_temporary_status(
                    SurveyStatusState.
                    ALREADY_ON_RECOMMENDED_CHANNEL,
                    current_frequency=(
                        confirmed_frequency_mhz
                    )
                )
                return

        self.freq_input.setText(
            str(recommended_frequency)
        )

        self.pending_auto_tune_frequency = (
            recommended_frequency
        )

        self.tune_frequency_callback()

    def handle_tune_request(
            self,
            frequency_hz=None,
            refresh_persistent=False
    ):
        self._cancel_status_transition()

        if self.pending_auto_tune_frequency is None:
            if refresh_persistent:
                self._show_persistent_status()
            return

        if frequency_hz is None:
            self.pending_auto_tune_frequency = None
            if refresh_persistent:
                self._show_persistent_status()
            return

        requested_frequency_mhz = frequency_hz / 1e6

        if abs(
                requested_frequency_mhz
                - self.pending_auto_tune_frequency
        ) >= 0.1:
            self.pending_auto_tune_frequency = None

        if refresh_persistent:
            self._show_persistent_status()

    def handle_tune_success(
            self,
            frequency_hz
    ):
        self._cancel_status_transition()

        if self.survey_timer.isActive():
            return

        pending_frequency = (
            self.pending_auto_tune_frequency
        )

        frequency_mhz = frequency_hz / 1e6

        if pending_frequency is None:
            self._show_persistent_status()
            return

        self.pending_auto_tune_frequency = None

        if abs(
                frequency_mhz
                - pending_frequency
        ) >= 0.1:
            self._show_persistent_status()
            return

        self._show_temporary_status(
            SurveyStatusState.AUTO_TUNE_COMPLETE,
            current_frequency=frequency_mhz
        )

    def handle_auto_tune_failure(
            self,
            frequency_hz,
            message
    ):
        self._cancel_status_transition()

        pending_frequency = (
            self.pending_auto_tune_frequency
        )

        if pending_frequency is None:
            self._show_persistent_status()
            return

        self.pending_auto_tune_frequency = None

        frequency_mhz = frequency_hz / 1e6

        if abs(
                frequency_mhz
                - pending_frequency
        ) >= 0.1:
            self._show_persistent_status()
            return

        self._show_temporary_status(
            SurveyStatusState.AUTO_TUNE_FAILED,
            message=message
        )

    def handle_receiver_error(self):
        self._cancel_status_transition()
        self.pending_auto_tune_frequency = None
        self._show_persistent_status()

    def _show_persistent_status(self):
        self._cancel_status_transition()

        recommended_frequency = survey.best_frequency

        if recommended_frequency is None:
            show_survey_status(
                self.survey_label,
                SurveyStatusState.NO_SURVEY_DATA
            )
            return

        confirmed_frequency_hz = (
            self.get_center_frequency_callback()
        )

        if confirmed_frequency_hz is None:
            show_survey_status(
                self.survey_label,
                SurveyStatusState.RECOMMENDATION_AVAILABLE,
                recommended_frequency=recommended_frequency
            )
            return

        confirmed_frequency_mhz = (
            confirmed_frequency_hz / 1e6
        )

        if abs(
                confirmed_frequency_mhz
                - recommended_frequency
        ) < 0.1:
            state = (
                SurveyStatusState.ON_RECOMMENDED_CHANNEL
            )
        else:
            state = (
                SurveyStatusState.OFF_RECOMMENDED_CHANNEL
            )

        show_survey_status(
            self.survey_label,
            state,
            current_frequency=confirmed_frequency_mhz,
            recommended_frequency=recommended_frequency
        )

    def _show_temporary_status(
            self,
            state,
            **values
    ):
        self._cancel_status_transition()

        show_survey_status(
            self.survey_label,
            state,
            **values
        )

        revision = self.status_revision

        self.status_timer.timeout.connect(
            lambda: self._finish_temporary_status(
                revision
            )
        )

        self.status_timer.start(
            SURVEY_STATUS_TIMEOUT_MS
        )

    def _finish_temporary_status(
            self,
            revision
    ):
        if revision != self.status_revision:
            return

        self._show_persistent_status()

    def _cancel_status_transition(self):
        self.status_timer.stop()
        self.status_revision += 1

        try:
            self.status_timer.timeout.disconnect()
        except TypeError:
            pass

    def start_survey(self):

        self._cancel_status_transition()
        self.pending_auto_tune_frequency = None

        if self.shutting_down:
            return

        if self.survey_timer.isActive():
            show_survey_notice(
                self.survey_label,
                "Survey already running",
                "Wait for completion or select Clear Survey.",
                tone="warning"
            )
            return

        try:
            start_mhz = float(
                self.start_freq_input.text()
            )

            stop_mhz = float(
                self.stop_freq_input.text()
            )

            step_mhz = float(
                self.step_freq_input.text()
            )

        except ValueError:
            show_survey_notice(
                self.survey_label,
                "Invalid survey input",
                "Start, stop, and step values must be numbers.",
                tone="error"
            )
            return

        if step_mhz <= 0:
            show_survey_notice(
                self.survey_label,
                "Invalid step size",
                "Step size must be greater than 0 MHz.",
                tone="error"
            )
            return

        if stop_mhz <= start_mhz:
            show_survey_notice(
                self.survey_label,
                "Invalid frequency range",
                "Stop frequency must be greater than start frequency.",
                tone="error"
            )
            return

        new_frequencies = generate_frequencies(
            start_mhz,
            stop_mhz,
            step_mhz
        )

        if len(new_frequencies) == 0:
            show_survey_notice(
                self.survey_label,
                "Invalid survey",
                "The selected settings generated no frequencies.",
                tone="error"
            )
            return

        # clean survey state only after validation passes
        survey.survey_frequencies = []
        survey.survey_results.clear()
        survey.survey_metrics.clear()
        survey.current_survey_index = 0

        current_survey_settings = (
            start_mhz,
            stop_mhz,
            step_mhz
        )

        settings_changed = (
                self.last_survey_settings is not None
                and
                current_survey_settings
                !=
                self.last_survey_settings
        )

        self.latest_survey_results_html = ""

        self.survey_results_button.setVisible(
            False
        )

        if self.survey_popup is not None:
            self.survey_popup.close()
            self.survey_popup = None

        self.recommended_line.hide()

        survey.best_frequency = None
        survey.best_occupancy = 0

        if settings_changed:
            survey.heatmap_history.clear()
            self.heatmap_img.clear()

            show_empty_survey_history(
                self.top_frequencies_label
            )

        self.last_survey_settings = (
            current_survey_settings
        )

        survey.survey_frequencies = (
            new_frequencies
        )

        show_survey_progress(
            self.survey_label,
            survey.survey_frequencies[0],
            0,
            len(survey.survey_frequencies),
            0
        )

        self.survey_timer.start(
            3000
        )

    def survey_step(self):

        if self.shutting_down:
            return

        if survey.current_survey_index >= len(
                survey.survey_frequencies
        ):
            self._handle_survey_completion()
            return

        frequency = survey.survey_frequencies[
            survey.current_survey_index
        ]

        progress_percent = int(
            (survey.current_survey_index + 1)
            / len(survey.survey_frequencies)
            * 100
        )

        print(
            "Survey point:",
            survey.current_survey_index + 1,
            "/",
            len(survey.survey_frequencies)
        )

        show_survey_progress(
            self.survey_label,
            frequency,
            survey.current_survey_index + 1,
            len(survey.survey_frequencies),
            progress_percent
        )

        self.freq_input.setText(
            str(frequency)
        )

        self.tune_frequency_callback()

        QTest.qWait(
            500
        )

        if self.shutting_down:
            return

        measurement = (
            self.get_occupancy_callback()
        )

        required_measurements = {
            "occupancy",
            "max_power",
            "average_power"
        }

        normalized_measurement = None

        if (
                isinstance(measurement, dict)
                and required_measurements.issubset(measurement)
        ):
            try:
                normalized_measurement = {
                    name: float(measurement[name])
                    for name in required_measurements
                }
            except (TypeError, ValueError):
                normalized_measurement = None

        if (
                normalized_measurement is None
                or not all(
                    np.isfinite(value)
                    for value in normalized_measurement.values()
                )
        ):
            self.survey_timer.stop()

            show_survey_notice(
                self.survey_label,
                "Measurement error",
                "Survey stopped because RF measurements "
                "are not available.",
                tone="error"
            )
            return

        normalized_measurement["occupancy"] = float(
            np.clip(
                normalized_measurement["occupancy"],
                0,
                100
            )
        )

        normalized_measurement[
            "feature_snapshot"
        ] = build_feature_snapshot(
            frequency,
            self.feature_store,
            max_age_seconds=2.0
        )

        current_occupancy = normalized_measurement[
            "occupancy"
        ]

        survey.survey_results[frequency] = round(
            float(current_occupancy),
            1
        )

        survey.survey_metrics[frequency] = (
            normalized_measurement
        )


        survey.current_survey_index += 1

    def _handle_survey_completion(self):
        self.survey_timer.stop()
        self._cancel_status_transition()

        if len(survey.survey_results) == 0:
            show_survey_notice(
                self.survey_label,
                "Survey incomplete",
                "No valid RF measurements were collected.",
                tone="warning"
            )
            return

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

        recommendation = make_decision(

            self.decision_mode,
            survey.survey_results,
            survey.survey_metrics,
            survey.heatmap_history,
            self.feature_store

        )

        recommended_frequency = recommendation[
            "frequency"
        ]

        recommended_occupancy = recommendation[
            "occupancy"
        ]

        if recommended_frequency is None:
            show_survey_notice(
                self.survey_label,
                "No recommendation",
                "No valid frequency could be selected.",
                tone="warning"
            )
            return

        survey.best_frequency = recommended_frequency

        self._update_heatmap_and_history()

        average_occupancy = round(
            sum(survey.survey_results.values())
            / len(survey.survey_results),
            1
        )

        points_scanned = len(
            survey.survey_results
        )

        results_html = build_results_html(
            sorted_results,
            points_scanned,
            average_occupancy,
            recommendation,
            diagnostic_snapshot=(
                survey.survey_metrics.get(
                    recommended_frequency,
                    {}
                ).get("feature_snapshot")
            ),
            diagnostic_snapshots={
                frequency: metrics.get(
                    "feature_snapshot"
                )
                for frequency, metrics
                in survey.survey_metrics.items()
            }
        )

        self.latest_survey_results_html = (
            results_html
        )

        self.survey_results_button.setVisible(
            True
        )

        self._show_persistent_status()

        self.auto_tune_best()

        return

    def _update_heatmap_and_history(self):
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

        top_frequencies = [
            survey.survey_frequencies[index]
            for index in top_indices
        ]

        top_occupancies = [
            average_by_frequency[index]
            for index in top_indices
        ]

        update_survey_history(
            self.top_frequencies_label,
            top_frequencies,
            top_occupancies,
            len(survey.heatmap_history)
        )

        self.heatmap_img.setImage(
            heatmap_data,
            autoLevels=False
        )

        self.heatmap_img.setLevels(
            (
                0, 100
            )
        )

        frequency_step = (
            survey.survey_frequencies[1]
            - survey.survey_frequencies[0]
        )

        left_edge = (
            survey.survey_frequencies[0]
            - frequency_step / 2
        )

        heatmap_width = (
            frequency_step
            * len(survey.survey_frequencies)
        )

        self.heatmap_img.setRect(
            QRectF(
                left_edge,
                0,
                heatmap_width,
                len(survey.heatmap_history)
            )
        )

        self.heatmap_plot.setLabel(
            "bottom",
            "Frequency",
            units="MHz"
        )

    def clear_current_survey(self):
        self.survey_timer.stop()
        self._cancel_status_transition()
        self.pending_auto_tune_frequency = None

        survey.survey_frequencies = []
        survey.survey_results.clear()
        survey.survey_metrics.clear()
        survey.current_survey_index = 0
        survey.heatmap_history.clear()
        survey.occupancy_percent = 0
        survey.best_frequency = None
        survey.best_occupancy = 0

        self.latest_survey_results_html = ""
        self.last_survey_settings = None

        self.survey_results_button.setVisible(
            False
        )

        if self.survey_popup is not None:
            self.survey_popup.close()
            self.survey_popup = None

        self.heatmap_img.clear()

        self.recommended_line.hide()

        show_empty_survey_history(
            self.top_frequencies_label
        )

        clear_survey(
            self.survey_label
        )
