# -*- coding: utf-8 -*-
"""
Created on Wed Feb  2 15:42:31 2022

@author: Ida Anthonj Nissen
"""

#This script makes the figure with the confusion matrix (with larger font and colorbar from [0 1])

#%% Import packages

import matplotlib.pyplot as plt
from sklearn.metrics import ConfusionMatrixDisplay
import numpy as np


#%% Make confusion matrix from classification results
cm = np.array([[0.60, 0.40],[0.32, 0.68]])
display_labels = ('male', 'female')

color_map = plt.cm.get_cmap('gist_heat')
reversed_color_map = color_map.reversed()
plt.rcParams['font.size'] = '15'   #increase font size

disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=display_labels)
disp.plot(cmap=reversed_color_map)
disp.im_.set_clim(0, 1)
#Save figure
plt.savefig(r'PATH\FIG_NAME.png', dpi=300, bbox_inches='tight')
plt.show()

#restore rc changes to default
#plt.style.use('default')



