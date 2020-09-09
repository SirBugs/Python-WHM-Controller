#!/usr/bin/python
# -*- coding: utf-8 -*-

# ( -- IMPORTS -- ) #
import os
import time
import string
import random
import requests
from colorama import Fore
from colorama import init
init(autoreset=True)
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

RED = Fore.RED
WHITE = Fore.WHITE

# ///////////////////////////////////////////////// #
# ///////////////////////////////////////////////// #
#            Sett WHM Script Definitions            #

def Cookie(IP, user, passwd):
    # // Getting Cpanels Total Count
    global sectoken, STATUS, session
    URL = 'https://{}:2087/'.format(IP)
    data = 'user={}&pass={}&goto_uri=%2F'.format(user, passwd)
    session = requests.Session()
    r = session.post(URL+'/login/?login_only=1', data=data, verify=False)
    src = r.content
    # // print src
    if 'redirect' in src and 'security_token' in src:
        STATUS = 'good'
        sectoken = src.split('"security_token":"')[1].split('"')[0]
        # // print sectoken
    else:
        STATUS = 'bad'
        print '\t{} -| {}Logging To WHM Failed, Please Review Your Data.'.format(WHITE, RED)
        time.sleep(7)
        quit()

def CPCookie(IP, user, passwd):
    # // Getting Cpanels Total Count
    global sectoken, STATUS, session
    URL = 'https://{}:2083/'.format(IP)
    data = 'user={}&pass={}'.format(user, passwd)
    session = requests.Session()
    r = session.post(URL+'/login/?login_only=1', data=data, verify=False)
    src = r.content
    # // print src
    if 'redirect' in src and 'security_token' in src:
        STATUS = 'good'
        sectoken = src.split('"security_token":"')[1].split('"')[0]
        # // print sectoken
    else:
        STATUS = 'bad'
        print '\t{} -| {}Logging To Cpanel Failed, Please Review Your Data.'.format(WHITE, RED)

def Get_CPS(IP, user, passwd):
    # // Getting Cpanels Total Count
    global WHM_Domains
    WHM_Domains = []
    Cookie(IP, user, passwd)
    if STATUS == 'good':
        r = session.get('https://{}:2087/{}/scripts4/listaccts?viewall=1&search=&searchtype=&acctp=30&sortrev=&sortorder=domain'.format(IP, sectoken), verify=False)
        src = r.content
        GG = 0
        try:
            CPs_Count = src.count('suspended=')
            for i in xrange(CPs_Count):
                GG+=1
                TEXT = src.split('user="')[GG].split('" suspended=')[0]
                CP_USER = TEXT.split('"')[0]
                CP_DOMAIN = TEXT.split('domain="')[1].split('"')[0]
                FULL = CP_USER+':'+CP_DOMAIN
                WHM_Domains.append(FULL)
                print '\t{} -| {}Grapped Domain [{}] -> {}{}'.format(RED, WHITE, GG, RED, FULL)
            print '\t{} -| {}Totally Grapped {}{} {}Domains.'.format(WHITE, RED, WHITE, GG, RED)
        except:
            pass
            print '\t{} -| {}Failed Grapping Your Domains, Unknown Error.'.format(WHITE, RED)
    else:
        # // print '\t{} -| {}Failure Status Found, Please Review Your Login Data.'.format(WHITE, RED)
        pass
    
    
    # // Getting Cpanels Domains
    pass

def GEN_USER(size=8, chars=string.digits + string.ascii_lowercase):
    # // GENERATE PASSWORD
    return ''.join(random.choice(chars) for _ in range(size))

def GEN_PASS(size=14, chars=string.ascii_letters + string.ascii_uppercase + string.digits):
    # // GENERATE PASSWORD
    return ''.join(random.choice(chars) for _ in range(size)) + '@' + str(random.randint(1, 999))

# ///////////////////////////////////////////////// #
# ///////////////////////////////////////////////// #
#            Main WHM Script Definitions            #

