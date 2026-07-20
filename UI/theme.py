"""Shared visual design tokens for the SDR analyzer UI.

Keep palette and reusable widget styling here so each panel can migrate to
the approved Survey Analysis Report style without duplicating color values.
"""


# ==================================================
# COLOR PALETTE
# ==================================================

WINDOW_BACKGROUND = "#202124"
REPORT_SURFACE = "#111315"
CARD_SURFACE = "#1d2329"
RECOMMENDATION_SURFACE = "#132631"
TABLE_HEADER_SURFACE = "#252a30"
TABLE_ALTERNATE_SURFACE = "#181b1f"

BORDER = "#3c4043"

TEXT_PRIMARY = "#e8eaed"
TEXT_STRONG = "#ffffff"
TEXT_MUTED = "#9aa0a6"
TEXT_SUBTLE = "#7f8a93"

ACCENT = "#1769aa"
ACCENT_BORDER = "#2b7bbb"
ACCENT_HOVER = "#1f7fc5"
ACCENT_PRESSED = "#135887"
ACCENT_LIGHT = "#7dd3fc"

STATUS_SUCCESS = "#4ade80"
STATUS_WARNING = "#fbbf24"
STATUS_ERROR = "#fb7185"


# ==================================================
# LEFT SURVEY CONTROL PANEL
# ==================================================

SURVEY_CONTROL_PANEL_MARGINS = (
    18,
    18,
    18,
    18
)

SURVEY_CONTROL_PANEL_SPACING = 6

SURVEY_CONTROL_PANEL_STYLESHEET = f"""
QWidget#surveyControlPanel {{
    background-color: {WINDOW_BACKGROUND};
    border: 1px solid {BORDER};
    border-radius: 10px;
}}

QLabel#surveyPanelTitle {{
    color: {TEXT_STRONG};
    font-size: 18px;
    font-weight: 700;
    border: none;
}}

QLabel#surveyPanelSubtitle {{
    color: {TEXT_MUTED};
    font-size: 11px;
    border: none;
}}

QLabel#surveySectionTitle {{
    color: {TEXT_PRIMARY};
    font-size: 12px;
    font-weight: 700;
    border: none;
}}

QLabel#surveyFieldLabel {{
    color: {TEXT_MUTED};
    font-size: 11px;
    font-weight: 600;
    border: none;
}}

QLineEdit#surveyInput {{
    min-height: 30px;
    padding: 0 10px;
    color: {TEXT_PRIMARY};
    background-color: {REPORT_SURFACE};
    border: 1px solid {BORDER};
    border-radius: 6px;
    selection-background-color: {ACCENT};
}}

QLineEdit#surveyInput:hover {{
    border-color: {ACCENT_BORDER};
}}

QLineEdit#surveyInput:focus {{
    border: 1px solid {ACCENT_LIGHT};
}}

QComboBox#surveyMode {{
    min-height: 30px;
    padding: 0 10px;
    color: {TEXT_PRIMARY};
    background-color: {CARD_SURFACE};
    border: 1px solid {BORDER};
    border-radius: 6px;
}}

QComboBox#surveyMode:hover,
QComboBox#surveyMode:focus {{
    border-color: {ACCENT_LIGHT};
}}

QComboBox#surveyMode QAbstractItemView {{
    color: {TEXT_PRIMARY};
    background-color: {CARD_SURFACE};
    border: 1px solid {BORDER};
    selection-color: {TEXT_STRONG};
    selection-background-color: {ACCENT};
    outline: 0;
}}

QPushButton#surveyPrimaryButton {{
    min-height: 34px;
    padding: 0 14px;
    color: {TEXT_STRONG};
    background-color: {ACCENT};
    border: 1px solid {ACCENT_BORDER};
    border-radius: 6px;
    font-weight: 700;
}}

QPushButton#surveyPrimaryButton:hover {{
    background-color: {ACCENT_HOVER};
}}

QPushButton#surveyPrimaryButton:pressed {{
    background-color: {ACCENT_PRESSED};
}}

QPushButton#surveySecondaryButton {{
    min-height: 32px;
    padding: 0 14px;
    color: {TEXT_PRIMARY};
    background-color: {CARD_SURFACE};
    border: 1px solid {BORDER};
    border-radius: 6px;
    font-weight: 600;
}}

QPushButton#surveySecondaryButton:hover {{
    color: {TEXT_STRONG};
    border-color: {ACCENT_BORDER};
    background-color: {TABLE_HEADER_SURFACE};
}}

QPushButton#surveyPrimaryButton:disabled,
QPushButton#surveySecondaryButton:disabled {{
    color: {TEXT_SUBTLE};
    background-color: {REPORT_SURFACE};
    border-color: {BORDER};
}}

QTextEdit#surveyResultsCard {{
    color: {TEXT_PRIMARY};
    background-color: {REPORT_SURFACE};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 10px;
    selection-background-color: {ACCENT};
}}
"""


