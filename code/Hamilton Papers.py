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


def iterate_place_person(node):
#提取所有的persName和placeName
    global all_persName
    global all_placeName
    
    for child in node:
        if child.tag=='{http://www.tei-c.org/ns/1.0}persName':
            
            #将整个pers的字符全转为str            
            pers_str = ET.tostring(child, encoding='unicode')
            #检查str中是否含lb
            lb_str=r'<ns0:lb.*?>'
            result=re.search(lb_str,pers_str,flags=re.DOTALL)
            if result!=None:
                #如果有lb，则用改进过的名字
                new_str1=re.sub(r'<ns0:orig>.*?</ns0:orig>','',pers_str,flags=re.DOTALL)
            else:
                #如果不含lb，则用原本的名字，即把expan或reg的删掉
                new_str=re.sub(r'<ns0:expan>.*?</ns0:expan>','',pers_str) 
                new_str1=re.sub(r'<ns0:reg>.*?</ns0:reg>','',new_str)
            
            #接下来针对被嵌套tag分离的str，将他们连接起来
            persName=''
            pattern=r'>(.*?)<'
            person_result=re.findall(pattern,new_str1)
            for i in person_result:  #将被tag分离的名字加起来
                persName=persName+i 
            all_persName.append(persName)
            
            
        elif child.tag=='{http://www.tei-c.org/ns/1.0}placeName':              
            xml_str = ET.tostring(child, encoding='unicode')
            lb_str=r'<ns0:lb.*?>'
            result=re.search(lb_str,xml_str,flags=re.DOTALL)
            if result!=None:
                xml_str=re.sub(r'<ns0:orig>.*?</ns0:orig>','',xml_str,flags=re.DOTALL)
            else:            
                xml_str=re.sub(r'<ns0:expan>.*?</ns0:expan>','',xml_str) #把expan中的内容删掉
                xml_str=re.sub(r'<ns0:reg>.*?</ns0:reg>','',xml_str)
            placeName=''
            pattern=r'>(.*?)<' #匹配><之间的东西
            place_result=re.findall(pattern,xml_str)
            

            #print(person_result)
            for i in place_result:  #将被tag分离的名字加起来
                placeName=placeName+i 
            all_placeName.append(placeName)
        else:
            iterate_place_person(child)
            
def transcribe(node):   
#提取纯文本(原文本，保留所有的换行和原文)
    global text
    #将整个text转为str
    text_str=ET.tostring(node, encoding='unicode')
    new_str1=re.sub(r'<ns0:expan>.*?</ns0:expan>','',text_str)
    new_str2=re.sub(r'<ns0:reg>.*?</ns0:reg>','',new_str1)
    new_str3=re.sub(r'<.*?>','',new_str2,flags=re.DOTALL)
    new_str4=new_str3.replace('&amp;','&')
    text=new_str4
    
