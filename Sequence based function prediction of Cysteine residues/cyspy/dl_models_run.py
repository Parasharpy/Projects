import argparse
import pandas as pd
import numpy as np
import os
import pickle
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.metrics import confusion_matrix, classification_report
import time

# check if user parameters are valid
parser = argparse.ArgumentParser(description='Run one DL models on protein dataset.')
parser.add_argument('model', help='Name of the model to run it on. Must be one of CNN, GRU, LSTM, BILSTM, ABLE')
parser.add_argument('-e', '--epochs', nargs='?', type=int, default=100, help='Number of epochs for training')
parser.add_argument('-b', '--batch', nargs='?', type=int, default=128, help='Batch size for training')
parser.add_argument('-l', '--lr', nargs='?', type=float, default=1e-4, help='Learning rate for Adam optimizer')
args = parser.parse_args()

if args.model not in ["ANN", "CNN", "GRU", "LSTM", "BILSTM", "ABLE"]:
	print("Model", args.model, "is not defined. Please make changes to dl_models.py and this file")
	exit(0)

## Keras/Tensorflow Imports and Setup
import keras
import tensorflow as tf
from keras.models import Model
from tensorflow.keras.models import load_model
from tensorflow.keras.utils import to_categorical
from keras.utils import np_utils
from keras.regularizers import l2
from tensorflow.compat.v1 import ConfigProto # GPU
from imblearn.over_sampling import SMOTE, ADASYN
from keras import backend as K

gpu_options = tf.compat.v1.GPUOptions(allow_growth=True)
sess = tf.compat.v1.Session(config=tf.compat.v1.ConfigProto(gpu_options=gpu_options))

# import all the neural network models
from dl_models import get_dl_model 

# Load Dataset
with open(r'path_to_X.pickle', 'rb') as infile:
	X = pickle.load(infile)

with open(r'path_to_y.pickle', 'rb') as infile:
	y = pickle.load(infile)


kf = StratifiedKFold(n_splits=10, random_state=1, shuffle=True)
# SAMPLING_METHODS = ["NONE", "SMOTE", "ADASYN"] # sampling methods
SAMPLING_METHODS = ["NONE", "SMOTE", "ADASYN"]

if os.path.exists(args.model + '_results.pickle'):
	with open(args.model + '_results.pickle', 'rb') as f:
		all_results = pickle.load(f)
	resumed_run = True
	last_iter_fold = all_results[-1]['fold']
	last_iter_model = all_results[-1]['model']
	last_iter_sampling = all_results[-1]['sampling']
else:
	all_results = []
	resumed_run = False
	last_iter_fold = None
	last_iter_model = None
	last_iter_sampling = None

