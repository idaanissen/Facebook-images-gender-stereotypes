# -*- coding: utf-8 -*-
"""
Created on Tue Feb 22 12:11:09 2022

@author: Ida Anthonj Nissen
"""

#Structure:
    #Code for research question (RQ) 2: correctly predicted females and males
    #Code for RQ 3: falsely predicted categories
        #Part 1: falsely predicted to be males but are females vs. correctly predicted males
        #Part 2: falsely predicted to be females but are males vs. correctly predicted females


import pandas as pd
import scipy.stats as stats
from scipy.stats import chi2_contingency
from statsmodels.stats.multitest import fdrcorrection
import numpy as np
import matplotlib.pyplot as plt
 

#%% Import datasets
#Import agreed rating from excel files
Data_agreed = pd.read_excel('FILE_NAME.xlsx') #Load Your Dataframe
Data_agreed.head()



##########################################################################################
#%% RQ2: USING ONLY CORRECTLY PREDICTED IMAGES

#Label images: which images were uploaded by males and females?
#Comparison 1 (RQ 2)
#Correctly predicted females: images 0-199
#Correctly predicted males: images 200-399


##make separate datasets
#Data_M_corr = Data_agreed.iloc[201:401,1:15]
#Data_M_corr = Data_M_corr.reset_index(drop=True)
#Data_M_corr = Data_agreed.iloc[201:211,1:15]
#Data_M_corr = Data_M_corr.reset_index(drop=True)

#Select only correctly predicted images and make one dataset
Data_agreed_corr = Data_agreed.iloc[1:401,1:15]
Data_agreed_corr = Data_agreed_corr.reset_index(drop=True)

##Test of the first 10 of each gender
#Data_agreed_corr = Data_agreed.iloc[[1,2,3,4,5,6,7,8,9,10, 201,202,203,204,205,206,207,208,209,210],1:15]
#Data_agreed_corr = Data_agreed_corr.reset_index(drop=True)

#add column with F and M labels
label =  [ele for ele in ['F', 'M'] for i in range(200)]
Data_agreed_corr['label'] = label



#%% Statistics using scipy
#Chi-square tests for homogeneity. Calculated the same way as Chi-square test for independence
#https://www.simplypsychology.org/chi-square.html
#https://towardsdatascience.com/chi-square-test-with-python-d8ba98117626

#Loop through all 14 variables
var = list(Data_agreed_corr.columns)
var.pop()   #remove the last column (with F/M labels)
p_value_list = []
chi2_list = []
dof_list = []

for v in var:
    # create contingency table
    data_crosstab_totals = pd.crosstab(index=Data_agreed_corr['label'], columns=Data_agreed_corr[v], dropna=True, margins=True, margins_name="Total")
    
    if v == 'Design':   #add zero counts to third option for 'Design', as none felt into that category and hence they do not show in the crosstab. But since they were an option, they must be included.
        data_crosstab_totals.insert(2, '2', [0, 0, 0])  #insert at third position, before total column
    if v == 'Children':   #add option 20+ for 'Children', as none felt into that category and hence they do not show in the crosstab. But since they were an option, they must be included.
        data_crosstab_totals.insert(5, '5', [0, 0, 0])
        

    print(v)
    print(data_crosstab_totals)
    #remove 'total' columns for calculations of chi2 (as it affects the p-value and dof)
    data_crosstab = pd.crosstab(index=Data_agreed_corr['label'], columns=Data_agreed_corr[v])
    
    #Calculate chi2 and p-value
    [chi2, p, dof, expected] = chi2_contingency(data_crosstab)
    print("For variable", v, ", chi-square score is:", chi2, " and dof is:", dof)
    chi2_list.append(chi2)
    dof_list.append(dof)
    
    # interpret p-value
    p_value_list.append(p)
    #alpha = 0.05 / len(var) #Bonferroni corrected     #apply FDR correction at the end instead
    alpha = 0.05
    print("p value is " + str(p))
    if p <= alpha:
        print('Null hypothesis is rejected.')
    else:
        print('Failed to reject the null hypothesis')
    
    
    ### EXPORT TO EXCEL
    #Export to excel
    out = pd.DataFrame([['chi2', chi2], ['dof', dof], ['p', p]])
    writer = pd.ExcelWriter(r'PATH\chisquare_{}.xlsx'.format(v), engine='xlsxwriter')
    
    # Write each dataframe to a different worksheet.
    data_crosstab_totals.to_excel(writer, sheet_name='crosstab', encoding='utf-8-sig')
    out.to_excel(writer, index=False, header=False, sheet_name='stats', encoding='utf-8-sig')
    # Close the Pandas Excel writer and output the Excel file.
    writer.save()
    writer.close()
    

