# -*- coding: utf-8 -*-
"""
Created on Wed Nov 13 16:21:39 2024

@author: liulu
"""
#本文档尝试提取创造IOB文件时用的text

import xml.etree.ElementTree as ET
import re
from nltk import word_tokenize
import pandas as pd
import os

def read_file(file):
    
    #print(files)
    
    tree=ET.parse('D:\OneDrive - University College London\Desktop\Corpora\Mary Hamilton papers\XML_files_minus_project-specific_mark-up_20240212\%s'%file)
    root=tree.getroot()
    text_node=root.find('{http://www.tei-c.org/ns/1.0}text')
    
    
    return text_node

def extract_text(node):
    text_str=ET.tostring(node, encoding='unicode') 
    #去掉note
    text_str=re.sub(r'<ns0:note.*?</ns0:note>','',text_str)
    #遇到choice,判断sic,org和abbr，之所以要将choice拉出来，因为choice里面会将单词分割
    choice_pattern=r'<ns0:choice.*?</ns0:choice>'
    choice_matches=re.findall(choice_pattern, text_str,flags=re.S)
    sic_str=r'<ns0:sic.*?>'
    expan_str=r'<ns0:expan.*?>'
    lb_str=r'<ns0:lb.*?>'
    choice_replace_result=[]
    for all_choice in choice_matches:
        if re.search(sic_str, all_choice,flags=re.S)!=None:
            all_choice=re.sub(r'<ns0:corr>.*?</ns0:corr>','',all_choice,flags=re.S)
        else:
            all_choice=all_choice
        
        if re.search(expan_str, all_choice,flags=re.S)!=None:
            all_choice=re.sub(r'<ns0:expan>.*?</ns0:expan>','',all_choice,flags=re.S)
        else:
            all_choice=all_choice
        
        if re.search(lb_str, all_choice,flags=re.S)!=None:
            all_choice=re.sub(r'<ns0:orig>.*?</ns0:orig>','',all_choice,flags=re.S)
        else:
            all_choice=re.sub(r'<ns0:reg>.*?</ns0:reg>','',all_choice,flags=re.S)
        #如果有大于一个的空格，即出现了lb情况，则将其替代成一个空格
        space_pattern=r'\s{1,}'
        all_choice=re.sub(space_pattern,' ',all_choice)
        
        #接下来将choice里所有被tag阻断的字符连接起来
        pattern=r'>(.*?)<' #匹配><之间的东西
        result=re.findall(pattern,all_choice)
        #print(result)
        new_result=''
        for letter in result:
            new_result=new_result+letter
        #print(new_result)
        choice_replace_result.append(new_result)
    #开始替换全文中的choice
    choice_num=len(choice_replace_result)
    choice_replacements=[]
    choice_index=0
    for i in range(choice_num):
        choice_replacements.append('<ns0:choice>'+choice_replace_result[choice_index]+'</ns0:choice>')
        choice_index+=1
    for match,replacement in zip(choice_matches, choice_replacements):
        text_str=text_str.replace(match,replacement,1)
    text_str=text_str.replace('&amp;','&')
    group_pattern=r'>(.*?)<' #匹配><之间的东西
    group_result=re.findall(group_pattern,text_str,flags=re.S)
    
    #print(match_result)
    new_group=[]
    #去空值，只把有文本的留下
    for m in group_result:
        if m!='' and m.isspace() == False:
            new_group.append(m)
    
    #print(new_group)
    text_group=[]
    for g in new_group:
        g=g.replace('\n',' ')
        text_group.append(g)
    text=''
    for t in text_group:
        text=text+' '+t
    space_pattern=r'\s{1,}'
    text=re.sub(space_pattern,' ',text)
    print(text)
    
        
    
    #print(text_str)


if __name__ == "__main__":
    path='D:\OneDrive - University College London\Desktop\Corpora\Mary Hamilton papers\XML_files_minus_project-specific_mark-up_20240212'   
    files= os.listdir(path)
    
    for file in files[0:1]: 
        text_node=read_file(file)
        extract_text(text_node)
        