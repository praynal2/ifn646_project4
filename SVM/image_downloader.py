from tcia_utils import nbia
import pandas as pd
import requests
import logging

# Check current handlers
# print(logging.root.handlers)

# Remove all handlers associated with the root logger object.
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
# print(logging.root.handlers)

# Set handler with level = info
logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s',
                    level=logging.INFO)

print("Logging set to INFO")

path = "..."  ## Destination 

import os

df1 = pd.read_csv(path + '\mass_case_description_train_set.csv')
df2 = pd.read_csv(path + '\calc_case_description_train_set.csv')

## Get a subset of patient 
## 100 first ones for example
nb = 100
df1 = df1[0:nb]
df2 = df2[0:nb]

def download_images(df, nb):
    
    ## Save information for the dataset
    pathologies = df['pathology']
    info = df['image file path'].str.split('/')  ## Only the classic images, change for cropped ones
    series = info.apply(lambda x: x[2]) 
    
    for i in range(nb) : 
        folder = pathologies[i]
        uids = nbia.getSopInstanceUids(seriesUid = series[i])
        if uids: 
            for uid in uids : 
                nbia.downloadImage(seriesUID = series[i], sopUID = uid.get('SOPInstanceUID'), path = os.path.join(path, folder))
        
download_images(df1, nb)
download_images(df2, nb)


## Cleaning folder

folders = ['BENIGN', 'MALIGNANT']
index = 1

import pydicom
import cv2
import matplotlib.pyplot as plt

for folder in folders : 
    
    main = os.path.join(path_bis, folder)    
    for root, dirs, files in os.walk(main):
        
        for directory in dirs : 
            for file in os.listdir(os.path.join(main, directory)):
                if file.endswith('.dcm'):
                
                    dcm_file = os.path.join(main, directory, file)
                    ds = pydicom.dcmread(dcm_file)

                    image_data = ds.pixel_array
                    normalized_image_data = cv2.normalize(image_data, None, 0, 255, cv2.NORM_MINMAX)

                    image_filename = str(index) + '.jpg'  
                    image_path = os.path.join(main, image_filename)
                    cv2.imwrite(image_path, normalized_image_data)

  #                 os.remove(dcm_file)  ##Uncomment to remove dcm_file

                    index += 1
            
        