#FDR correction (BH)
[rejected, q_value] = fdrcorrection(p_value_list, alpha=0.05, method='indep')


#%% Export to excel
out_lists = pd.DataFrame(list(zip(chi2_list, dof_list, p_value_list, q_value, rejected)), columns =['chi2', 'dof', 'p_values', 'q_values', 'rejected']).T
out_lists.to_excel(r'PATH\FDR_results.xlsx', encoding='utf-8-sig')



#%% MAKE FIGURES

# set width of bar
barWidth = 0.25
x_tick_labels = ['a','b','c','d']
#From coding list:
x_tick_labels = {var[0]: ['photograph', 'no photograph', 'blank/uniform'],
                 var[1]: ['no humans', 'humans'],
                 var[2]: ['character', 'animal', 'object', 'landscape', 'text', 'other'],
                 var[3]: ['0', '1', '2', '3-5', '6-20', '20+'],
                 var[4]: ['0', '1', '2', '3-5', '6-20', '20+'],
                 var[5]: ['all female', 'all male', 'mixed', 'unclear'],
                 var[6]: ['action', 'sports ongoing', 'sports-related', 'ceremonies', 'military', 'other'],
                 var[7]: ['facing camera', 'not facing camera', 'differing'],
                 var[8]: ['center', 'off-center', 'differing'],
                 var[9]: ['partial face', 'face', 'upper body', 'full body', 'other'],
                 var[10]: ['indoors', 'outdoors', 'NA'],
                 var[11]: ['no object', 'vehicle', 'alcohol', 'building', 'food', 'flowers', 'sign', 'other'],
                 var[12]: ['no animal', 'pets', 'wild', 'domesticated'],
                 var[13]: ['sunset', 'nature', 'panorama', 'other']}

for v in var:
    
    #generate crosstable again
    data_crosstab = pd.crosstab(index=Data_agreed_corr['label'], columns=Data_agreed_corr[v])
    
    if v == 'Design':   #add zero counts to third option for 'Design', as none felt into that category and hence they do not show in the crosstab. But since they were an option, they must be included.
        data_crosstab[2] = [0, 0]
    
    if v == 'Children':   #add option 20+ for 'Children', as none felt into that category and hence they do not show in the crosstab. But since they were an option, they must be included.
        data_crosstab[5] = [0, 0]
    
    print(data_crosstab)
    
    #fig, ax = plt.subplots(figsize = (12, 8))
    fig, ax = plt.subplots()
    
    # Set position of bar on X axis
    x_values = list(data_crosstab.columns)  #get column names for x-axis ticks
    br1 = [x - barWidth/2 for x in x_values]
    br2 = [x + barWidth/2 for x in x_values]
    
    #y-values
    sum_cat = data_crosstab.sum(axis=1)
    #NB: check the order of the crosstab output, the 'label' will be order alphabetically
    occ1 = data_crosstab.iloc[0,:]
    occ2 = data_crosstab.iloc[1,:]
    #y1 = data_crosstab.iloc[0,:]/sum(data_crosstab.sum(axis=1))*100
    #y2 = data_crosstab.iloc[1,:]/sum(data_crosstab.sum(axis=1))*100
    #y1 = occ1/sum_cat[0]*100
    #y2 = occ2/sum_cat[1]*100
    y1 = occ1
    y2 = occ2
   
    
    # Make the plot
    rects1 = plt.bar(br1, y1, color ='r', width = barWidth, edgecolor ='grey', label ='Females')
    rects2 = plt.bar(br2, y2, color ='g', width = barWidth, edgecolor ='grey', label ='Males')
     
    # Adding to plot
    if v == 'Non_Human':
        plt.title('Non-human', fontsize = 28)
    else:
        plt.title(v, fontsize = 28)
    #plt.xlabel('Option', fontsize = 15)
    #plt.ylabel('Percentage', fontsize = 15)
    plt.ylabel('Occurence', fontsize = 15)
    x_ticks_loc = [r for r in range(len(x_values))]
    plt.xticks(x_ticks_loc, labels = x_tick_labels[v], fontsize = 14)
    #plt.xticks(['a','b','c','d'], x_values, fontsize = 14)
    plt.yticks(fontsize=14) 
    plt.box(False)
    plt.legend(fontsize = 14)
    
    if v == 'Non_Human' or v == 'Events' or v == 'Body' or v == 'Object':
        plt.xticks(rotation=45)
    
    # #add value on top of bar  
    ax.bar_label(rects1, labels= occ1, padding=3)
    ax.bar_label(rects2, labels= occ2, padding=3)
    
    #Save figures
    plt.savefig(r'PATH\Statistics_RQ2\Fig_{}.png'.format(v), dpi=300, bbox_inches='tight')
    plt.show()
    

    
