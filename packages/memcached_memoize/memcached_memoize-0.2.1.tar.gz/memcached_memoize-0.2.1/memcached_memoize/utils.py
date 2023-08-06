# coding: utf8


def time_string_to_seconds(time_string):
    unit_to_seconds = {
        's': 1,
        'm': 60,
        'h': 60 * 60,
        'd': 60 * 60 * 24
    }
    return int(time_string[:-1]) * unit_to_seconds[time_string[-1]]

MAX_TIMEOUT = time_string_to_seconds('30d')
