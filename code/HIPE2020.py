# -*- coding: utf-8 -*-
"""
Created on Thu May  9 22:06:27 2024

@author: liulu
"""
import csv
import pandas as pd
import numpy as np
'''
hipe=pd.read_csv("D:\OneDrive - University College London\Desktop\HIPE-data-v1.3-test-masked-bundle5-en.tsv", delimiter="\t", quoting=csv.QUOTE_NONE, encoding='utf-8')

hipe=hipe.drop(['NE-COARSE-METO','NE-FINE-LIT','NE-FINE-LIT','NE-FINE-METO','NE-FINE-COMP','NE-NESTED','NEL-LIT','NEL-METO','MISC'],axis=1)
#print(hipe[6100:6150])

#hipe1=hipe.drop(hipe.index[6139:18438],inplace=True)

#hipe.to_csv("D:\OneDrive - University College London\Desktop\check\HIPE2020.tsv",index=False,encoding="utf-8")
hipe.drop(hipe.index[6139:18920],inplace=True)
print(hipe)
hipe.dropna(axis=0, how='any', inplace=True)
print(hipe)

hipe.to_csv("D:\OneDrive - University College London\Desktop\check\HIPE2020.tsv",index=False,sep='\t')
'''

def find_index(element_index,hipe_array):
    #print(element_index)
    if hipe_array[element_index][1]=='B-pers':
        print(element_index)
    else:
        element_index-=1
        find_index(element_index,hipe_array)
     

def read_file():
    hipe=pd.read_csv("D:\OneDrive - University College London\Desktop\Evaluation-Corpora\HIPE2020\HIPE2020-Extended.tsv", delimiter="\t", quoting=csv.QUOTE_NONE, encoding='utf-8')
    #print(hipe)
    return hipe

def deal_file(hipe):
    hipe_array=np.array(hipe)
    '''
    hipe_array[1557:1565][1]=0   
    hipe_array[2531:2549][1]=0
    hipe_array[2601:2609][1]=0
    hipe_array[4422:4428][1]=0
    hipe_array[4432:4439][1]=0
    '''
    
    element_index=0
    for element in hipe_array:

        if element_index>=1557 and element_index<=1565:
            hipe_array[element_index][1]=0
        elif element_index>=2531 and element_index<=2549:
            hipe_array[element_index][1]=0
        elif element_index>=2601 and element_index<=2609:
            hipe_array[element_index][1]=0
        elif element_index>=4422 and element_index<=4428:
            hipe_array[element_index][1]=0
        elif element_index>=4432 and element_index<=4439:
            hipe_array[element_index][1]=0
    
        element_index+=1
        
    
    return hipe_array

def write_csv(hipe_array):
    all_tokens=[]
    all_entity=[]
    for element in hipe_array:
        all_tokens.append(element[0])
        all_entity.append(element[1])
        
    dataframe = pd.DataFrame({'TOKEN':all_tokens,'NE':all_entity})
    dataframe.to_csv('D:\OneDrive - University College London\Desktop\HIPE2020-Light.tsv',index=False,sep='\t')
    #test=pd.read_csv("D:\OneDrive - University College London\Desktop\HIPE2020-Light.tsv", delimiter="\t", quoting=csv.QUOTE_NONE, encoding='utf-8')       
    #print(test)


if __name__ == "__main__":
    hipe=read_file()
    hipe_array=deal_file(hipe)
    hipe_array
    print(hipe_array)
    
        
    #write_csv(hipe_array)