##############################################################################
#%% RQ3: ANALYZING FALSELY PREDICTED IMAGES

#Part 1: Falsely predicted to be male but are female VS correctly predicted MALES

#Falsely predicted to be males but are females: images 400-599
#Correctly predicted males: images 200-399

#Select only correctly predicted images and make one dataset
Data_agreed_falseF = Data_agreed.iloc[401:601,1:15]
Data_agreed_falseF = Data_agreed_falseF.reset_index(drop=True)

Data_agreed_corrM = Data_agreed.iloc[201:401,1:15]
Data_agreed_corrM = Data_agreed_corrM.reset_index(drop=True)

#Merge into one dataframe
Data_agreed_FM = pd.concat([Data_agreed_falseF, Data_agreed_corrM], axis=0, ignore_index=True)

#add column with false and correct labels
label =  [ele for ele in ['falseF', 'corrM'] for i in range(200)]
Data_agreed_FM['label'] = label


#%% Statistics using scipy
#Chi-square tests for homogeneity. Calculated the same way as Chi-square test for independence
#https://www.simplypsychology.org/chi-square.html
#https://towardsdatascience.com/chi-square-test-with-python-d8ba98117626

#Loop through all 14 variables
var = list(Data_agreed_FM.columns)
var.pop()   #remove the last column (with false/correct labels)
p_value_list = []
chi2_list = []
dof_list = []

for v in var:
    # create contingency table
    data_crosstab_totals = pd.crosstab(index=Data_agreed_FM['label'], columns=Data_agreed_FM[v], dropna=True, margins=True, margins_name="Total")
    
    if v == 'Children':   #add option 20+ for 'Children', as none felt into that category and hence they do not show in the crosstab. But since they were an option, they must be included.
        data_crosstab_totals.insert(5, '5', [0, 0, 0])
        
    print(v)
    print(data_crosstab_totals)
    #remove 'total' columns for calculations of chi2 (as it affects the p-value and dof)
    data_crosstab = pd.crosstab(index=Data_agreed_FM['label'], columns=Data_agreed_FM[v])
    #print(data_crosstab)
    
    #Calculate chi2 and p-value
    [chi2, p, dof, expected] = chi2_contingency(data_crosstab)
    print("For variable", v, ", chi-square score is:", chi2, " and dof is:", dof)
    chi2_list.append(chi2)
    dof_list.append(dof)
    
    # interpret p-value
    p_value_list.append(p)
    #alpha = 0.05 / len(var) #Bonferroni corrected     #apply FDR correction at the end instead
    alpha = 0.05
    print("p value is " + str(p))
    if p <= alpha:
        print('Null hypothesis is rejected.')
    else:
        print('Failed to reject the null hypothesis')
    
    
    ### EXPORT TO EXCEL
    #Export to excel
    out = pd.DataFrame([['chi2', chi2], ['dof', dof], ['p', p]])
    writer = pd.ExcelWriter(r'PATH\Statistics_RQ3_FalseF_vs_CorrM\chisquare_{}.xlsx'.format(v), engine='xlsxwriter')
    
    # Write each dataframe to a different worksheet.
    data_crosstab_totals.to_excel(writer, sheet_name='crosstab', encoding='utf-8-sig')
    out.to_excel(writer, index=False, header=False, sheet_name='stats', encoding='utf-8-sig')
    # Close the Pandas Excel writer and output the Excel file.
    writer.save()
    writer.close()
    

#FDR correction (BH)
[rejected, q_value] = fdrcorrection(p_value_list, alpha=0.05, method='indep')


#%% Export to excel
out_lists = pd.DataFrame(list(zip(chi2_list, dof_list, p_value_list, q_value, rejected)), columns =['chi2', 'dof', 'p_values', 'q_values', 'rejected']).T
out_lists.to_excel(r'PATH\Statistics_RQ3_FalseF_vs_CorrM\FDR_results.xlsx', encoding='utf-8-sig')


#%% MAKE FIGURES

