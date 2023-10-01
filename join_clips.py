"""
How to automatically cut video, given the timestamps

"""

import pandas as pd
from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.video.io.VideoFileClip import VideoFileClip

from analyze import to_seconds

df = pd.read_csv('timestamps4.csv', header=2)
# Fill Nans with start of next, or end of previous
df.end = df.end.fillna(df.start.shift(-1))
df.start = df.start.fillna(df.end.shift(1))

df["start_seconds"] = df.apply(to_seconds, column="start", axis=1)
df["end_seconds"] = df.apply(to_seconds, column="end", axis=1)
df["duration (s)"] = df["end_seconds"] - df["start_seconds"]
df2 = df[df["needed"] == "yes"]
group = df.groupby("needed")
run_times = group.sum("duration (s)")
run_times["duration (m)"] = run_times["duration (s)"] / 60
"""
run times
add up run times based on needed
"""
total = len(df)
print('starting')
clips = []
for i, row in df.iterrows():
    pct = round(i / total * 100, 0)
    print(f'{i} / {total} ({pct}%)')
    if row["needed"] == "yes":
        filename = f'clips/{row["start_seconds"]}_{row["end_seconds"]}.mp4'
        clips.append(VideoFileClip("The.Other.Guys.1080p - original.mp4").subclip(row["start_seconds"],
                                                                                  row["end_seconds"]))
        if row["mute"] == "yes":
            clips[-1] = clips[-1].without_audio()
result = concatenate_videoclips(clips)
result.write_videofile('the other guys - adhd cut v3.mp4')
