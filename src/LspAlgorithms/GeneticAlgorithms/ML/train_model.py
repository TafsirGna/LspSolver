# training with a Deep Neural network

import pandas as pd
from tensorflow import keras
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import confusion_matrix, precision_score, recall_score

datasetDirPath = "data/ML/sets/preproc/"
fileRootName = datasetDirPath + "1"
strat_train_set_file_path = fileRootName + "_test_set.csv"

df = pd.read_csv(strat_train_set_file_path)

# corr_matrix = df.iloc[:, :19].corr()
# print(corr_matrix)

training_data_labels = df.iloc[:, -1]
training_data = df.iloc[:, :-1]

# df.head()

scaler = StandardScaler()
training_data = pd.DataFrame(scaler.fit_transform(training_data))

# model = keras.models.Sequential([
#     keras.layers.Flatten(input_shape=[1, 22]),
#     keras.layers.Dense(300, activation="relu"),
#     keras.layers.Dense(100, activation="relu"),
#     keras.layers.Dense(1, activation="sigmoid")
# ])

# model.compile(loss="binary_crossentropy",
#             optimizer="sgd",
#             metrics=["accuracy"]
# )

model = keras.models.load_model("ga_ml_model.h5")

# early_stopping_cb = keras.callbacks.EarlyStopping(patience=10, restore_best_weights=True)

# checkpoint_cb = keras.callbacks.ModelCheckpoint("ga_ml_model.h5", save_best_only=True)

# print(model.fit(training_data, training_data_labels, epochs=100, validation_split=.1, callbacks=[checkpoint_cb, early_stopping_cb]))

# Making predictions
y_train_pred = model.predict(training_data)
y_train_pred = (y_train_pred > .5)

print(confusion_matrix(training_data_labels, y_train_pred))

print(precision_score(training_data_labels, y_train_pred))

print(recall_score(training_data_labels, y_train_pred))

# model.save("ga_ml_model.h5")