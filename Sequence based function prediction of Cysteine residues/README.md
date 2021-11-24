# Sequence-based function prediction of Cysteine residues
This project mainly focuses on developing deep learning models which can predict the most probable function of a cysteine residue by exploring the FASTA sequences. Cysteine is one of the most reactive amino acids and it is involved in many biological reactions such as reactions of protein synthesis etc. This behaviour makes cysteine a crucial target for its function determination in a given protein. Generally, the experimental determination of amino acid function is expensive and not time efficient. And, computational methods handle these two things extremely well. The only drawback of a computational method can be its relative accuracy when compared to experimental methods. This is the prime objective of the project. The project talks about neural-network oriented computational techniques and its implementation for the prediction of cysteine functions. The predictive model requires four inputs, namely Uniprot ID, Residue ID, modifications, and sequences. The seven functions of cysteine explored in the project are Disulfide, S-Glutathionylation, Metal-Binding, Nitrosylation, Palmitoylation, Thioether and Sulfenylation.

The code for preprocessing (generation of word embeddings / protein vectors using word2vec)can be found in ***/Data Preprocessing*** folder. And, the code for the deep learning models (with cross validation and sampling methods) can be found in ***/cyspy*** folder. DL models can be run using the script ***dl_models_run.py***. The epochs and batch size used for all the models are 100 and 128 respectively. Different activation functions were used for different models for hidden layers but for final connected layer in all the models, *softmax* activation function was used.

DL models used are CNN, ANN, GRU, LSTM, BILSTM and they can be run by a command of the format:
> python3 dl_models_run.py GRU

The inputs to the models are two pickle files one contains the protein vector embeddings and the other one contains respective modifications numbered from 0 to 7 as classes. Sample data and input:
> >P0C1A9_192
> >SDCRIS
Where, P0C1A9 is uniprot_id and 192 is residue_id means at 192th postion cysteine is present. SDCRIS is the trimmed sequence from a large protein sequence.
