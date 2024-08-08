"""
How to automatically cut video, given the timestamps

"""
import pandas as pd


# df = pd.read_csv(PROJ_DIR + 'timestamps.csv', header=2)
# # Fill Nans timestamps with start of next, or end of previous
# df.end = df.end.fillna(df.start.shift(-1))
# df.start = df.start.fillna(df.end.shift(1))


# def to_seconds(row, column):
def to_seconds(timestamp_raw):
    # timestamp_raw = row["start"]
    if pd.isna(timestamp_raw):
        return timestamp_raw
    timestamp_parts_str = timestamp_raw.split(':')
    print(timestamp_parts_str)
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
    return (row["needed"] in ["yes", "1", "2"]) or (row["purpose"] in ["joke", "hilariously pointless"])


def should_create_clip(row):
    # create all clips we may want to use
    return not (row["needed"] == "no")
