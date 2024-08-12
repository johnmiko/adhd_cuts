"""
How to automatically cut video, given the timestamps

"""
import os
import shutil
import time
from datetime import datetime

import pandas as pd
from moviepy.config import change_settings
from moviepy.video.VideoClip import TextClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.video.io.VideoFileClip import VideoFileClip

from analyze import should_include_clip, to_seconds, should_create_clip
from inputs import PROJ_DIR, ORIGINAL_FILE, CSV_FILENAME

change_settings({"IMAGEMAGICK_BINARY": r"D:/Program Files/ImageMagick-7.1.1-Q16-HDRI/magick.exe"})
should_create_clips = False
should_overwrite_existing_clips = False
should_create_intermediate_movie = False
should_create_adhd_cut = True


def get_df(csv_filename=CSV_FILENAME):
    # Copy the file and rename it
    old_csvfile = csv_filename + "_old.csv"
    if not os.path.exists("timestamps_old.csv"):
        # For first time when file does not exist
        shutil.copyfile(csv_filename, old_csvfile)
    df_in = pd.read_csv(csv_filename, header=2)
    df_old = pd.read_csv(old_csvfile, header=2)
    changes_in_csv_file = not df_in.equals(df_old)
    # todo: compare changes or whatever. Then don't need to redo everything
    # remove rows where start and end time are not filled in. In case of user error
    # df = df_in[~df_in[["start", "end"]].isna().all(axis=1)]
    # df.end = df.end.fillna(df.start.shift(-1))
    # df.start = df.start.fillna(df.end.shift(1))
    # convert to seconds so we can see what the total runtimes are
    df = df_in
    df['start_seconds'] = df['start'].apply(to_seconds)
    df['end_seconds'] = df['end'].apply(to_seconds)
    # df['start_seconds'] = df['start']
    # df['end_seconds'] = df['end']
    df["duration"] = df["end_seconds"] - df["start_seconds"]
    # df2 = df[df["needed"] == "yes"]
    group = df.groupby("needed")
    run_times = group.sum("duration")
    run_times["duration (m)"] = run_times["duration"] / 60
    run_times_m = run_times["duration (m)"]
    run_time_1 = run_times_m["1"]
    run_time_2 = run_times_m["1"] + run_times_m["2"]
    run_time_3 = run_times_m["1"] + run_times_m["2"]
    run_time_4 = run_times_m["1"] + run_times_m["2"] + run_times_m["3"] + run_times_m["4"]
    print(f"original run time")
    print(f"{round(df.iloc[-1]["end_seconds"] / 60, 0)}")
    print(f"new run times ")
    print(f"1: {round(run_time_1, 0)}")
    print(f"2: {round(run_time_2, 0)}")
    print(f"2: {round(run_time_3, 0)}")
    print(f"2: {round(run_time_4, 0)}")
    return df


df = get_df(CSV_FILENAME)
total = len(df)
original_filename_no_ext = os.path.splitext(os.path.basename(ORIGINAL_FILE))[0]


def modify_clip(row, clip):
    # danishandoneill@gmail.com
    # TODO: not tested
    if row["other"] == "mute":
        clip = clip.without_audio()
    if row["other"] == "force_subtitles":
        dialogue = row["dialogue"]
        text = TextClip(dialogue, fontsize=70, color='white', font='Arial', stroke_color='black', stroke_width=2)
        text = text.set_duration(clip.duration).set_position(("center", "bottom"))
        clip = CompositeVideoClip([clip, text])
    return clip


def create_clips():
    # https://zulko.github.io/moviepy/ref/VideoClip/VideoClip.html?highlight=subclip#moviepy.video.io.VideoFileClip.VideoFileClip.subclip
    # maybe don't need to modify the times if I put them in correctly
    # the times it accepts are flexible example 00:15:13.254
    if should_create_clips:
        print('creating clips')
        # Ensure the clips directory exists
        os.makedirs(f"{PROJ_DIR}clips", exist_ok=True)
        for i, row in df.iterrows():
            pct = round((i + 1) / total * 100, 0)
            print(f'{i + 1} / {total} ({pct}%)')
            filename = f'{PROJ_DIR}clips/{row["start_seconds"]}_{row["end_seconds"]}.mp4'
            if should_create_clip(row):
                clip = VideoFileClip(ORIGINAL_FILE).subclip(row["start_seconds"],
                                                            row["end_seconds"])
                if should_overwrite_existing_clips:
                    clip.write_videofile(filename)
                elif not os.path.exists(filename):
                    clip.write_videofile(filename)
        print('finished creating clips')


