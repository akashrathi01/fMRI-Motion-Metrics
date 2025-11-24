import os
import pandas as pd

fmriprep_dir = '/projects/b1108/studies/RADAR/data/preprocessed/fmriprep_nofmap'

runs = [
    ('mid', 'run-01'),
    ('mid', 'run-02'),
    ('rest', 'run-01'),
    ('rest', 'run-02'),
    ('rest', 'run-03'),
    ('rest', 'run-04')
]

fd_thresh = 0.5
cutoff_thresholds = [10, 20, 30]  # percent

results = []

for subj in os.listdir(fmriprep_dir):
    if not subj.startswith('sub-'):
        continue

    subj_path = os.path.join(fmriprep_dir, subj)
    for root, _, files in os.walk(subj_path):
        for file in files:
            if not file.endswith('desc-confounds_timeseries.tsv'):
                continue

            for task, run_number in runs:
                if f'task-{task}' in file and run_number in file:
                    confound_file = os.path.join(root, file)
                    try:
                        df = pd.read_csv(confound_file, sep='\t')
                        if 'framewise_displacement' not in df.columns:
                            print(f"Missing FD in {confound_file}")
                            continue

                        fd = pd.to_numeric(df['framewise_displacement'], errors='coerce')
                        n_spikes = (fd > fd_thresh).sum()
                        perc_spikes = (n_spikes / fd.count()) * 100

                        ses = next((part for part in root.split(os.sep) if part.startswith('ses-')), None)

                        result = {
                            'subject': subj,
                            'session': ses,
                            'task': task,
                            'run_number': run_number,
                            'spike_percentage': perc_spikes
                        }

                        for cutoff in cutoff_thresholds:
                            result[f'cutoff_{cutoff}_exceeded'] = int(perc_spikes > cutoff)

                        results.append(result)
                    except Exception as e:
                        print(f"Error processing {confound_file}: {e}")

df_results = pd.DataFrame(results)
df_results.to_csv('spike_cutoff_flags_by_run.csv', index=False)
