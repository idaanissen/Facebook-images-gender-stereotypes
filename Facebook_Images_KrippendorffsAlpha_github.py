# -*- coding: utf-8 -*-
"""
Created on Fri Jan 28 12:33:48 2022

@author: Ida Anthonj Nissen
"""

#Calculate Krippendorff's alpha on Facebook Image Rating dataset
#Calculates the inter-observer reliability across 14 manually rated variables

#Krippendorff's alpha from: https://github.com/LightTag/simpledorff

import simpledorff
import pandas as pd
import numpy as np


#%% First Rater (rat1)
#Import rating from excel files
Data_rat1 = pd.read_excel('FILE_RATER1') #Load Your Dataframe
Data_rat1.head()

#take out ratings and put them into one columns (rows and columns will become one column with all)
annotation_df_rat1 = Data_rat1.iloc[1:801,1:15]
annotation_col_rat1 = annotation_df_rat1.stack(dropna=False).to_frame()
annotation_col_rat1 = annotation_col_rat1.reset_index(drop=True)

#Create a column with annotater (rater) id (one column with 'rat1')
#empty column with same dimensions as annotation_col
rater_col_rat1 = pd.DataFrame().reindex_like(annotation_col_rat1)
rater_col_rat1[0] = 'rat1'

#Create a column with document id (each variable for each image counts as a document) (one column with ascending numbers)
document_col_rat1 = pd.DataFrame().reindex_like(annotation_col_rat1)
document_col_rat1[0] = document_col_rat1.reset_index().index + 1


#%% Second Rater (rat2)
#Import
Data_rat2 = pd.read_excel('FILE_RATER2') #Load Your Dataframe
Data_rat2.head()

#take out ratings and put them into one columns (rows and columns will become one column with all)
annotation_df_rat2 = Data_rat2.iloc[np.r_[1:201, 203:403, 405:605, 608:808],1:15]
annotation_col_rat2 = annotation_df_rat2.stack(dropna=False).to_frame()
annotation_col_rat2 = annotation_col_rat2.reset_index(drop=True)

#Create a column with annotater (rater) id (one column with 'rat2')
#empty column with same dimensions as annotation_col
rater_col_rat2 = pd.DataFrame().reindex_like(annotation_col_rat2)
rater_col_rat2[0] = 'rat2'

#Create a column with document id (each variable for each image counts as a document) (one column with ascending numbers)
document_col_rat2 = pd.DataFrame().reindex_like(annotation_col_rat2)
document_col_rat2[0] = document_col_rat2.reset_index().index + 1


#%% Combine
annotation_col_all = annotation_col_rat1[0].append(annotation_col_rat2[0], ignore_index=True).to_frame()
rater_col_all = rater_col_rat1[0].append(rater_col_rat2[0], ignore_index=True).to_frame()
document_col_all = document_col_rat1[0].append(document_col_rat2[0], ignore_index=True).to_frame()

#Put columns together into one dataframe
df_all = pd.concat([document_col_all, rater_col_all, annotation_col_all], axis=1)
df_all = df_all.set_axis(['document_id', 'rater_id', 'annotation'], axis=1)


#%% Krippendorff's alpha
simpledorff.calculate_krippendorffs_alpha_for_df(df_all,experiment_col='document_id', annotator_col='rater_id', class_col='annotation')







#%% Create a document that only contains the cells where the reviewers differ

#Identify differing ratings - 1
#Output as a dataframe (rows and columns as the input)

df_agreement = np.equal(annotation_df_rat2.to_numpy(na_value = -1),annotation_df_rat1.to_numpy(na_value = -1)) 
df_agreement = pd.DataFrame(df_agreement)
df_agreement.columns = annotation_df_rat2.columns
df_agreement = df_agreement.replace(to_replace = True, value = np.NaN)
#Export
df_agreement.to_excel(r'FILE2_OUTPUT', index=False, encoding='utf-8-sig')


#Identify differing ratings - 2
#Output as a list with image number for images with disagreement

comparison = annotation_col_rat1[0].eq(annotation_col_rat2[0])|annotation_col_rat1.loc[:, [0,0]].isna().all(1)
#calculate list back to image number (there are 14 columns)
comparison = comparison.tolist()

import math
image_nr = []
for i in range(len(comparison)):
    if comparison[i] == False:
        image_nr.append(math.floor((i+1)/15) + 1)

#Nr. images
new_set = set(image_nr)
len(new_set)

#Put same image numbers into one row
from collections import Counter
counter = Counter(image_nr)

images_for_agreement = pd.DataFrame.from_dict(counter, orient='index').reset_index()
images_for_agreement.columns =['Image nr.', 'occurrence']
#Export
images_for_agreement.to_excel(r'FILE_TO_OUTPUT', index=False, encoding='utf-8-sig')

