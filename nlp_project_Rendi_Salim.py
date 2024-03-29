# -*- coding: utf-8 -*-
"""NLP_project.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1zulvQ4mW5JXAXLRNjETFclwgomWRQaQY

## Nama: Rendi Salim
## Email: rendisalim10@gmail.com
"""

!pip install -q kaggle
from google.colab import files
files.upload()

# Commented out IPython magic to ensure Python compatibility.
# %cd //

!pwd

!mkdir -p ~/.kaggle
!cp kaggle.json ~/.kaggle/
!ls ~/.kaggle
!chmod 600 /root/.kaggle/kaggle.json

!mkdir NLP_project

!kaggle datasets download -d mrutyunjaybiswal/iitjee-neet-aims-students-questions-data -p /NLP_project

#Extract data 
import zipfile, os
localZip = '/NLP_project/iitjee-neet-aims-students-questions-data.zip'
zipRef = zipfile.ZipFile(localZip, 'r')
zipRef.extractall('/NLP_project')
zipRef.close()

# Commented out IPython magic to ensure Python compatibility.
# %cd /NLP_project/

import pandas as pd
df = pd.read_csv('subjects-questions.csv')
df.head()

df.info()

df.rename(columns={'eng':'Question'}, inplace = True)

len(df[df.duplicated()])

df.drop_duplicates(inplace=True)

df.info()

df['Question']

df['Subject'].value_counts()

#mengambil 10000 data untuk setiap kelas
dfPhysics = df[df['Subject'] == 'Physics'].sample(n=10000, random_state=1)
dfChem = df[df['Subject'] == 'Chemistry'].sample(n=10000, random_state=1)
dfMath = df[df['Subject'] == 'Maths'].sample(n=10000, random_state=1)
dfBio = df[df['Subject'] == 'Biology'].sample(n=10000, random_state=1)

frames = [dfPhysics, dfChem, dfMath, dfBio]
dfClean = pd.concat(frames,
                  ignore_index = True)

#one-hot-encoding
subject = pd.get_dummies(dfClean['Subject'])
dfBaru = pd.concat([dfClean, subject], axis=1)
dfBaru.drop(columns='Subject', inplace=True)
dfBaru.head()

#ubah data menjadi numpy array
question = dfBaru['Question'].values
label = dfBaru[['Biology', 'Chemistry', 'Maths', 'Physics']].values

from sklearn.model_selection import train_test_split
questionTrain, questionTest, labelTrain, labelTest = train_test_split(question, label, test_size=0.2)

print('Total sample = ', len(dfBaru))
print('Total data train = ', len(questionTrain))
print('Total data validation = ', len(questionTest))

from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences

tokenizer = Tokenizer(num_words=50000, oov_token ='x')
tokenizer.fit_on_texts(questionTrain)
tokenizer.fit_on_texts(questionTest)

sequenceTrain = tokenizer.texts_to_sequences(questionTrain)
sequenceTest = tokenizer.texts_to_sequences(questionTest)

paddedTrain = pad_sequences(sequenceTrain)
paddedTest = pad_sequences(sequenceTest)

class Callback(tf.keras.callbacks.Callback):
  def on_epoch_end(self, epoch, logs={}):
    if(logs.get('accuracy') > 0.91 and logs.get('val_accuracy') > 0.91):
      self.model.stop_training = True

callbacks = Callback()

#Model Evaluation plot
import matplotlib.pyplot as plt

def evalPlot(training):
  plt.style.use('seaborn')
  plt.figure(figsize = (8,6))

  plt.subplot(1,2,1)
  trainAcc = training.history['accuracy']
  valAcc = training.history['val_accuracy']
  epoch = range(len(trainAcc))
  trainAccPlot = plt.plot(epoch, trainAcc, 'r')
  valAccPlot = plt.plot(epoch, valAcc, 'b')
  plt.title('Akurasi training vs Akurasi Validasi')
  plt.legend(['Train Accuracy', 'Validation Accuracy'], loc=0)

  plt.subplot(1,2,2)
  trainLoss = training.history['loss']
  valLoss = training.history['val_loss']
  trainLossPlt = plt.plot(epoch, trainLoss, 'r')
  valLossPlt = plt.plot(epoch, valLoss, 'b')
  plt.title('Loss Training vs Loss Validasi')
  plt.legend(['Train Loss', 'Validation Loss'], loc=0)

import tensorflow as tf
model = tf.keras.Sequential([
    tf.keras.layers.Embedding(input_dim=50000, output_dim=16),
    tf.keras.layers.LSTM(64),
    tf.keras.layers.Dense(256, activation = 'sigmoid'),
    tf.keras.layers.Dropout(0.5),
    tf.keras.layers.Dense(128, activation = 'sigmoid'),
    tf.keras.layers.Dropout(0.2),
    tf.keras.layers.Dense(64, activation = 'relu'),
    tf.keras.layers.Dropout(0.2),
    tf.keras.layers.Dense(4, activation = 'softmax')
])

model.compile(loss='categorical_crossentropy',
              optimizer = 'adam',
              metrics = ['accuracy'])

history = model.fit(paddedTrain, labelTrain, 
              epochs=50,
              validation_data = (paddedTest, labelTest),
              verbose = 2,
              batch_size = 100,
              callbacks=[callbacks])

evalPlot(history)

import numpy as np
newQuestion = ['Why is tartaric acid added into baking soda to get baking powder?']
seq = tokenizer.texts_to_sequences(newQuestion)
padded = pad_sequences(seq)
pred = model.predict(padded)
label = ['Biology', 'Chemistry', 'Maths', 'Physics']
print(pred, label[np.argmax(pred)])

