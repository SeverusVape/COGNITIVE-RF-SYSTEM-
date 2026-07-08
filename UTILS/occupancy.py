import numpy as np


def calculate_occupancy(
    power_db,
    threshold
):

    occupied_bins = np.sum(
        power_db > threshold
    )

    occupancy = (
        occupied_bins / len(power_db)
    ) * 100

    bars = int(
        occupancy / 10
    )

    COLOR_BLUE = "#2ab7ca"
    COLOR_GREEN = "#24b755"
    COLOR_YELLOW = "#f4b400"
    COLOR_RED = "#fe4a49"
    COLOR_EMPTY = "#333333"

    colored_bars = ""

    for i in range(1, 11):

        if i <= bars:

            if i <= 4:
                color = COLOR_BLUE

            elif i <= 7:
                color = COLOR_GREEN

            elif i <= 9:
                color = COLOR_YELLOW

            else:
                color = COLOR_RED

            colored_bars += (
                f'<span style="color:{color};">'
                '■'
                '</span>'
            )

        else:

            colored_bars += (
                f'<span style="color:{COLOR_EMPTY};">'
                '░'
                '</span>'
            )

    meter = (
        f'<span style="font-family: Courier New; color: #ffffff;">'
        f'[{colored_bars}]'
        f'</span>'
    )

    return occupancy, meter