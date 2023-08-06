'''
Created on 2011. 12. 9.

@author: HwanSeung Lee(rucifer1217@gmail.com)
'''

import ply.lex as lex
import re#정규표현식 모듈
import math
import logging

# List of token names. This is always required
tokens = (
   'PYL_OUTPUT',
   'PYL',
   'HTML',
) 

def t_PYL_OUTPUT(t):
    r'\{\$\=(.*?)\$\}' 
    t.value = (t.value)
    logging.debug(t)
    return t

def t_PYL(t):
    r'\{\$[^<>]*?\$\}' 
    t.value = (t.value)
    logging.debug(t)
    return t

def t_HTML(t):
    r'[^{$]+' 
    t.value = (t.value)   
    logging.debug(t)  
    return t


# A string containing ignored characters (spaces and tabs)
t_ignore = '\n'

# Error handling rule
def t_error(t):
    logging.debug ("Illegal character '%s'" % t.value[0:40])
    t.lexer.skip(1)

class pylToPy:
    pystring=""
    page=""
    pyl_path=""
    
    blank=0;
    
    def __init__(self,pyl_path,filterStr):
        # 파일 읽기
        self.pyl_path=pyl_path
        if filterStr == "":
            self.page = open('pyl/'+pyl_path, encoding='utf-8').read()
        else:
            self.page += filterStr
            self.page += open('pyl/'+pyl_path, encoding='utf-8').read()
            
            
        self.translationPy()
        pass
    
        
    def translationPy(self):
        pypage = ["# -*- coding: utf-8 -*- \n"]
        pypage.append('import pylatte.web.formFile as formFile\n')
        
        pypage.append('class ' +self.pyl_path.split('.')[0]+':\n')
        pypage.append('\t'+'pylToHtmlResult=""\n')
        pypage.append('\t'+'sessionDic=dict()\n')
        pypage.append('\t'+'def __init__(self,param,pyFile,session,headerInfo,lattedb):\n')
        pypage.append('\t\t'+'self.generate(param,pyFile,session,headerInfo,lattedb)\n\n')
        
        pypage.append('\t'+'def generate(self,param,pyFile,session,headerInfo,lattedb):\n')
        
         # 파이썬 코드 처리
        # Build the lexer
        lexer = lex.lex(debug=1)
        
        # Give the lexer some input
        lexer.input(self.page)
        
        while True:
            tok = lexer.token()
            processResult=""
            if not tok: 
                break # No more input
            else:
                if tok.type=="PYL":
                    processResult=self.processPyl(tok.type, tok.value, tok.lineno, tok.lexpos)
                elif tok.type=="PYL_OUTPUT":
                    processResult=self.processPylOut(tok.type, tok.value, tok.lineno, tok.lexpos)
                elif tok.type=="HTML":
                    processResult=self.processHTML(tok.type, tok.value, tok.lineno, tok.lexpos)
                elif tok.type=="HTML" or tok.type=="HTML_L" or tok.type=="HTML_R" or tok.type=="NOHTML":
                    processResult=self.processNotPyl(tok.type, tok.value, tok.lineno, tok.lexpos)
            pypage.append(processResult)
             
        #logging.debug("end!!")   
        pypage.append('\t\t'+'self.sessionDic=session\n')
        pypage.append('\t\t'+'pass\n')
        pypage.append('\t'+'def getHtml(self):\n')
        pypage.append('\t\t'+'return self.pylToHtmlResult\n')
        pypage.append('\t\t'+'pass\n')
        pypage.append('\t'+'def getSession(self):\n')
        pypage.append('\t\t'+'return self.sessionDic\n')
        pypage.append('\t\t'+'pass\n') 
        # 파이썬 코드 만들어보기
        
        ##logging.debug(type(pypage))
        ##logging.debug(type(self.pystring))
        pystring = ""
        for p in pypage:
            if p=='\n':
                pystring += "\n\t\t"
            else:
                pystring += p
                
        self.pystring=pystring
        pass
        
    def processPyl(self, type,value,lineno,lexpos):
        #remove whitespace front PYL CODE
        value=value[value.rfind("{$"):]
        #logging.debug("***\n"+value+"\n***")

        content=value[3:-3];
        
        #logging.debug("+++"+t.value[-2:]+"##")
        if value[0:3]=="{$\n" and value[-3:]=="\n$}":
            try:
                firstNPos=content.index("\n")
                #logging.debug("Value", firstNPos, secondNPos)
                firstLineCotent=content[:firstNPos]
            except ValueError:
                #logging.debug("ValueError")
                firstLineCotent=content
            finally:
                #logging.debug("&&"+firstLineCotent+"&&")
                localTapCount=0
                localSpaceCount=0
                space="\n\t\t"
                for i in firstLineCotent:
                    if i == '\n':
                        localTapCount=0
                        localSpaceCount=0
                    elif i == '\t':
                        localTapCount+=1;
                    elif i == ' ':
                        localSpaceCount+=1;
                    else:
                        #logging.debug("end" + i)
                        #logging.debug("count", localTapCount, localSpaceCount)
                        
                        forList =re.findall(r"for.+:",content);
                        logging.debug("for len :" +str(len(forList)))
                        whileList =re.findall(r"while.+:",content);
                        logging.debug("while len :" +str(len(whileList)))
                        ifList =re.findall(r"if.+:",content);
                        logging.debug("if len :" +str(len(ifList)))
                        elifList =re.findall(r"elif.+:",content);
                        logging.debug("elif len :" +str(len(elifList)))
                        elseList =re.findall(r"else:",content);
                        logging.debug("else len :" +str(len(elseList)))
                        passList =re.findall(r"pass",content);
                        logging.debug("pass len :" +str(len(passList)))
                            
                        if not len(elifList)==0: #elif와 if의 중복 검출
                            logging.debug("elif와 if중복 검출로 인한 중s 제거")
                            localLoopCount=(len(forList)+len(whileList)+(len(ifList)-len(elifList))+len(elifList)+len(elseList)-len(passList));
                            pass
                        else:
                            localLoopCount=(len(forList)+len(whileList)+len(ifList)+len(elifList)+len(elseList)-len(passList));
                        
                        count=localTapCount+(math.ceil(localSpaceCount/4))+localLoopCount
                        self.blank=count;
                        logging.debug("count="+str(count))
                        logging.debug(content)
                        for i in range(count-1):
                            space+="\t"
                        logging.debug(" ")
                        break
                            
               
                #데이터베이스 정보 include 해주기!!
                content=content.replace("latteDatabaseExt()","import pylatte.database.DBMappingParser as pyLatteDBMappingParser");
                content=content.replace("latteDatabase()","import pylatte.database.DBMappingParser as pyLatteDBMappingParser;"+" pyLatteDBMappingParser=latteDB=DBMappingParser.pyLatteDBMappingParser(); latteDB=pyLatteDBMappingParser.makeToUseSimpleDB()");
                
                #if(content.find("\n")!=-1):
                # logging.debug(content[:content.find("\n")])

                content="\n"+content  
                content=content.replace("\n",space)
                content+="\n"
                ##logging.debug("@@@\n"+content+"\n@@@")
        else:
            logging.debug("this is not pylcode")
        
        return content
        pass
    
    def processPylOut(self, type,value,lineno,lexpos):
        value=value.replace('{$=', "")
        value=value.replace('$}', "")
        space=""
        for i in range(self.blank):
            space+="\t"
        
        return space+'\t\tself.pylToHtmlResult+=str('+value+')\n'
        pass
    
    def processHTML(self, type,value,lineno,lexpos):
        space=""
        for i in range(self.blank):
            space+="\t"
        
        return space+'\t\tself.pylToHtmlResult+=str("""'+value+'""")\n'
        pass
    
    def processNotPyl(self, type,value,lineno,lexpos):
        if not type=="NOHTML":
            value=value.replace('\"', "&quot;")
        space=""
        for i in range(self.blank):
            space+="\t"
        
        logging.debug("notpyl : "+type+" : "+value)
        return space+'\t\tself.pylToHtmlResult+=str("""'+value+'""")\n'
        pass
    
    
    def outPy(self):
        # .py 로 저장하는데 저장할 때 원본 .pyl 파일명을 따름
        import os
        if os.path.isdir("topy") == False:
            os.mkdir("topy")
        
        with open("topy/"+self.pyl_path.split('.')[0]+"_pyl.py", mode='w', encoding='utf-8') as result_file:
            result_file.write(self.pystring)

