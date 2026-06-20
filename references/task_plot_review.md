# Task Plot Review

## Evidence Match

- Pass: title and construct match the Cambridge Gambling Task.
- Pass: rows summarize sampled explicit box ratios as high, medium, and low probability evidence levels.
- Pass: phase order matches README and `src/run_trial.py`: Fixation -> Color choice -> Bet choice -> Feedback -> ITI.
- Pass: timing labels match config: 300-600 ms fixation, 3000 ms color choice, 3500 ms bet choice, 1000 ms feedback, 300-600 ms ITI.
- Pass: color-choice mapping shows F=red and J=blue.
- Pass: bet-choice mapping shows keys 1-5 and options 5%, 25%, 50%, 75%, and 95%.
- Pass: feedback shows token color, applied stake, point delta, and updated score.

## Visual Quality

- Pass: labels and timings are readable.
- Pass: generated timeline content stays below the header band.
- Pass: fixed title and Construct subtitle are centered.
- Pass: top-right TaskBeacon logo lockup is borderless and non-overlapping.
- Pass: no generated title, logo, watermark, people, devices, or decorative scene is present.

## README Embed

- Pass: `README.md` contains `## 2. Task Flow`.
- Pass: the section embeds `![Task Flow](task_flow.png)`.
- Pass: final image is saved as `task_flow.png`; raw timeline is saved as `references/task_plot_timeline_raw.png`.