def Create_Cpanel(Domain, Email, Pack):
    # // Getting Cookie And Tokens
    # // ////////////////////////////
    if STATUS == 'good':
        # // Create Cpanel From WHM
        # // ////////////////////////
        TRIES = 1
        while 1:
            if TRIES != 10:
                CP_USER = GEN_USER()
                CP_PASS = GEN_PASS()
                create_url = 'https://{}:2087/{}/scripts5/wwwacct'.format(Host, sectoken)
                cp_create_data = 'sign=&plan={}&domain={}&username={}&password={}&contactemail={}&dbuser={}&msel=n%2Cy%2C10240%2C%2Cpaper_lantern%2C0%2C0%2C0%2C0%2C0%2C1048576%2Cn%2C0%2C0%2Cdefault%2Cen%2C%2C%2C%2Cn%2C1024%2Caarotfkx_default&cgi=1&language=en&spamassassin=1&hasuseregns=1&mxcheck=local'.format(Pack, Domain, CP_USER, CP_PASS, Email, CP_USER)
                REQ = session.post(create_url, data=cp_create_data, verify=False)
                if 'Account Creation Status: ok (Account Creation Ok)' in REQ.content:
                    print '\t{} -| {}Created Cpanel -> {}https://{}:2083|{}|{} {}#TRY: {}'.format(RED, WHITE, RED, Domain, CP_USER, CP_PASS, WHITE, TRIES)
                    with open('CPS.txt','a+')as f:
                        f.write('https://'+Domain+':2083|'+CP_USER+'|'+CP_PASS+'\n')
                    TRIES = 0
                    break
                else:
                    TRIES+=1
                    # // print '\t{} -| {}Failed Creating Cpanel, Please Review Your Data.'.format(WHITE, RED)
                    pass
            else:
                print '\t{} -| {}Failed Creating Cpanel, Please Review Your Data {}#TRY: {}.'.format(WHITE, RED, WHITE, TRIES)
                TRIES = 0
                break
    else:
        # // print '\t{}-| {}Logging To WHM Failed, Please Review Your Data {}#TRY: {}.'.format(WHITE, RED, WHITE, TRIES)
        pass

def Change_Pass(PASS):
    if STATUS == 'good':
        for DATA in WHM_Domains:
            CP_US, CP_DO = DATA.split(':')
            R = session.get('https://{}:2087/{}/scripts4/listaccts'.format(Host, sectoken), verify=False)
            SRC = R.content
            passwordtoken = SRC.split("name=passwordtoken value='")[1].split("'")[0]
            data = 'password={}&user={}&passwordtoken={}&enablemysql=1'.format(PASS, CP_US, passwordtoken)
            r = session.post('https://{}:2087/{}/scripts/passwd'.format(Host, sectoken), data=data, verify=False)
            # // print r.content
            print '\n'
            if 'has been changed' in r.content:
                print '\t{} -| {}Password For {}{} {}Has Been Changed To : {}{}'.format(RED, WHITE, RED, DATA, WHITE, RED, PASS)
                file = open('Changed_Cpanels.txt', 'a+')
                file.write('https://{}:2083|{}|{}\n'.format(CP_DO, CP_US, PASS))
                file.close()
            else:
                print '\t{} -| {}Failed Changing Password For {}{}'.format(WHITE, RED, WHITE, DATA)
    else:
        # // print '\t{} -| {}Failure Status Found, Please Review Your Login Data.'.format(WHITE, RED)
        pass

def Change_CP_Pass(Host, OLD_PASS, NEW_PASS):
    if STATUS == 'good':
        data = 'oldpass={}&newpass={}&newpass2={}&enablemysql=1&B1=Change+your+password+now%21'.format(OLD_PASS, NEW_PASS, NEW_PASS)
        r = session.post('https://{}:2083/{}/frontend/paper_lantern/passwd/changepass.html'.format(Host, sectoken), data=data, verify=False)
        # // print r.content
        print '\n'
        if 'Success! The browser is now redirecting' in r.content:
            print '\t{} -| {}Password For {}{} {}Has Been Changed To : {}{}'.format(RED, WHITE, RED, Host, WHITE, RED, PASS)
            file = open('Changed_Cpanels_CPS.txt', 'a+')
            file.write('https://{}:2083|{}|{}\n'.format(Host, User, NEW_PASS))
            file.close()
        else:
            print '\t{} -| {}Failed Changing Password For {}{}'.format(WHITE, RED, WHITE, Host)
    else:
        # // print '\t{} -| {}Failure Status Found, Please Review Your Login Data.'.format(WHITE, RED)
        pass

# ///////////////////////////////////////////////// ## ///////////////////////////////////////////////// #

os.system('cls')

print '{}  ____  _    _  _____  _____  __          ___    _ __  __ '.format(RED); time.sleep(0.1)
print '{} |  _ \| |  | |/ ____|/ ____| \ \        / / |  | |  \/  |'.format(WHITE); time.sleep(0.1)
print '{} | |_) | |  | | |  __| (___    \ \  /\  / /| |__| | \  / |'.format(RED); time.sleep(0.1)
print '{} |  _ <| |  | | | |_ |\___ \    \ \/  \/ / |  __  | |\/| |'.format(WHITE); time.sleep(0.1)
print '{} | |_) | |__| | |__| |____) |    \  /\  /  | |  | | |  | |'.format(RED); time.sleep(0.1)
print '{} |____/ \____/ \_____|_____/      \/  \/   |_|  |_|_|  |_|\n'.format(WHITE); time.sleep(0.1)
print '{} -| {}Bugs {}New {}WHM Manager {}v2.0 {}@2020{}.'.format(WHITE, RED, WHITE, RED, RED, WHITE, RED, WHITE); time.sleep(0.1)
print '{} -| {}Made {}With {}Love For {}Xleet{} & {}Olux {}Sellers.\n'.format(WHITE, RED, WHITE, RED, WHITE, RED, WHITE, RED); time.sleep(0.1)

