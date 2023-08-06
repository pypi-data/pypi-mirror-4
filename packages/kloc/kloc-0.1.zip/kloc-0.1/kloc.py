'''a tool count the line of code for C, C++, java...
@auther: zhangzhihong'''



import os,os.path ,fnmatch,shutil



loc={"h":{},"c":{}, "java":{} , "php":{} , "py":{} ,"cpp":{}, "cc":{} ,"jsp":{}, "xml":{},"rb":{},"sh":{}}
comment_single={"h":"//","c":"//", "java":"//" , "php":" ", "py":"#" ,"cpp":"//", "cc":"//","h":"//","jsp":" ","xml":" " ,"rb":"#","sh":"#" }
comment_multi_begin={"h":"/*","c":"/*", "java":"/*" , "php":" ", "cpp":"/*", "cc":"/*" ,"py":" ","h":"/*","jsp":" ","xml":" ","rb":" ","sh":" " }
comment_multi_end={"h":"*/","c":"*/", "java":"*/" , "php":" ","cpp":"*/", "cc":"*/","py":" " ,"cc":"*/", "jsp":" ","xml":" ","rb":" ","sh":" " }
comment_token = False

def init():
    for subfix in loc.keys():
        loc[subfix]["code"]=0
        loc[subfix]["comment"]=0
        loc[subfix]["blank"]=0
        
def is_blank(line):
    if( len(line.strip())==0 ):
        return True
    return False

def is_comment( line, subfix ):
    global comment_token    
    line=line.strip()
    if line.startswith( comment_single[subfix] ) :
        return True
    elif line.startswith( comment_multi_begin[subfix] ) :
        comment_token = True
        return True
    elif ( comment_token == True ):
        if line.endswith(comment_multi_end[subfix]) :
            comment_token = False
        return True
    return False

def dir_tree_print( dir , pattern ):
    for dirpath,dirname,dirfile in os.walk(dir):
        for name in dirfile:
            #print name
            if fnmatch.fnmatch(name,pattern):
                print os.path.join(dirpath,name)
                
'''walk through the directory tree and call fn to every file'''

def dir_tree_file( dir , fn ):
    print dir
    print "----------------------------------------------------------------"
    for dirpath,dirname,dirfile in os.walk(dir):
        for name in dirfile:
            #print name
            fn( os.path.join(dirpath,name) )
    print "----------------------------------------------------------------"
    
'''count the line of codes of the file path'''
def count_file( path ):
    global comment_token 
    subfix=path[path.rfind(".")+1:]
    comment_token = False
    if loc.has_key(subfix):
        code_line=0
        comment_line=0
        blank_line=0
        f=open(path)
        for line in f.readlines():
            if( is_blank(line) ):
                blank_line += 1
            elif ( is_comment(line,subfix) ) :
                comment_line += 1
            else:
                code_line += 1
        f.close()
        loc[subfix]["code"] += code_line
        loc[subfix]["comment"] += comment_line
        loc[subfix]["blank"] += blank_line

def print_sum () :
    sum= {}
    sum["code"]=0
    sum["comment"]=0
    sum["blank"]=0
    print " %16s %16s %16s %16s %16s"  %("language","code","comment","blank","sum")
    for subfix in loc.keys():
        print " %16s %16s %16s %16s %16s"  \
              %( subfix,
                 loc[subfix]["code"],\
                 loc[subfix]["comment"],\
                 loc[subfix]["blank"] , \
                 loc[subfix]["code"]+loc[subfix]["comment"]+loc[subfix]["blank"])
        sum["code"] += loc[subfix]["code"]
        sum["comment"] += loc[subfix]["comment"]
        sum["blank"] += loc[subfix]["blank"]
        
    print " %16s %16s %16s %16s %16s"  \
              %( "summary",
                 sum["code"],\
                 sum["comment"],\
                 sum["blank"] , \
                 sum["code"]+sum["comment"]+sum["blank"])
           
        
                
if __name__=="__main__":
    import sys
    if( len(sys.argv)<2 ):
        print "usage %s dir1 ... dirn"
        sys.exit(-1)
    dirs = sys.argv[1:]
    for directory in dirs:
        init()
        dir_tree_file(directory , count_file)
        print_sum()
    