def create_intermediate_movie():
    clips = []
    if should_create_intermediate_movie:
        print('starting creating intermediate movie')
        for i, row in df.iterrows():
            pct = round((i + 1) / total * 100, 0)
            print(f'{i + 1} / {total} ({pct}%)')
            filename = f'{PROJ_DIR}clips/{row["start_seconds"]}_{row["end_seconds"]}.mp4'
            if os.path.exists(filename):
                clip = VideoFileClip(filename)
            else:
                clip = VideoFileClip(ORIGINAL_FILE).subclip(row["start_seconds"],
                                                            row["end_seconds"])
            text = TextClip(f"{i}", fontsize=70, color='white', font='Arial', stroke_color='black',
                            stroke_width=2)
            text = text.set_duration(clip.duration).set_position(("right", "bottom"))
            composite_clip = CompositeVideoClip([clip, text])
            clips.append(composite_clip)

        if clips:
            result = concatenate_videoclips(clips)
            current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f'{PROJ_DIR}{original_filename_no_ext} {current_time} intermediate.mp4'
            result.write_videofile(output_filename)
            print('finished combining clips')
        else:
            print("No clips to combine!")


def create_adhd_cut():
    clips = []
    og_run_time_secs = df.iloc[-1]["end_seconds"]
    save_every_x_minutes = 20 * 60
    x_minute_clips = []
    clip_counter = 1
    accumulated_time = 0
    if create_adhd_cut:
        print('starting combining clips')
        original_video = VideoFileClip(ORIGINAL_FILE)
        save_first_half = False
        try:
            for i, row in df.iterrows():
                pct = round((i + 1) / total * 100, 0)
                print(f'{i + 1} / {total} ({pct}%)')
                accumulated_time += end - start

                # Check if the accumulated time exceeds the save threshold
                if row["end_seconds"] > (save_every_x_minutes * clip_counter):
                    print(f"saving minutes {clip_counter * save_every_x_minutes} to "
                          f"{(clip_counter + 1) * save_every_x_minutes}")
                    clip_counter += 1
                    result = concatenate_videoclips(x_minute_clips)
                    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
                    output_filename = (f'{PROJ_DIR}{original_filename_no_ext}_Part{clip_counter}_'
                                       f'{current_time}_ADHD_Cut.mp4')
                    result.write_videofile(output_filename)
                    x_minute_clips = []
                if should_include_clip(row):
                    filename = f'{PROJ_DIR}clips/{row["start_seconds"]}_{row["end_seconds"]}.mp4'
                    start = row["modified_start"] if not pd.isna(row["modified_start"]) else row["start_seconds"]
                    end = row["modified_end"] if not pd.isna(row["modified_end"]) else row["end_seconds"]

                    def create_clip(start, end, retry=True):
                        try:
                            return original_video.subclip(start, end)
                        except IOError as e:
                            print(e)
                            if retry:
                                print(f"Failed to clip part {i}, trying again")
                                time.sleep(3)
                                return create_clip(start, end, retry=False)
                            else:
                                raise

                    if row["modified_start"] or row["modified_end"]:
                        clip = create_clip(start, end)
                    elif os.path.exists(filename):
                        try:
                            clip = VideoFileClip(filename)
                        except OSError as e:
                            print(e)
                            clip = create_clip(row["start_seconds"], row["end_seconds"])
                            clip.write_videofile(filename)
                    else:
                        clip = create_clip(row["start_seconds"], row["end_seconds"])

                    clips.append(clip)
        except Exception as e:
            print(f"error on row {i}")
            print(e)
        finally:
            if clips:
                result = concatenate_videoclips(clips)
                current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_filename = f'{PROJ_DIR}{original_filename_no_ext} {current_time} ADHD Cut.mp4'
                result.write_videofile(output_filename)
                print('finished combining clips')
            else:
                print("No clips to combine!")
    return output_filename


def add_manual_scenes(video_file=None):
    pass
    # # clips = [video_file]
    # clips = []
    # folder = "D:/ccode/adhd_cuts/movies/Star Wars Episode IV A New Hope (1977) [1080p]/"
    # extra_scenes = ["Star.Wars.Episode.4.A.New.Hope.1977.1080p.BrRip.x264.BOKUTOX.YIFY 20240811_123615 first half "
    #                 "ADHD Cut.mp4",
    #                 "Star.Wars.Episode.4.A.New.Hope.1977.1080p.BrRip.x264.BOKUTOX.YIFY 20240811_143333 ADHD Cut.mp4"]  # ,
    # # "bar scene - droids not welcome.mkv"]
    # for scene in extra_scenes:
    #     clip = VideoFileClip(f"{folder}{scene}")
    #     clips.append(clip)
    # result = concatenate_videoclips(clips)
    # current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    # output_filename = f'{PROJ_DIR}{original_filename_no_ext} {current_time} ADHD Cut final.mp4'
    # result.write_videofile(output_filename)


def create_new_subtitle_file():
    pass


if __name__ == "__main__":
    create_clips()
    create_intermediate_movie()
    # adhd_file = create_adhd_cut()
    add_manual_scenes()
    create_new_subtitle_file()
    df = get_df()
