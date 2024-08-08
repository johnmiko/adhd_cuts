# ADHD Cuts

- Script for cutting movies down to a modern ADHD version
- Input `timestamps.csv` with columns `start`,`end`, `needed`
- DO NOT SAVE TIMESTAMPS WITH MILLISECONDS IN EXCEL AS CSV FILE, EXCEL WILL NOT SAVE MILLISECONDS PROPERLY
- start & end: timestamps of clip in format hour:minute:second or minute:second (ex: 0:47, 1:36:00)
- needed: "yes", "no" or a number indicating if scene can be included (ex: 2 means scene is fun but not iconic and not
  necessary to understand the plot)