# -*- coding: utf-8 -*-
"""spoofing.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1WHIgtdG4pplq6g2fzp1CCuZFshs_WvJB
"""

#pip install opencv-python==2.4
 #pip install keras
import keras
# keras.__version__
#pip install Pillow
from google.colab import drive    #mounting local dataset to drive
drive.mount('/content/gdrive')
from PIL import Image
import numpy as np   #NumPy is the fundamental package for scientific computing with Python.
import pandas as pd  # for data manipulation and analysis. In particular, it offers data structures and operations for manipulating numerical tables and time series.


import matplotlib.pyplot as plt   #Matplotlib is a plotting library
import os  #This module provides a portable way of using operating system dependent functionality
from keras.preprocessing.image import load_img  #Keras Preprocessing is the data preprocessing and data augmentation module of the Keras deep learning library
import random    #Generate pseudo-random numbers with various common distributions.

"""**resize the image**

**Printing images from dataset**
"""

PATH = os.getcwd()   #os.getcwd gets current directory
  train_path = PATH+'/gdrive/My Drive/fingerprint/train/real/'
  train_batch = os.listdir(train_path)   #gets the list of the elements in that directory
  img=load_img(train_path+train_batch[0])
  plt.imshow(img)
  for sample in train_batch:
    filename = train_path+sample
    if filename=='/content/gdrive/My Drive/fingerprint/train/real/225__M_Left_little_finger.BMP':
        continue;
    with Image.open(filename) as image: 

      image = image.resize((96,96),Image.ANTIALIAS)
      image.save(filename)
    
     


#displaying 5 random images from train dataset
for x in range(10):
   num = random.randint(1,20)
  
   img = load_img(train_path+train_batch[num])

  print(train_path+train_batch[num])
  plt.imshow(img)   #matplot function to show image
  plt.show()

"""**Importing all required libraries and modules**"""

#import keras layers making functionality
from keras.layers import Input , Dense , Reshape , Flatten , Dropout  
from keras.layers import BatchNormalization , ZeroPadding2D , Activation
from keras.layers.convolutional import UpSampling2D , Conv2D , Conv2DTranspose , Convolution2D
from keras.layers.advanced_activations import LeakyReLU 
from keras.models import load_model
import h5py

#importing keras sequential model

from keras.models import Sequential , Model

#importing keras optimizers 
from keras.optimizers import Adam

#accessing interpeter variable
import sys

"""**creating the model**"""