# set width of bar
barWidth = 0.25
x_tick_labels = ['a','b','c','d']
#From coding list:
x_tick_labels = {var[0]: ['photograph', 'no photograph', 'blank/uniform'],
                 var[1]: ['no humans', 'humans'],
                 var[2]: ['character', 'animal', 'object', 'landscape', 'text', 'other'],
                 var[3]: ['0', '1', '2', '3-5', '6-20', '20+'],
                 var[4]: ['0', '1', '2', '3-5', '6-20', '20+'],
                 var[5]: ['all female', 'all male', 'mixed', 'unclear'],
                 var[6]: ['action', 'sports ongoing', 'sports-related', 'ceremonies', 'military', 'other'],
                 var[7]: ['facing camera', 'not facing camera', 'differing'],
                 var[8]: ['center', 'off-center', 'differing'],
                 var[9]: ['partial face', 'face', 'upper body', 'full body', 'other'],
                 var[10]: ['indoors', 'outdoors', 'NA'],
                 var[11]: ['no object', 'vehicle', 'alcohol', 'building', 'food', 'flowers', 'sign', 'other'],
                 var[12]: ['no animal', 'pets', 'wild', 'domesticated'],
                 var[13]: ['sunset', 'nature', 'panorama', 'other']}

for v in var:
    
    #generate crosstable again
    data_crosstab = pd.crosstab(index=Data_agreed_FM['label'], columns=Data_agreed_FM[v])
    
    if v == 'Children':   #add option 20+ for 'Children', as none felt into that category and hence they do not show in the crosstab. But since they were an option, they must be included.
        data_crosstab[5] = [0, 0]
    
    print(data_crosstab)
    
    #fig, ax = plt.subplots(figsize = (12, 8))
    fig, ax = plt.subplots()
    
    # Set position of bar on X axis
    x_values = list(data_crosstab.columns)  #get column names for x-axis ticks
    br1 = [x - barWidth/2 for x in x_values]
    br2 = [x + barWidth/2 for x in x_values]
    
    #y-values
    sum_cat = data_crosstab.sum(axis=1)
    #NB: check the order of the crosstab output, the 'label' will be order alphabetically
    occ2 = data_crosstab.iloc[0,:]
    occ1 = data_crosstab.iloc[1,:]
    #y1 = occ1/sum_cat[0]*100
    #y2 = occ2/sum_cat[1]*100
    y1 = occ1
    y2 = occ2
    
    # Make the plot
    rects1 = plt.bar(br1, y1, color ='y', width = barWidth, edgecolor ='grey', label ='False F')
    rects2 = plt.bar(br2, y2, color ='g', width = barWidth, edgecolor ='grey', label ='Correct M')
    
    # Adding to plot
    if v == 'Non_Human':
        plt.title('Non-human', fontsize = 28)
    else:
        plt.title(v, fontsize = 28)
    #plt.xlabel('Option', fontsize = 15)
    #plt.ylabel('Percentage', fontsize = 15)
    plt.ylabel('Occurence', fontsize = 15)
    x_ticks_loc = [r for r in range(len(x_values))]
    plt.xticks(x_ticks_loc, labels = x_tick_labels[v], fontsize = 14)
    #plt.xticks(['a','b','c','d'], x_values, fontsize = 14)
    plt.yticks(fontsize=14) 
    plt.box(False)
    plt.legend(fontsize = 14)
    
    if v == 'Non_Human' or v == 'Events' or v == 'Body' or v == 'Object':
        plt.xticks(rotation=45)
    
    # #add value on top of bar  
    ax.bar_label(rects1, labels= occ1, padding=3)
    ax.bar_label(rects2, labels= occ2, padding=3)
    
    #Save figures
    plt.savefig(r'PATH\Statistics_RQ3_FalseF_vs_CorrM\Fig_{}.png'.format(v), dpi=300, bbox_inches='tight')
    plt.show()
    



#Part 2: Falsely predicted to be female but are male VS correctly predicted FEMALES

#Falsely predicted to be females but are males: images 600-799
#Correctly predicted females: images 0-199

#Select only correctly predicted images and make one dataset
Data_agreed_falseM = Data_agreed.iloc[601:801,1:15]
Data_agreed_falseM = Data_agreed_falseM.reset_index(drop=True)

Data_agreed_corrF = Data_agreed.iloc[1:201,1:15]
Data_agreed_corrF = Data_agreed_corrF.reset_index(drop=True)