# ==================================================
# SURVEY REPORT POPUP
# ==================================================

SURVEY_POPUP_SIZE = (
    720,
    760
)

SURVEY_POPUP_MINIMUM_SIZE = (
    560,
    520
)

SURVEY_POPUP_MARGINS = (
    20,
    18,
    20,
    18
)

SURVEY_POPUP_SPACING = 12

SURVEY_POPUP_STYLESHEET = f"""
QWidget {{
    background-color: {WINDOW_BACKGROUND};
    color: {TEXT_PRIMARY};
}}

QLabel#reportTitle {{
    color: {TEXT_STRONG};
    font-size: 22px;
    font-weight: 700;
}}

QLabel#reportSubtitle {{
    color: {TEXT_MUTED};
    font-size: 12px;
}}

QTextEdit {{
    background-color: {REPORT_SURFACE};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 16px;
    selection-background-color: {ACCENT};
}}

QPushButton {{
    min-width: 96px;
    min-height: 32px;
    padding: 4px 16px;
    color: {TEXT_STRONG};
    background-color: {ACCENT};
    border: 1px solid {ACCENT_BORDER};
    border-radius: 6px;
    font-weight: 600;
}}

QPushButton:hover {{
    background-color: {ACCENT_HOVER};
}}

QPushButton:pressed {{
    background-color: {ACCENT_PRESSED};
}}
"""


# ==================================================
# SURVEY REPORT HTML
# ==================================================

REPORT_HTML_COLORS = {
    "WINDOW_BACKGROUND": WINDOW_BACKGROUND,
    "REPORT_SURFACE": REPORT_SURFACE,
    "CARD_SURFACE": CARD_SURFACE,
    "RECOMMENDATION_SURFACE": RECOMMENDATION_SURFACE,
    "TABLE_HEADER_SURFACE": TABLE_HEADER_SURFACE,
    "TABLE_ALTERNATE_SURFACE": TABLE_ALTERNATE_SURFACE,
    "TEXT_PRIMARY": TEXT_PRIMARY,
    "TEXT_STRONG": TEXT_STRONG,
    "TEXT_MUTED": TEXT_MUTED,
    "TEXT_SUBTLE": TEXT_SUBTLE,
    "ACCENT_LIGHT": ACCENT_LIGHT,
}

CONFIDENCE_COLORS = {
    "HIGH": STATUS_SUCCESS,
    "MODERATE": STATUS_WARNING,
    "LOW": STATUS_ERROR,
    "N/A": TEXT_MUTED,
}


def confidence_color(
        confidence
):
    return CONFIDENCE_COLORS.get(
        confidence,
        TEXT_MUTED
    )


def apply_report_html_theme(
        report_html
):
    themed_html = report_html

    for name, value in REPORT_HTML_COLORS.items():
        themed_html = themed_html.replace(
            "{{" + name + "}}",
            value
        )

    return themed_html
