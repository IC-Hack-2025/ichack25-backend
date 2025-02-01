import re
from datetime import timedelta


def timedelta_to_h_m_s_micro_str(td: timedelta) -> str:
    total_seconds = td.total_seconds()
    h = int(total_seconds // 3600)
    m = int((total_seconds % 3600) // 60)
    s = int(total_seconds % 60)
    mu_s = td.microseconds
    return f"{h:02d}:{m:02d}:{s:02d}.{mu_s:06d}"


def h_m_s_micro_str_to_timedelta(s: str) -> timedelta:
    regex = r"(\d+):(\d+):(\d+).(\d+)"
    values = re.findall(regex, s)[0]
    td = timedelta(hours=int(values[0]), minutes=int(values[1]), seconds=int(values[2]), microseconds=int(values[3]))
    return td
