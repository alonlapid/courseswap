# -*- coding: utf-8 -*-
"""
Created on Thu Sep  3 13:25:23 2020

@author: alon lapid
"""

from pandas import read_sql
import pyodbc 
from tabulate import tabulate
import sys



conn = pyodbc.connect('Driver={SQL Server Native Client 11.0};'
                      'Server=syncservercs133.database.windows.net;'
                      'Database=courseswap;'
                      'PWD=syncserver20);'
                      'UID=cs133')



def DisplyTable(df ):
    print(tabulate(df, headers='keys', tablefmt='psql'))

def help_command(tokens:list):
    print("usage: ")
    print("<show|exe|help|exit>  [options] ")
    print("show: presents information relevant to section swap - type 'help show' for more information    ")
    print("exe: performs action - type 'help show' for more information")
    print("help [command] - shows this help message or help on a specific command")
    print("exit - quit the program")
    

def help_command_show(argstokens:list):
    print("usage: ")
    print("show <sections|courses|students|requests|enrollments>")
    print("show sections - presents the sections available in this symester ")
    print("show courses - presents the list of courses")
    print("show students - presents the listof students")
    print("show requests - presents the pending exchange requests")
    print("show enrollments - presents the current student enrollments")
    print("show matches - presents the matching exchange requests")

def login_command(argstokens:list):
    print("login_command")
    
def execute_command(argstokens:list):
    print("execute_command")
    
def show_command(argstokens:list):
    if(len(argstokens) < 2) :
        print("invalid show command")
        help_command_show(argstokens)
        return
    
    entities =  {"sections":"fn_section()","courses":"fn_course()","students":"fn_student()","requests":"fn_exchangerequest()","enrollments":"fn_enrollment()","matches":"fn_match()"  }
    entity = argstokens[1]
    if entity not in entities.keys():
        print(entity + " is not a valid argument to the show command")
        help_command_show(argstokens)
        return
        
    query = "select * from   " +   entities[entity]
    df = read_sql(query,conn)
    DisplyTable(df)
   
def exit_command(argstokens:list):
    sys.exit()

commands =  {"help": help_command,"exit":exit_command,"show":show_command,"exe":execute_command  }
print("Wellcome to section swapper! Please type a command ")  
while(True):    
    print(">>")  
    theinput=input()
    argstokens = theinput.split(' ')
    command = argstokens[0]
    if command not in commands.keys():
        print("invalid command")
        help_command(argstokens)
        continue
        
    handle_command = commands[command];
    handle_command(argstokens)

   