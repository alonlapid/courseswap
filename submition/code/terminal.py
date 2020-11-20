"""
Terminal for section swapper
"""

from pandas import read_sql
import pyodbc 
from tabulate import tabulate
import sys
from getpass import getpass
import re

#Global connection to the database
_Conn = None

#Display nicly a dataframe
def DisplyTable(df ):
    print(tabulate(df, headers='keys', tablefmt='psql'))

def FormatError(err:str):
    p=re.compile("\(.+\](.+)\(\d.+")
    m=p.match(err)
    if(m is None):
        return err
    else:
        return "Error: " +  m.group(1)
#Help menu
def help_command(argstokens:list):
    if(len(argstokens) > 1 ):
        if(argstokens[1] == "show"):
            help_command_show(argstokens)
            return 
        elif (argstokens[1] == "exe"):
            help_command_exe(argstokens)
            return
        else :
            print("invalid argument to the help command")
            return        
                    
    print("usage: ")
    print("<show|exe|help|exit>  [options] ")
    print("show: presents information relevant to section swap - type 'help show' for more information    ")
    print("exe: performs action - type 'help exe' for more information")
    print("help [command] - shows this help message or help on a specific command")
    print("exit - quit the program")

#Help menu for exe command
def help_command_exe(argstokens:list):     
    print("usage: ")
    print("exe <request|swap|cancell>  [options] ")
    print("exe request <section id to drop > <section id to join>  - request to exchange sections ")
    print("exe cancel - cancel student pending exchange requets  ")
    print("exe swap - swap sections of maching requests (registrar only) ")

#Help menu for show  command
def help_command_show(argstokens:list):          
    print("usage: ")
    print("show <sections|courses|students|requests|enrollments|lessons|credits|prereqs> [filter]")
    print("show sections [filter] - presents the sections available in this symester ")
    print("show courses [filter]- presents the list of courses")
    print("show students [filter] - presents the list of students")
    print("show requests [filter] - presents the pending exchange requests")
    print("show enrollments [filter] - presents the current student enrollments")
    print("show matches [filter] - presents the matching exchange requests")
    print("show lessons [filter] - presents the lessons for a section")
    print("show credits [filter] - presents the courses the student completed")
    print("show prereqs [filter] - presents the prerequisites for each course")
    print("show schedule [filter] - presents the schedule for the current user")
    print("filter is  a condition to filter the result. The syntax of a where clause is supported")
    

#Login to the remote SQL Server
def login(argstokens:list):
    global _Conn      
    server = 'tcp:syncservercs133.database.windows.net' 
    database = 'courseswap' 
    if( _Conn is  None):
        if(len(sys.argv) == 3) :            
            username = sys.argv[1]
            password = sys.argv[2]
            _Conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
        else:
            print("User name:")
            username = input();
            password = getpass();
            _Conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)

#Queue a request for a section swap
def exe_swap_request(argstokens:list):
    global _Conn
    if(len(argstokens) != 4):
         print("invalid arguments to swap request command")
         help_command_exe(argstokens)
         return
    else:
        cursor = _Conn.cursor()
        remove_section = argstokens[2]
        add_section = argstokens[3]
        sqlstmt = "sp_exchange_request_student " + str(remove_section) +"," +  str(add_section)
        cursor.execute(sqlstmt)
        cursor.commit()
        cursor.close()
        
    print("command executed")      

#Cancel all student requests   
def exe_swap_cancel_request(argstokens:list):
    global _Conn
    cursor = _Conn.cursor()
    sqlstmt = "sp_cancel_request_student"
    cursor.execute(sqlstmt)
    cursor.commit()
    cursor.close()
    print("command executed")      

#Execute  a swap request (registrar only)    
def exe_swap(argstokens:list):
    global _Conn
    cursor = _Conn.cursor()
    sqlstmt = "sp_swap"
    cursor.execute(sqlstmt)
    cursor.commit()
    cursor.close()
    print("command executed")      

#Entry point for the exe command    
def execute_command(argstokens:list):
    global _Conn
    if(len(argstokens) < 2) :
        print("invalid exe command")
        help_command_exe(argstokens)
        return
    
    login(argstokens)
    actions =  {"request":exe_swap_request,"swap":exe_swap,"cancel":exe_swap_cancel_request}
    action = argstokens[1]
    if action not in actions.keys():
        print(action + " is not a valid argument to the exe command")
        help_command_exe(argstokens)
        return
    
    #Run the command
    actions[action](argstokens)

def combin_arguments(argstokens:list, fromindex:int):
    ret = "";    
    for i in range(fromindex,len(argstokens)):
        ret = ret + argstokens[i] + " "
    
    
    return ret    

#Entry point for the show command              
def show_command(argstokens:list):
    global _Conn
    if(len(argstokens) < 2) :
        print("invalid show command")
        help_command_show(argstokens)
        return
    
    login(argstokens)
    entities =  {"sections":"fn_section()","courses":"fn_course()","students":"fn_student()","requests":"fn_exchangerequest()","enrollments":"fn_enrollment()","matches":"fn_match()","lessons":"fn_lesson()","credits":"fn_credit()","prereqs":"fn_prerequisite()","schedule":"fn_schedule_student()"}
    entity = argstokens[1]
    if entity not in entities.keys():
        print(entity + " is not a valid argument to the show command")
        help_command_show(argstokens)
        return
    
    #Query the entity and display the result    
    query = "select * from   " +   entities[entity]
    if(len(argstokens) >= 3):
        query = query +" where " + combin_arguments(argstokens,2)
        
                
    df = read_sql(query,_Conn)
    DisplyTable(df)   
     
#Exit    
def exit_command(argstokens:list):
    sys.exit()

commands =  {"help": help_command,"exit":exit_command,"show":show_command,"exe":execute_command  }
print("Wellcome to the section swapper! Please type a command ")  

#Main terminal loop - reading the user commands and executing them    
while(True):    
    print(">>")  
    theinput=input()
    argstokens = theinput.split()
    command = argstokens[0]
    if command not in commands.keys():
        print("invalid command")
        help_command(argstokens)
        continue
        
    handle_command = commands[command];
    try:
        handle_command(argstokens)
    except SystemExit:
       sys.exit("User requsted exit")   
    except pyodbc.ProgrammingError as e:
        print(FormatError(str(e)))
        continue
    except Exception as e:
        print(e)
   
