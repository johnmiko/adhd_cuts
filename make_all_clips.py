"""
How to automatically cut video, given the timestamps

"""
import os

import pandas as pd
from moviepy.video.io.VideoFileClip import VideoFileClip

from analyze import to_seconds

df = pd.read_csv('timestamps.csv', header=2)
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
for i, row in df.iterrows():
    pct = round(i / total * 100, 0)
    print(f'{i} / {total} ({pct}%)')
    if row["needed"] != "no":
        filename = f'clips/{row["start_seconds"]}_{row["end_seconds"]}.mp4'
        # Do not recreate clip if it's already been done
        if not os.path.exists(filename):
            clip = VideoFileClip("The.Other.Guys.1080p - original.mp4").subclip(row["start_seconds"],
                                                                                row["end_seconds"])
            # resultlt = concatenate_videoclips([video, video2])
            # result = CompositeVideoClip([video, video2])  # Overlay text on video
            clip.write_videofile(filename)
