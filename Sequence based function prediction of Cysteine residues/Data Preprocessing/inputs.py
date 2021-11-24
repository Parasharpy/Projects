#code for second input which contains modifications for sequences


import pandas as pd 
import pickle
from google.colab import files
uploaded = files.upload()
import io
window = x # x can be 3,5,7,9,11,13
ds = pd.read_csv(io.BytesIO(uploaded['data_file_name.csv']))
UniProt_ID = list(ds.iloc[:,0].values)
res = list(ds.iloc[:,1].values)
sequences = list(ds.iloc[:,2].values)
modifications = list(ds.iloc[:,3].values)
i = 0
textfile = []
for seq in sequences:
    start = int(res[i]) - window 
    end = int(res[i]) + window
    if (len(seq[start:end]) == 2*x):
        if modifications[i] == 'Disulfide'
            textfile.append(0)
        elif modifications[i] == 'S-Glutathionylation'
            textfile.append(1)
        elif modifications[i] == 'Metal-Binding':
            textfile.append(2)
        elif modifications[i] == 'Nitrosylation' or modifications[i] == 'S-Nitrosylation':
            textfile.append(3)
        elif modifications[i] == 'Palmitoylation':
            textfile.append(4)
        elif modifications[i] == 'Sulfenylation':
            textfile.append(5)
        elif modifications[i] == 'thioether':
            textfile.append(6)
        else:
            textfile.append(7)
    i += 1
    
filename = 'Y.pickle'
outfile = open(filename, 'wb')
pickle.dump(textfile, outfile)
outfile.close()
