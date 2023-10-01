"""
How to automatically cut video, given the timestamps

"""
import pandas as pd

df = pd.read_csv('timestamps4.csv', header=2)
# Fill Nans with start of next, or end of previous
df.end = df.end.fillna(df.start.shift(-1))
df.start = df.start.fillna(df.end.shift(1))


def to_seconds(row, column):
    timestamp_raw = row[column]
    timestamp_parts_str = timestamp_raw.split(':')
    print(timestamp_parts_str)
    timestamp_parts = [float(part) for part in timestamp_parts_str]
    # hour, minute, seconds,
    if len(timestamp_parts) == 3:
        # # excel added stupid 00 to the timestamp
        # if (timestamp_parts_str[-1] == "00") and (timestamp_parts_str[0] != "1"):
        #     seconds = timestamp_parts[0] * 60 + timestamp_parts[1]
        # else:
        seconds = timestamp_parts[0] * 3600 + timestamp_parts[1] * 60 + timestamp_parts[2]
    elif len(timestamp_parts) == 2:
        seconds = timestamp_parts[0] * 60 + timestamp_parts[1]
    else:
        raise ValueError(f'unsure what to do with {timestamp_parts}')
    return seconds


df["start_seconds"] = df.apply(to_seconds, column="start", axis=1)
df["end_seconds"] = df.apply(to_seconds, column="end", axis=1)
df["duration (s)"] = df["end_seconds"] - df["start_seconds"]
df2 = df[df["needed"] == "yes"]
group = df.groupby("needed")
run_times = group.sum("duration (s)")
run_times["duration (m)"] = (run_times["duration (s)"] / 60).round(0)
print(run_times)
# clips = []
# filename = f'temp.mp4'
# clips.append(VideoFileClip("The.Other.Guys.1080p - original.mp4").subclip(194.5, 218))
# result = concatenate_videoclips(clips)
# result.write_videofile('the other guys - adhd cut v2.mp4')
# VideoFileClip("The.Other.Guys.1080p - original.mp4").subclip(194.5, 218).write_videofile('temp.mp4')