print '{} -| {}1{} | {}Create New Cpanels{}.'.format(RED, WHITE, RED, WHITE, RED); time.sleep(0.1)
print '{} -| {}2{} | {}Change All Cpanels Password [WHM]{}.'.format(RED, WHITE, RED, WHITE, RED); time.sleep(0.1)
print '{} -| {}3{} | {}Change CPanels Password [CPS]{}.'.format(RED, WHITE, RED, WHITE, RED); time.sleep(0.1)

print ' {}---{}---{}---{}---{}---{}---{}---{}---{}---{}---{}---{}---{}---{}---{}---{}---{}---{}---{}---\n'.format(RED, WHITE, RED, WHITE, RED, WHITE, RED, WHITE, RED, WHITE, RED,RED, WHITE, RED, WHITE, RED, WHITE, RED, WHITE); time.sleep(0.1)

# ///////////////////////////////////////////////// ## ///////////////////////////////////////////////// #

ask = raw_input('\t{} -| {}Choose A Tool {}: '.format(WHITE, RED, WHITE))

try:
    ask = int(ask)
except:
    print '\n\t{} -| {}Please Choose Valid Tool And Try Again{}.'.format(WHITE, RED, WHITE)
    time.sleep(7)
    quit()

if ask == 1:
    # // Create Cpanel
    Host = raw_input(' \t\t{}-| {}Enter Your Host         {}: '.format(RED, WHITE, RED))
    Log = raw_input(' \t\t{}-| {}Enter Your Log          {}: '.format(RED, WHITE, RED))
    Password = raw_input(' \t\t{}-| {}Enter Your Password     {}: '.format(RED, WHITE, RED))
    Email = raw_input(' \t\t{}-| {}Enter Your Email        {}: '.format(RED, WHITE, RED))
    Package = raw_input(' \t\t{}-| {}Enter Your Package      {}: '.format(RED, WHITE, RED))
    Domains_List = raw_input(' \t\t{}-| {}Enter Your Domains List {}: '.format(RED, WHITE, RED))
    Cookie(Host, Log, Password)
    print '\n'
    fi = open(Domains_List, 'r')
    try:
        for i in fi:
            Domain = i.strip()
            Create_Cpanel(Domain, Email, Package)
    except:
        print '\n\t{} -| {}Please Provide Valid Data Or File To Open{}.'.format(WHITE, RED, WHITE)
        time.sleep(7)
        quit()
elif ask == 2:
    # // Changing All Passwords
    Host = raw_input(' \t\t{}-| {}Enter Your Host          {}: '.format(RED, WHITE, RED))
    Log = raw_input(' \t\t{}-| {}Enter Your Log           {}: '.format(RED, WHITE, RED))
    Password = raw_input(' \t\t{}-| {}Enter Your Password      {}: '.format(RED, WHITE, RED))
    PASS = raw_input(' \t\t{}-| {}Enter Password To Change {}: '.format(RED, WHITE, RED))
    PASS = PASS + '@' + str(random.randint(1, 999))
    Get_CPS(Host, Log, Password)
    try:
        Change_Pass(PASS)
    except:
        print '\n\t{} -| {}UnExpected Error! Failed To Change Password{}.'.format(WHITE, RED, WHITE)
    else:
        print '\n\t{} -| {}Please Choose Valid Tool And Try Again{}.'.format(WHITE, RED, WHITE)
        time.sleep(7)
        quit()
elif ask == 3:
    # // Changing All Passwords
    Cpanels = raw_input(' \t\t{}-| {}Enter Your Cpanels File {}: '.format(RED, WHITE, RED))
    PASS = raw_input(' \t\t{}-| {}Enter Password To Change {}: '.format(RED, WHITE, RED))
    try:
        fi = open(Cpanels, 'r')
        for i in fi:
            PASS = PASS + '@' + str(random.randint(1, 999))
            Line = i.strip()
            Url, User, Pass = Line.split('|')
            Domain = Url.split('https://')[1].split(':')[0]
            CPCookie(Domain, User, Pass)
            Change_CP_Pass(Domain, Pass, PASS)
    except:
        print '\n\t{} -| {}Please Provide Valid Data Or File To Open{}.'.format(WHITE, RED, WHITE)
        time.sleep(7)
        quit()
        
# ///////////////////////////////////////////////// ## ///////////////////////////////////////////////// #
