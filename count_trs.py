import glob
import os
import nibabel as nib
import csv


PATH = 'YOUR/PROCESSED/RESTING/NETWORKS'


files = glob.glob(PATH)

tr_counts = [["ID", "ses", "cleaned_shape"]]


for file in files:     
    short_name = os.path.basename(file)
    print(short_name)
    ID = short_name[0:8]
    ses = short_name[25:31]
    img = nib.load(file)
    tr_counts.append([ID, ses, img.shape])
    print(img.shape)
    

with open('RADAR_REST_fd-1_TRs.csv', 'w') as myfile:
    wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
    for row in tr_counts:
        wr.writerow(row)
