import subprocess

import pandas as pd


def record_keyframes_to_file(in_file, out_file="all_frames.csv"):
    # To run manually "D:/Users/johnm/OneDrive/ccode_files/adhd_cuts/digimon> ffprobe -loglevel error -select_streams v:0 -show_entries packet=pts_time,flags -of csv=print_section=0 "Digimon Adventure 02 Ep01-1.m4v" > keyframes.txt"
    print("recording all frame times to file")
    command = [
        "ffprobe",
        "-loglevel", "error",
        "-select_streams", "v:0",
        "-show_entries", "packet=pts_time,flags",
        "-of", "csv=print_section=0",
        in_file
    ]
    # Run the command in the specified directory
    with open(f"{folder}/{out_file}", "w") as outfile:
        subprocess.run(command, cwd=folder, stdout=outfile)


def create_keyframes_df():
    print("creating keyframe timestamps csv file")
    filename = f"{folder}all_frames.csv"
    # df = pd.read_csv(filename, encoding="utf-16", header=None)
    df_raw = pd.read_csv(filename, header=None)
    df_keyframes = df_raw[df_raw[1] == "K__"]
    df_keyframes.columns = ["start_seconds", "end_seconds"]
    df_keyframes["end_seconds"] = df_keyframes["start_seconds"].shift(-1)
    # Drop the very last row because it does not have an end frame
    # Would be a bit better to instead set the very last end frame time to the end of the video
    df_keyframes = df_keyframes.iloc[:-1]
    df_keyframes = df_keyframes.reset_index()
    df_keyframes.rename(columns={'index': 'frame_num'}, inplace=True)
    return df_keyframes


# Function to convert seconds to formatted time string
def format_time(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    sec = int(seconds % 60)
    milliseconds = int((seconds % 1) * 10000)  # Adjusted for four decimal places

    # Format the time as HH:MM:SS.mmm
    formatted_time = f"{hours:02}:{minutes:02}:{sec:02}.{milliseconds:04}"
    return formatted_time


def create_timestamps_csv():
    df['start'] = df['start_seconds'].apply(format_time)
    df['end'] = df['end_seconds'].apply(format_time)
    df.to_csv(f"{folder}keyframe_timestamps.csv", header=True, index=True)


if __name__ == "__main__":
    in_file = "Star.Wars.Episode.4.A.New.Hope.1977.1080p.BrRip.x264.BOKUTOX.YIFY.mp4"
    folder = "D:/ccode/adhd_cuts/movies/Star Wars Episode IV A New Hope (1977) [1080p]/"
    # record_keyframes_to_file(in_file)
    df = create_keyframes_df()
    create_timestamps_csv()
