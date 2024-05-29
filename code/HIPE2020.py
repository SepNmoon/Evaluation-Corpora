# -*- coding: utf-8 -*-
"""
Created on Thu May  9 22:06:27 2024

@author: liulu
"""
import csv
import pandas as pd

hipe=pd.read_csv("D:\OneDrive - University College London\Desktop\HIPE-data-v1.3-test-masked-bundle5-en.tsv", delimiter="\t", quoting=csv.QUOTE_NONE, encoding='utf-8')

hipe=hipe.drop(['NE-COARSE-METO','NE-FINE-LIT','NE-FINE-LIT','NE-FINE-METO','NE-FINE-COMP','NE-NESTED','NEL-LIT','NEL-METO','MISC'],axis=1)
#print(hipe[6100:6150])

hipe1=hipe.drop(hipe.index[6139:18438],inplace=True)
print(hipe)
hipe.to_csv("D:\OneDrive - University College London\Desktop\check\HIPE2020.tsv",index=False,encoding="utf-8")