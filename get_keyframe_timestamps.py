# D:\Users\johnm\OneDrive\ccode_files\adhd_cuts\digimon> ffprobe -loglevel error -select_streams v:0 -show_entries packet=pts_time,flags -of csv=print_section=0 "Digimon Adventure 02 Ep01-1.m4v" > keyframes.txt
# Run the above in the terminal
import pandas as pd

from inputs import PROJ_DIR

filename = PROJ_DIR + "keyframes.txt"
keyframes = []
with open(filename, "r") as f:
    timestamps = f.readlines()

df = pd.read_csv(filename, encoding="utf-16", header=None)
df_keyframes = df[df[1] == "K__"]
df_keyframes.columns = ["start", "end"]
df_keyframes["end"] = df_keyframes["start"].shift(-1)
df_keyframes = df_keyframes.reset_index()
df.rename(columns={'index': 'frame_num'}, inplace=True)
df_keyframes.to_csv(f"{PROJ_DIR}keyframe_timestamps.csv", header=True, index=True)
