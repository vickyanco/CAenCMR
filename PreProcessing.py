# file: PreProcessing.py
# description: Process DICOM files to feed the CNN
# author: María Victoria Anconetani
# date: 01/08/2024

import pandas as pd
import numpy as np
import pydicom
import torch
import tensorflow as tf
from skimage.transform import resize
from torch.utils.data import Dataset, DataLoader

class DICOMDataset(Dataset):
    def __init__(self, csv_file, transform=None, new_size=(256, 256)):
        # Load the CSV file containing paths and labels
        self.df = pd.read_csv(csv_file)
        self.transform = transform
        self.new_size = new_size

    def __len__(self):
        # Return the number of images
        return len(self.df)

    def __getitem__(self, idx):
        # Get the image file path from the CSV
        img_path = self.df.iloc[idx]['filepath']
        dicom_file = pydicom.dcmread(img_path)
        image = dicom_file.pixel_array
        
        # Normalize the image
        image = (image - np.min(image)) / (np.max(image) - np.min(image))
        
        # Resize the image
        image = resize(image, self.new_size, anti_aliasing=True)
        
        # Add a channel dimension 
        image = image[np.newaxis, :, :]

        # Convert the image to a tensor
        image = torch.from_numpy(image).float()
        
        # Get the label
        label = self.df.iloc[idx]['label']  # Asume que la etiqueta está en la columna 'label'
        
        # Apply any additional transformations
        if self.transform:
            image = self.transform(image)
        
        return image, label

def load_and_preprocess_image(img_path, label, img_height=256, img_width=256):
    dicom_file = pydicom.dcmread(img_path)
    image = dicom_file.pixel_array
    
    # Normalize the image
    image = (image - np.min(image)) / (np.max(image) - np.min(image))
    
    # Resize the image
    image = tf.image.resize(image, [img_height, img_width])
    
    # Add a channel dimension
    image = tf.expand_dims(image, axis=-1)
    
    return image, label