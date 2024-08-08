"""
How to automatically cut video, given the timestamps

"""
import os

import pandas as pd
from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.video.io.VideoFileClip import VideoFileClip

from analyze import to_seconds, should_include_clip
from inputs import PROJ_DIR, ORIGINAL_FILE

df_in = pd.read_csv(PROJ_DIR + 'timestamps.csv', header=2)
# remove rows where start and end time are not filled in. In case of user error
df = df_in[~df_in[["start", "end"]].isna().all(axis=1)]
# Fill Nans timestamps with start of next, or end of previous
df.end = df.end.fillna(df.start.shift(-1))
df.start = df.start.fillna(df.end.shift(1))
df['start_seconds'] = df['start'].apply(to_seconds)
df['end_seconds'] = df['end'].apply(to_seconds)
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
print('creating clips')
clips = []
if "create_clips" == "nope":
    # TODO: make clips directory if it doesn't exist
    # Think I don't need this whole thing yeah?
    for i, row in df.iterrows():
        pct = round(i / total * 100, 0)
        print(f'{i} / {total} ({pct}%)')
        if should_include_clip(row):
            filename = f'{PROJ_DIR}clips/{row["start_seconds"]}_{row["end_seconds"]}.mp4'
            # Do not recreate clip if it's already been done
            if not os.path.exists(filename):
                clip = VideoFileClip(ORIGINAL_FILE).subclip(row["start_seconds"],
                                                            row["end_seconds"])
                # clips.append(clip)
                # resultlt = concatenate_videoclips([video, video2])
                # result = CompositeVideoClip([video, video2])  # Overlay text on video
                # TODO: not tested
                # if row["other"] == "mute":
                #     clips[-1] = clips[-1].without_audio()
                clip.write_videofile(filename)
                # TODO: create clip with extra text in it for debugging, hard to tell which frame is which one for
                #  the first watch to check if it is joined properly
    print('finished creating clips')

if "combine_clips":
    print('starting combining clips')
    print("need to decide if I should make the clips, then just join those, or just only do here")
    print("combining 20 minute digimon episode takes about 2 minutes")
    for i, row in df.iterrows():
        pct = round(i / total * 100, 0)
        print(f'{i} / {total} ({pct}%)')
        if should_include_clip(row):
            filename = f'{PROJ_DIR}clips/{row["start_seconds"]}_{row["end_seconds"]} - ADHD Cut - funny.mp4'
            clip = VideoFileClip(ORIGINAL_FILE).subclip(row["start_seconds"],
                                                        row["end_seconds"])
            clips.append(clip)
    result = concatenate_videoclips(clips)
    result.write_videofile(f'{ORIGINAL_FILE}.mp4')
    print('finished combining clips')