fold = 1
for train_index, test_index in kf.split(X, y):
	if resumed_run:
		if fold < last_iter_fold:
			# this fold has already been done, skip
			print("K Fold Cross Validation || Fold #", fold, "already done. Skipped.")
			fold+=1
			continue

	print("K Fold Cross Validation || Fold #", fold)
	X_train, X_test = [X[index] for index in train_index], [X[index] for index in test_index] #vector of vector
	y_train, y_test = [y[index] for index in train_index], [y[index] for index in test_index]
	
	# y_train_dummy = np_utils.to_categorical(y_train, dtype = 'str') #added dtype = 'str'
	
	for sampling_method in SAMPLING_METHODS:
		print("K Fold", fold, "sampling methods begin")
		
		if resumed_run:
			if SAMPLING_METHODS.index(last_iter_sampling) > SAMPLING_METHODS.index(sampling_method):
				print("Fold #", fold, ", sampling", sampling_method, "already done. Skipped.")
				continue
			elif SAMPLING_METHODS.index(last_iter_sampling) == SAMPLING_METHODS.index(sampling_method):
				print("Fold #", fold, ", sampling", sampling_method, "already done. Skipped.")
				resumed_run = False
				continue


		CACHED_FOLD_FILE = "../data/" + sampling_method + "_FOLD_" + str(fold) + ".pickle"

		if sampling_method == "NONE":
			X_resampled = np.asarray(X_train)
			y_resampled =  tf.keras.utils.to_categorical(y_train) #np_utils.to_categorical is changed to tf.keras.utils.to_categorical


		else:
			print(CACHED_FOLD_FILE)
			if os.path.exists(CACHED_FOLD_FILE):
				print("Currently doing ", fold, "with", sampling_method, "Found: ", CACHED_FOLD_FILE)
				with open(CACHED_FOLD_FILE,'rb') as infile:
					X_resampled, y_resampled, X_val, y_val, X_test, y_test = pickle.load(infile)

			elif sampling_method == "SMOTE":
				start_smote = time.time()
				X_resampled, X_val, y_resampled, y_val = train_test_split(X_train, y_train, test_size=0.1)
				y_val = tf.keras.utils.to_categorical(y_val) #np_utils.to_categorical is changed to tf.keras.utils.to_categorical
				X_resampled = np.asarray(X_resampled)
				
				X_resampled = np.reshape(X_resampled, newshape=(X_resampled.shape[0], 300))
				print("Sampling with SMOTE begin")
				X_resampled, y_resampled = SMOTE(random_state=1, n_jobs=3).fit_resample(X_resampled, y_resampled)
				X_resampled = np.reshape(X_resampled, newshape = (X_resampled.shape[0], 3, 100))
				y_resampled = tf.keras.utils.to_categorical(y_resampled) #np_utils.to_categorical is changed to tf.keras.utils.to_categorical
				
				all_data_current_fold = [X_resampled, y_resampled, X_val, y_val, X_test, y_test]
				
				all_data_current_fold = None
				
				print("SMOTE complete in %.2f seconds"%(time.time() - start_smote))

			elif sampling_method == "ADASYN":
				start_adasyn = time.time()
				X_resampled, X_val, y_resampled, y_val = train_test_split(X_train, y_train, test_size=0.1) #remove stratify part
				y_val = np_utils.to_categorical(y_val)
				X_resampled = np.reshape(X_resampled, newshape=(X_resampled.shape[0], 300))
				print("Sampling with ADASYN begin")
				X_resampled, y_resampled = ADASYN(random_state=1, n_jobs=3).fit_resample(X_resampled, y_resampled)
				X_resampled = np.reshape(X_resampled, newshape = (X_resampled.shape[0], 3, 100))
				y_resampled = np_utils.to_categorical(y_resampled)
				print("ADASYN complete in %.2f seconds"%(time.time() - start_adasyn))

				all_data_current_fold = [X_resampled, y_resampled, X_val, y_val, X_test, y_test]
				with open(CACHED_FOLD_FILE, 'wb') as handle:
					pickle.dump(all_data_current_fold, handle)
				
				all_data_current_fold = None

		start_train = time.time()
		model = get_dl_model(args.model)
		print(model.summary())
		opt = tf.keras.optimizers.Adam(learning_rate = args.lr)
		model.compile(loss='categorical_crossentropy', optimizer=opt, metrics=['accuracy'])

		keras_saved_file = "models/" + args.model + "_" + sampling_method + "_" + str(fold) + ".h5"

		mcp_save = keras.callbacks.ModelCheckpoint(keras_saved_file, save_best_only=True, monitor='val_loss', verbose=1)
		reduce_lr = keras.callbacks.ReduceLROnPlateau(monitor='val_loss', factor=0.1, patience=10, verbose=1, mode='auto', min_delta=0.0001, cooldown=0, min_lr=0)
		callbacks_list = [reduce_lr, mcp_save]
		if sampling_method == "NONE":
			history = model.fit(X_resampled, y_resampled, batch_size = args.batch, epochs = args.epochs, validation_split = 0.1, shuffle = True, callbacks = callbacks_list)
		else:
			print("Sampled train dataset: ", X_resampled.shape, y_resampled.shape)
			X_val = np.asarray(X_val)
			y_val = np.asarray(y_val)
			print("Validation dataset: ", X_val.shape, y_val.shape)
			history = model.fit(X_resampled, y_resampled, batch_size = args.batch, epochs = args.epochs, validation_data = (X_val, y_val), shuffle = True, callbacks = callbacks_list)
		
		model = load_model(keras_saved_file)
		end_train = time.time()
		X_test = np.asarray(X_test)
		
		y_pred = model.predict(X_test)

		y_labels = np.argmax(y_pred, axis=1)
		end_test = time.time()

		print(y_pred.shape)
		print(y_labels.shape)
		
		# dump raw predictions
		Y_SAVE_LOCATION_PREFIX = "./results/dl/" + args.model + "_" + sampling_method + "_" + str(fold) + "_" + str(args.epochs) + "_" + str(args.batch)
		np.save(Y_SAVE_LOCATION_PREFIX + "_PRED.npy", y_pred)
		np.save(Y_SAVE_LOCATION_PREFIX + "_TRUE.npy", y_test)

		# Metrics
		filename = "./results/dl/" + args.model + "_" + sampling_method + "_" + str(fold) + "_" + str(args.epochs) + "_" + str(args.batch) + ".npy"
		
		results_dict = {
			"model": args.model,
			"epochs": args.epochs,
			"batch_size": args.batch,
			"initial_lr": args.lr,
			"fold": fold,
			"train_examples": X_resampled.shape[0],
			"sampling": sampling_method, 
			"confusion_matrix": confusion_matrix(y_test, y_labels),
			"report": classification_report(y_test, y_labels, output_dict = True),
			"train_time": end_train - start_train,
			"filename": filename
		}
		
		np.save(filename, history.history)
		#print("Model", args.model, "done running on fold", fold, "with sampling strategy", sampling_method, "in", round(time.time()-start_train, 3), "s")
		all_results.append(results_dict)
		with open(args.model + '_results.pickle', 'wb') as handle:
			pickle.dump(all_results, handle)
		#print("Model", args.model, "on fold", fold, "with sampling strategy", sampling_method, "completed in total of", round(time.time()-start_train, 2), "seconds")
		model = None
		history = None
		K.clear_session()
	fold += 1	
