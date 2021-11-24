#This was done on google colab. Sequence was trimmed for different window sizes with "cysteine" as centre.

import pandas as pd 
window = x #x can be 3,5,7,9,11,13
from google.colab import files
uploaded = files.upload()
import io
ds = pd.read_csv(io.BytesIO(uploaded['data_file_name.csv']))
UniProt_ID = list(ds.iloc[:,0].values)
res = list(ds.iloc[:,1].values)
sequences = list(ds.iloc[:,2].values)
i = 0
with open('trimmed_sequence.txt', 'w', newline = '') as f:
    for seq in sequences:
        start = int(res[i]) - window 
        end = int(res[i]) + window
        if (len(seq[start:end]) == 2*x):
            f.write('>' + str(UniProt_ID[i]) + '_' + str(res[i]) + '\n')
            f.write(seq[start:end] + '\n')
        i = i + 1
