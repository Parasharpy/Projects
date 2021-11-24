#biovec(an extension of word2vec algorithm) is used to create protein vectors.

import pickle
from Bio import SeqIO
import biovec
from google.colab import files
uploaded = files.upload()
pv = biovec.models.ProtVec("trimmeda_seq.txt", corpus_fname = "output.txt", n = 3)
pv.save('biovec_seq')
sequences = []
with open("trimmeda_seq.txt") as handle:
  for record in SeqIO.parse(handle, "fasta"):
    sequences.append(str(record.seq))
pv2 =  biovec.models.load_protvec('biovec_seq')
all_embeddings = []
for i in sequences:
  embed = pv2.to_vecs(i)
  all_embeddings.append(embed)
filename = 'X.pickle' #first input
output = open(filename, 'wb')
pickle.dump(all_embeddings, outfile)
outfile.close()