#Merge into one dataframe
Data_agreed_MF = pd.concat([Data_agreed_falseM, Data_agreed_corrF], axis=0, ignore_index=True)

#add column with false and correct labels
label =  [ele for ele in ['falseM', 'corrF'] for i in range(200)]
Data_agreed_MF['label'] = label


#%% Statistics using scipy
#Chi-square tests for homogeneity. Calculated the same way as Chi-square test for independence
#https://www.simplypsychology.org/chi-square.html
#https://towardsdatascience.com/chi-square-test-with-python-d8ba98117626

#Loop through all 14 variables
var = list(Data_agreed_MF.columns)
var.pop()   #remove the last column (with false/correct labels)
p_value_list = []
chi2_list = []
dof_list = []

for v in var:
    # create contingency table
    data_crosstab_totals = pd.crosstab(index=Data_agreed_MF['label'], columns=Data_agreed_MF[v], dropna=True, margins=True, margins_name="Total")
    
    if v == 'Design':   #add zero counts to third option for 'Design', as none felt into that category and hence they do not show in the crosstab. But since they were an option, they must be included.
        data_crosstab_totals.insert(2, '2', [0, 0, 0])  #insert at third position, before total column
    if v == 'Children':   #add option 20+ for 'Children', as none felt into that category and hence they do not show in the crosstab. But since they were an option, they must be included.
        data_crosstab_totals.insert(5, '5', [0, 0, 0])    
    if v == 'Events':   #add zero counts to third option for 'Design', as none felt into that category and hence they do not show in the crosstab. But since they were an option, they must be included.
        data_crosstab_totals.insert(4, '4', [0, 0, 0])  #insert at fifth position, before total column
    if v == 'Object':   #add zero counts to third option for 'Design', as none felt into that category and hence they do not show in the crosstab. But since they were an option, they must be included.
        data_crosstab_totals.insert(6, '6', [0, 0, 0])  #insert at seventh position, before total column
    if v == 'Surrounding':   #add zero counts to third option for 'Design', as none felt into that category and hence they do not show in the crosstab. But since they were an option, they must be included.
        data_crosstab_totals.insert(0, '0', [0, 0, 0])  #insert at first position, before total column

    print(v)
    print(data_crosstab_totals)
    #remove 'total' columns for calculations of chi2 (as it affects the p-value and dof)
    data_crosstab = pd.crosstab(index=Data_agreed_MF['label'], columns=Data_agreed_MF[v])
    #print(data_crosstab)
    
    #Calculate chi2 and p-value
    [chi2, p, dof, expected] = chi2_contingency(data_crosstab)
    print("For variable", v, ", chi-square score is:", chi2, " and dof is:", dof)
    chi2_list.append(chi2)
    dof_list.append(dof)
    
    # interpret p-value
    p_value_list.append(p)
    #alpha = 0.05 / len(var) #Bonferroni corrected     #apply FDR correction at the end instead
    alpha = 0.05
    print("p value is " + str(p))
    if p <= alpha:
        print('Null hypothesis is rejected.')
    else:
        print('Failed to reject the null hypothesis')
    
    
    ### EXPORT TO EXCEL
    #Export to excel
    out = pd.DataFrame([['chi2', chi2], ['dof', dof], ['p', p]])
    writer = pd.ExcelWriter(r'PATH\Statistics_RQ3_FalseM_vs_CorrF\chisquare_{}.xlsx'.format(v), engine='xlsxwriter')
    
    # Write each dataframe to a different worksheet.
    data_crosstab_totals.to_excel(writer, sheet_name='crosstab', encoding='utf-8-sig')
    out.to_excel(writer, index=False, header=False, sheet_name='stats', encoding='utf-8-sig')
    # Close the Pandas Excel writer and output the Excel file.
    writer.save()
    writer.close()
    

#FDR correction (BH)
[rejected, q_value] = fdrcorrection(p_value_list, alpha=0.05, method='indep')


#%% Export to excel
out_lists = pd.DataFrame(list(zip(chi2_list, dof_list, p_value_list, q_value, rejected)), columns =['chi2', 'dof', 'p_values', 'q_values', 'rejected']).T
out_lists.to_excel(r'PATH\Statistics_RQ3_FalseM_vs_CorrF\FDR_results.xlsx', encoding='utf-8-sig')


#%% MAKE FIGURES