class DCGAN():
  def __init__(self):
    #preparing image
    self.img_rows = 96
    self.img_cols = 96
    self.channels = 3;
    self.img_shape = (self.img_rows , self.img_cols , self.channels)
    self.latent_dim = 100
    
    #adam optimiser with learning rate 0.0002 and beta1 = 0.5
    optimizer = Adam(0.0002 , 0.5)
    
    #now model building the discriminator
    self.discriminator = self.build_discriminator()
    self.discriminator.compile(optimizer = optimizer , loss='binary_crossentropy' , metrics = ['accuracy'])
    
    #now building the generator
    self.generator = self.build_generator()
    
    
    z = Input(shape=(self.latent_dim,))   #converting noise for input in generator as a tensor
    img = self.generator(z) #passing noise as input in geenrator
    
    
    #Since self.discriminator.trainable = False is set after the discriminator is compiled, it will not affect the training of the discriminator. 
    #However since it is set before the combined model is compiled the discriminator layers will be frozen when the combined model is 
    #trained
    
    self.discriminator.trainable = False
    
    
    #giving inputs to generated image to discriminator
    
    valid = self.discriminator(img)
    
    #creating Model giving input noise and getting output validation
    self.combined = Model(z,valid)
    self.combined.compile(optimizer = optimizer , loss = 'binary_crossentropy')
  
  
  
  def build_generator(self):
    """Creates a generator model that takes a 100-dimensional noise vector as a "seed", and outputs images
    of size 96*96*3."""
    model = Sequential()
    model.add(Dense(1024, activation="relu", input_dim=self.latent_dim))
    model.add(LeakyReLU())
    model.add(Dense(128 * 12 * 12))
    model.add(BatchNormalization())
    model.add(LeakyReLU())
    
    model.add(Reshape((12, 12, 128)))
    bn_axis = -1
    model.add(UpSampling2D())
    model.add(BatchNormalization(momentum=0.8))
    model.add(LeakyReLU())
    model.add(Convolution2D(64, (3, 3), padding='same'))
    model.add(BatchNormalization(momentum=0.8))
    model.add(LeakyReLU())
    model.add(Conv2DTranspose(64, (3, 3), strides=2, padding='same'))
    model.add(Convolution2D(64, (3, 3), padding='same'))
    model.add(BatchNormalization(momentum=0.8))
    model.add(LeakyReLU())
    # Because we normalized training inputs to lie in the range [-1, 1],
    # the tanh function should be used for the output of the generator to ensure its output
    # also lies in this range.
    model.add(Convolution2D(64, (3, 3), padding='same'))
    model.add(Conv2DTranspose(64, (3, 3), strides=2, padding='same'))
    model.add(BatchNormalization(momentum=0.8))
    model.add(LeakyReLU())
    model.add(Convolution2D(self.channels, (3, 3), padding='same', activation='tanh'))
    
    model.summary()

    noise = Input(shape=(self.latent_dim,))
    img = model(noise)
    #img=img.resize((64,64),Image.ANTIALIAS)
    return Model(noise, img) 
  
  def build_discriminator(self):
        model = Sequential()

        model.add(Conv2D(32, kernel_size=3, strides=2, input_shape=self.img_shape, padding="same"))
        model.add(LeakyReLU(alpha=0.2))
        model.add(Dropout(0.25))
        model.add(Conv2D(64, kernel_size=3, strides=2, padding="same"))
        model.add(ZeroPadding2D(padding=((0,1),(0,1))))
        model.add(BatchNormalization(momentum=0.8))
        model.add(LeakyReLU(alpha=0.2))
        model.add(Dropout(0.25))
        model.add(Conv2D(128, kernel_size=3, strides=2, padding="same"))
        model.add(BatchNormalization(momentum=0.8))
        model.add(LeakyReLU(alpha=0.2))
        model.add(Dropout(0.25))
        model.add(Conv2D(256, kernel_size=3, strides=1, padding="same"))
        model.add(BatchNormalization(momentum=0.8))
        model.add(LeakyReLU(alpha=0.2))
        model.add(Dropout(0.25))
        model.add(Flatten())
        model.add(Dense(1, activation='sigmoid'))

        model.summary()

        img = Input(shape=self.img_shape)
        validity = model(img)
        

        return Model(img, validity)
  def train(self , epochs , batch_size = 128 , save_interval=50):
    X_train = train_batch
    list=[]
    for sample in train_batch:

      full = train_path+sample
      if full=='/content/gdrive/My Drive/fingerprint/train/real/225__M_Left_little_finger.BMP':
        continue
      img = Image.open(full)
      #img = img.resize((64,64),Image.ANTIALIAS)
      data = np.asarray(img)
      #print(data.shape)
      list.append(data)
      

    list=np.array(list)
    print(list.size)
    #resizing image to -1 to 1
    list = list/127.5-1
    #list = np.expand_dims(list , axis=3)

    #adversarial ground truth
    valid = np.ones((batch_size,1))
    fake = np.zeros((batch_size,1))

    for epoch in range(epochs):
      #training discriminator
      index = np.random.randint(0,list.shape[0],batch_size)   #selecting random half images
      imgs = list[index]

      #sample noise and generating new images
      noise = np.random.normal(0,1,(batch_size,100))    #creating noise of taking 100 gaussian values
      gen_imgs = self.generator.predict(noise)  #Generates output predictions for the input samples
      
      #train the discriminator loss
      
      d_loss_real = self.discriminator.train_on_batch(imgs, valid)  #train_on_batch gives single gradient over the complete batch
      d_loss_fake = self.discriminator.train_on_batch(gen_imgs, fake)
      d_loss = 0.5 * np.add(d_loss_real, d_loss_fake)     #aggregating the total loss
      print(d_loss_real,d_loss_fake)
      
      #generator training

      g_loss = self.combined.train_on_batch(noise, valid)  #making discriminator make the mistake

      # Plot the progress
      print ("%d [D loss: %f, acc.: %.2f%%] [G loss: %f]" % (epoch, d_loss[0], 100*d_loss[1], g_loss))
      

      # If at save interval => save generated image samples
      if epoch % save_interval == 0:
        self.save_imgs(epoch)
        
  def save_imgs(self, epoch):
        r, c = 2,2
        noise = np.random.normal(0, 1, (r * c, self.latent_dim))
        gen_imgs = self.generator.predict(noise)
       
        # Rescale images 0 - 1
        gen_imgs = 0.5 * gen_imgs + 0.5

        fig, axs = plt.subplots(r, c)
        cnt = 0
        for i in range(r):
            for j in range(c):
                axs[i,j].imshow(gen_imgs[cnt, :,:,0],cmap="gray")
                
                axs[i,j].axis('off')
                cnt += 1
        fig.savefig("/content/gdrive/My Drive/fingerprint/testing/genimg/genimg_%d.JPEG" % epoch)
        
        plt.show()
       
        plt.close('all')
