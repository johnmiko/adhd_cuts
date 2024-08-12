"""
How to automatically cut video, given the timestamps

"""
import logging

import pandas as pd

from inputs import CREATE_ALL_CLIPS

logger = logging.getLogger(__name__)


# df = pd.read_csv(PROJ_DIR + 'timestamps.csv', header=2)
# # Fill Nans timestamps with start of next, or end of previous
# df.end = df.end.fillna(df.start.shift(-1))
# df.start = df.start.fillna(df.end.shift(1))


# def to_seconds(row, column):
def to_seconds(timestamp_raw):
    # TODO: check if this is needed or not, may be able to remove
    # timestamp_raw = row["start"]
    if pd.isna(timestamp_raw):
        return timestamp_raw
    timestamp_parts_str = timestamp_raw.split(':')
    logger.debug(timestamp_parts_str)
    timestamp_parts = [float(part) for part in timestamp_parts_str]
    # hour, minute, seconds,
    # if hours are included
    if len(timestamp_parts) == 3:
        # # excel added stupid 00 to the timestamp
        # if (timestamp_parts_str[-1] == "00") and (timestamp_parts_str[0] != "1"):
        #     seconds = timestamp_parts[0] * 60 + timestamp_parts[1]
        # else:
        seconds = timestamp_parts[0] * 3600 + timestamp_parts[1] * 60 + timestamp_parts[2]
    # if only minutes and seconds are included
    elif len(timestamp_parts) == 2:
        seconds = timestamp_parts[0] * 60 + timestamp_parts[1]
    # If it's the very first timestamp
    elif timestamp_parts == [0]:
        return 0
    else:
        raise ValueError(f'unsure what to do with {timestamp_parts}')
    return seconds


def should_include_clip(row):
    # minimal
    # (row["needed"] == "yes") or (row["needed"] == "1")
    # include funny and level 2
    # return (row["needed"] in ["yes", "1", "2", "3", "4"]) or (row["purpose"] in ["joke", "hilariously pointless"])
    return row["needed"] in ["yes", "1", "2", "3"]


def should_create_clip(row):
    # For intermediate movie we want to create all the clips so we can add scene numbers to the clips
    if CREATE_ALL_CLIPS:
        return True
    # For final cut, we only need the clips that are in the final cut
    clip_may_be_used = not ((row["needed"] == "no") or pd.isna(row["needed"]) or (row["needed"].strip() == ""))
    return clip_may_be_used