# set width of bar
barWidth = 0.25
x_tick_labels = ['a','b','c','d']
#From coding list:
x_tick_labels = {var[0]: ['photograph', 'no photograph', 'blank/uniform'],
                 var[1]: ['no humans', 'humans'],
                 var[2]: ['character', 'animal', 'object', 'landscape', 'text', 'other'],
                 var[3]: ['0', '1', '2', '3-5', '6-20', '20+'],
                 var[4]: ['0', '1', '2', '3-5', '6-20', '20+'],
                 var[5]: ['all female', 'all male', 'mixed', 'unclear'],
                 var[6]: ['action', 'sports ongoing', 'sports-related', 'ceremonies', 'military', 'other'],
                 var[7]: ['facing camera', 'not facing camera', 'differing'],
                 var[8]: ['center', 'off-center', 'differing'],
                 var[9]: ['partial face', 'face', 'upper body', 'full body', 'other'],
                 var[10]: ['indoors', 'outdoors', 'NA'],
                 var[11]: ['no object', 'vehicle', 'alcohol', 'building', 'food', 'flowers', 'sign', 'other'],
                 var[12]: ['no animal', 'pets', 'wild', 'domesticated'],
                 var[13]: ['sunset', 'nature', 'panorama', 'other']}

for v in var:
    
    #generate crosstable again
    data_crosstab = pd.crosstab(index=Data_agreed_MF['label'], columns=Data_agreed_MF[v])
    
    if v == 'Design':   #add zero counts to third option for 'Design', as none felt into that category and hence they do not show in the crosstab. But since they were an option, they must be included.
        data_crosstab[2] = [0, 0]
    
    if v == 'Children':   #add option 20+ for 'Children', as none felt into that category and hence they do not show in the crosstab. But since they were an option, they must be included.
        data_crosstab[5] = [0, 0]
    
    if v == 'Events':   #add zero counts to fifth option for 'Events', as none felt into that category and hence they do not show in the crosstab. But since they were an option, they must be included.
        data_crosstab[4] = [0, 0]

    if v == 'Object':   #add zero counts to seventh option for 'Object', as none felt into that category and hence they do not show in the crosstab. But since they were an option, they must be included.
        data_crosstab[6] = [0, 0]
    
    if v == 'Surrounding':   #add zero counts to first option for 'Surrounding', as none felt into that category and hence they do not show in the crosstab. But since they were an option, they must be included.
        data_crosstab[0] = [0, 0]
    
    print(data_crosstab)
    
    #fig, ax = plt.subplots(figsize = (12, 8))
    fig, ax = plt.subplots()
    
    # Set position of bar on X axis
    x_values = list(data_crosstab.columns)  #get column names for x-axis ticks
    br1 = [x - barWidth/2 for x in x_values]
    br2 = [x + barWidth/2 for x in x_values]
    
    #y-values
    sum_cat = data_crosstab.sum(axis=1)
    #NB: check the order of the crosstab output, the 'label' will be order alphabetically
    occ2 = data_crosstab.iloc[0,:]
    occ1 = data_crosstab.iloc[1,:]
    #y1 = occ1/sum_cat[0]*100
    #y2 = occ2/sum_cat[1]*100
    y1 = occ1
    y2 = occ2
    
    # Make the plot
    rects1 = plt.bar(br1, y1, color ='c', width = barWidth, edgecolor ='grey', label ='False M')
    rects2 = plt.bar(br2, y2, color ='r', width = barWidth, edgecolor ='grey', label ='Correct F')
    
    # Adding to plot
    if v == 'Non_Human':
        plt.title('Non-human', fontsize = 28)
    else:
        plt.title(v, fontsize = 28)
    #plt.xlabel('Option', fontsize = 15)
    #plt.ylabel('Percentage', fontsize = 15)
    plt.ylabel('Occurrence', fontsize = 15)
    x_ticks_loc = [r for r in range(len(x_values))]
    plt.xticks(x_ticks_loc, labels = x_tick_labels[v], fontsize = 14)
    #plt.xticks(['a','b','c','d'], x_values, fontsize = 14)
    plt.yticks(fontsize=14) 
    plt.box(False)
    plt.legend(fontsize = 14)
    
    if v == 'Non_Human' or v == 'Events' or v == 'Body' or v == 'Object':
        plt.xticks(rotation=45)
    
    # #add value on top of bar  
    ax.bar_label(rects1, labels= occ1, padding=3)
    ax.bar_label(rects2, labels= occ2, padding=3)
    
    #Save figures
    plt.savefig(r'PATH\Statistics_RQ3_FalseM_vs_CorrF\Fig_{}.png'.format(v), dpi=300, bbox_inches='tight')
    plt.show()
    



