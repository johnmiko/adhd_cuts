"""
How to automatically cut video, given the timestamps

"""
import os

import pandas as pd
from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.video.io.VideoFileClip import VideoFileClip

from analyze import to_seconds, should_include_clip
from inputs import PROJ_DIR, ORIGINAL_FILE

# -i "Digimon Adventure 02 Ep01-1.m4v" -vf select="eq(pict_type\, PICT_TYPE_I)" -vsync 2 -frame_pts 1 -r 1000 "output.mp4-%d.jpg"
# Can run directly with ffmpeg command line to get key frame timestamps
# ffprobe -select_streams v -show_frames -show_entries frame=pkt_pts_time,pict_type -of csv=print_section=0 "Digimon Adventure 02 Ep01-1.m4v" | findstr ",I" > keyframes.txt
# ffprobe -loglevel error -select_streams v:0 -show_entries packet=pts_time,flags -of csv=print_section=0  | awk -F',' '/K/ {print $1}'
# ffprobe -loglevel error -select_streams v:0 -show_entries packet=pts_time,flags -of csv=print_section=0 "Digimon
# Adventure 02 Ep01-1.m4v"

df_in = pd.read_csv(PROJ_DIR + 'Digimon 02 - 01 timestamps - timestamps (1).csv', header=2)
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
clips = []
if "create_clips" == "nope":
    print('creating clips')
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
            clip = VideoFileClip(ORIGINAL_FILE).subclip(row["start_seconds"],
                                                        row["end_seconds"])
            clips.append(clip)
    result = concatenate_videoclips(clips)
    filename = f'{ORIGINAL_FILE} - ADHD Cut - funny.mp4'
    result.write_videofile(filename)
    print('finished combining clips')