def match(node):
#将文本与实体类型对应起来
    text_str=ET.tostring(node, encoding='unicode')
    #print(text_str)
    
    #遇到choice,如果有lb保留新的，如果没有保留origin
    choice_pattern=r'<ns0:choice.*?</ns0:choice>'
    choice_matches=re.findall(choice_pattern, text_str,flags=re.S)
    #print(choice_result)
    lb_pattern=r'<ns0:lb.*?>'
    choice_replace_result=[]
    for all_choice in choice_matches:
        if re.search(lb_pattern, all_choice,flags=re.S)!=None:
            all_choice=re.sub(r'<ns0:orig>.*?</ns0:orig>','',all_choice,flags=re.S)
        else:
            all_choice=re.sub(r'<ns0:expan>.*?</ns0:expan>','',all_choice,flags=re.S)
            all_choice=re.sub(r'<ns0:reg>.*?</ns0:reg>','',all_choice,flags=re.S)
        #接下来将choice里所有被tag阻断的字符连接起来
        pattern=r'>(.*?)<' #匹配><之间的东西
        result=re.findall(pattern,all_choice)
        #print(result)
        new_result=''
        for letter in result:
            new_result=new_result+letter
        #print(new_result)
        choice_replace_result.append(new_result)
    #print(choice_replace_result)
    #开始替换全文中的choice
    choice_num=len(choice_replace_result)
    choice_replacements=[]
    choice_index=0
    for i in range(choice_num):
        choice_replacements.append('<ns0:choice>'+choice_replace_result[choice_index]+'</ns0:choice>')
        choice_index+=1
    for match,replacement in zip(choice_matches, choice_replacements):
        text_str=text_str.replace(match,replacement,1)
    
    #接下来是将所有人名tag换成all_persName
    pers_pattern=r'<ns0:persName.*?</ns0:persName>'
    pers_matches=re.findall(pers_pattern,text_str,flags=re.S)
    pers_replacements=[]
    for p in range(len(pers_matches)):
        pers_replacements.append('<ns0:persName>'+'persName'+'</ns0:persName>')
    #将所有的persName的tag全换掉
    for match, replacement in zip(pers_matches, pers_replacements):
        text_str = text_str.replace(match, replacement, 1)
    
    #所有地名也
    place_pattern=r'<ns0:placeName.*?</ns0:placeName>'
    place_matches=re.findall(place_pattern,text_str,flags=re.S)
    place_replacements=[]
    for p in range(len(place_matches)):
        place_replacements.append('<ns0:placeName>'+'placeName'+'</ns0:placeName>')
    #将所有的placeName的tag全换掉
    for match, replacement in zip(place_matches, place_replacements):
        text_str = text_str.replace(match, replacement, 1)
   
    
    text_str=text_str.replace('&amp;','&')
    group_pattern=r'>(.*?)<' #匹配><之间的东西
    group_result=re.findall(group_pattern,text_str,flags=re.S)
    #print(match_result)
    new_group=[]
    #去空值，只把有文本的留下
    for m in group_result:
        if m!='' and m.isspace() == False:
            new_group.append(m)
            
    index=0
    #开始造字典
    text_entity={}
    for i in new_group:
        inter=[]
        index+=1
        if i =='persName':
            inter.append(i)
            inter.append('IOB-pers')
            text_entity[index]=inter
        elif i == 'placeName':
            inter.append(i)
            inter.append('IOB-place')
            text_entity[index]=inter
        else:
            inter.append(i)
            inter.append('')
            text_entity[index]=inter
    #print(text_entity)
    
    pers_index=0
    place_index=0
    for keys, values in text_entity.items():
        if values[0]=='persName':
            values[0]=all_persName[pers_index]
            pers_index+=1
        elif values[0]=='placeName':
            values[0]=all_placeName[place_index]
            place_index+=1
        
    #print(text_entity)
    return text_entity
 
            
        
def token():
    text_entity=match(text_node)
    #print(text_entity)
    #print(text_entity)
    all_tokens=[]
    all_entity=[]
    #print(text_entity)
    
    for keys,values in text_entity.items():
        tt=values[0]
        if len(values[0])==0:
            continue
        word=word_tokenize(tt)
        #print(word)
        
        for w in word:
            #print(w)
            
            all_tokens.append(w)
        
        if values[1]=='IOB-pers':
            if len(word)==1:
                all_entity.append('B-pers')
            else:
                all_entity.append('B-pers')
                for i in range(len(word)-1):
                    all_entity.append('I-pers')
        elif values[1]=='IOB-place':
            if len(word)==1:
                all_entity.append('B-place')
            else:
                all_entity.append('B-place')
                for i in range(len(word)-1):
                    all_entity.append('I-place')
        else:
            for i in range(len(word)):                
                all_entity.append(0)

    return all_tokens,all_entity



def write_csv(file):
    all_tokens,all_entity=token()
    print(len(all_tokens),len(all_entity))
    file=file.replace('.xml','.tsv')
    dataframe = pd.DataFrame({'TOKEN':all_tokens,'NE':all_entity})
    dataframe.to_csv('D:\OneDrive - University College London\Desktop\Corpora\code\MH\%s'%file,encoding="utf_8_sig",index=False)
    
    

if __name__ == "__main__":
    path='D:\OneDrive - University College London\Desktop\Corpora\Mary Hamilton papers\XML_files_minus_project-specific_mark-up_20240212'   
    files= os.listdir(path)
    
    file='AR-HAM-00001-00008-00002-00007.xml'
    all_node=[]
    all_persName=[]
    all_placeName=[]
    text_node=read_file(file)
    iterate_place_person(text_node)
    print(all_persName)
    print(all_placeName)
    #for file in files[0:1598]:  
        #all_node=[]
        #all_persName=[]
        #all_placeName=[]
        #text=''
        #text_node=read_file(file)
        #iterate_place_person(text_node)
        #transcribe(text_node)
        #write_csv(file)
        
   
    
    
    