import os
import pandas as pd

# === User-defined parameters ===
fmriprep_dir = 'YOUR/fMRIPREP/DATA'
TR = 0.555  # seconds per TR

# Resting-state runs to include
rest_runs = [
    'run-01',
    'run-02',
    'run-03',
    'run-04'
]

# FD thresholds to evaluate
fd_thresholds = [0.1, 0.2, 0.3, 0.4, 0.5, 0.7, 0.9, 1.0]

# === Initialize storage ===
results = []

# === Main loop ===
for subj in os.listdir(fmriprep_dir):
    if not subj.startswith('sub-'):
        continue

    subj_path = os.path.join(fmriprep_dir, subj)
    subj_data = {}  # temporary dict per subject/session

    for root, _, files in os.walk(subj_path):
        for file in files:
            if not file.endswith('desc-confounds_timeseries.tsv'):
                continue
            if 'task-rest' not in file:
                continue
            if not any(run in file for run in rest_runs):
                continue

            confound_file = os.path.join(root, file)
            try:
                df = pd.read_csv(confound_file, sep='\t')
                if 'framewise_displacement' not in df.columns:
                    print(f"⚠️ Missing FD in {confound_file}")
                    continue

                fd = pd.to_numeric(df['framewise_displacement'], errors='coerce')
                n_total = fd.count()

                ses = next((part for part in root.split(os.sep) if part.startswith('ses-')), None)
                key = (subj, ses)

                if key not in subj_data:
                    subj_data[key] = {fd_thresh: 0 for fd_thresh in fd_thresholds}

                # Sum remaining scan time across runs for each FD threshold
                for fd_thresh in fd_thresholds:
                    n_spikes = (fd > fd_thresh).sum()
                    n_remaining = n_total - n_spikes
                    scan_time_min = n_remaining * TR / 60
                    subj_data[key][fd_thresh] += scan_time_min

            except Exception as e:
                print(f"Error processing {confound_file}: {e}")

    # Add aggregated data to results
    for (subj, ses), time_dict in subj_data.items():
        row = {'subject': subj, 'session': ses}
        # Add remaining scan time columns per FD threshold
        for fd_thresh, scan_time in time_dict.items():
            col_name = f'remaining_scan_time_fd_{fd_thresh:.1f}min'
            row[col_name] = round(scan_time, 2)
        results.append(row)

# === Save results ===
df_results = pd.DataFrame(results)
output_file = 'rest_remaining_scan_time_multi_fd_wide.csv'
df_results.to_csv(output_file, index=False)
print(f"Saved wide-format resting-state scan time for multiple FD thresholds to {output_file}")