if __name__ == '__main__':
    dcgan = DCGAN()
    
    dcgan.train(epochs=4000, batch_size=32, save_interval=50)    
    
dcgan.generator.save('/content/gdrive/My Drive/fingerprint/'+'dcgan_generator.h5')   
dcgan.discriminator.save('/content/gdrive/My Drive/fingerprint/'+'dcgan_discriminator.h5')
dcgan.combined.save('/content/gdrive/My Drive/fingerprint/'+'dcgan_combined.h5')

# Run this cell to mount your Google Drive.
from google.colab import drive
drive.mount('/content/drive')

newmodel = load_model('/content/gdrive/My Drive/fingerprint/'+'dcgan_discriminator.h5')
newmodel.compile(optimizer=Adam(0.0002,0.5),loss='binary_crossentropy' , metrics = ['accuracy'])
newmodel.summary()
# gen_path=PATH+'/gdrive/My Drive/fingerprint/test/spoof/'
# gen = os.listdir(gen_path)
# list1=[]
# for sample in gen:
#   file=gen_path+sample
#   img=Image.open(file)
#   img=img.resize((96,96),Image.ANTIALIAS)
#   data=np.asarray(img)
  
#   list1.append(data)
# list1=np.array(list1)  
# list1 = list1/127.5-1 
# list1=np.expand_dims(list1,axis=0)
# for sample in list1:
#   ans=newmodel.predict(sample)
#   print(ans)
  
  
path=PATH+'/gdrive/My Drive/fingerprint/train/real/'
training_path=os.listdir(path)
training_list=[]
training_label=[]
for sample in training_path:
  filenaming = path+sample
  img=Image.open(filenaming)
  img=img.resize((96,96),Image.ANTIALIAS)
  data=np.asarray(img)

  training_list.append(data)
  training_label.append(1)
  
  
path=PATH+'/gdrive/My Drive/fingerprint/train/spoofing/'
training_path=os.listdir(path)

for sample in training_path:
  filenaming = path+sample
  img=Image.open(filenaming)
  img=img.resize((96,96),Image.ANTIALIAS)
  data=np.asarray(img)
  
  training_list.append(data)
  training_label.append(0)  

training_list=np.array(training_list)
training_list=training_list/127.5-1
#training_list=np.expand_dims(training_list,axis=)
print(training_list.shape)
training_label=np.array(training_label)
print(training_list.shape)
results=newmodel.fit(training_list,training_label,epochs=100,validation_split=0.2)
print(np.mean(results.history["val_acc"]))
newmodel.evaluate(training_list)
ans=newmodel.predict(training_list)
for x in range(len(ans)):
  if ans[x]==1:
    print("real")
  else:
    print("spoof")
PATH = os.getcwd()   #os.getcwd gets current directory
train_path = PATH+'/gdrive/My Drive/testing/testing/'
train_batch = os.listdir(train_path)   #gets the list of the elements in that directory
#img=load_img(train_path+train_batch[0])
#plt.imshow(img)
listing=[]
for sample in train_batch:
  filename = train_path+sample
#   if filename=='/content/gdrive/My Drive/fingerprint/train/real/225__M_Left_little_finger.BMP':
#       continue;
  with Image.open(filename) as image: 
    
    image = image.resize((96,96),Image.ANTIALIAS)
    data=np.asarray(image)
    listing.append(data)
    #image.save(filename)  
#newmodel.evaluate(training_list,training_label)
listing=np.array(listing)
listing=listing/127.5-1
from sklearn.metrics import precision_score, recall_score
class Metrics(keras.callbacks.Callback):
    def on_train_begin(self, logs={}):
        self._data = []

    def on_epoch_end(self, batch, logs={}):
        X_val, y_val = self.validation_data[0], self.validation_data[1]
        y_predict = np.asarray(newmodel.predict(X_val))

        y_val = np.argmax(y_val, axis=1)
        y_predict = np.argmax(y_predict, axis=1)

        self._data.append({
            'val_recall': recall_score(y_val, y_predict),
            'val_precision': precision_score(y_val, y_predict),
        })
        return

    def get_data(self):
        return self._data


metrics = Metrics()
history = newmodel.fit(training_list,training_label, epochs=100, validation_split=0.2, callbacks=[metrics])
metrics.get_data()
ans=newmodel.predict(listing)
for x in range(len(ans)):
  if ans[x]==1:
    print("real")
  else:
    print("spoof")

"""new**creating a generator class now**"""



"""**Building discriminator class**"""