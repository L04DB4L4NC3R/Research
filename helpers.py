from flask import url_for,redirect,session,request,render_template
import csv
import bs4
import urllib.request
import lxml
import re

import csv
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import sys



def bfulSoup(query):    #to return google,youtube and wiki links to given query adn extract top 10 links from wikipedia

    ls,info=[],''

    wiki_url='https://en.wikipedia.org/wiki/' + query

    goog_url='https://www.google.co.in/search?q=' + query

    ytd = 'https://www.youtube.com/results?search_query='+query



    try:
        file= urllib.request.urlopen(wiki_url).read()

        content = bs4.BeautifulSoup( file,'html.parser')
        links=content.find("div",{'id':'bodyContent'}).findAll('a',href=re.compile('(/wiki/)+([A-Za-z0-9_:()])+') )
        info='https://en.wikipedia.org/wiki/' + query



        for link in links:
            dic={}

            dic['info']=info
            dic['title']=link['title']
            dic['href']= 'https://en.wikipedia.org/wiki/' + link['title']
            ls.append(dic)


    except:
        pass



    return [ls,info,ytd,goog_url]
    #ls is list of all key and value pairs for links and titles of the first 10 links extracted from wikipedia
    #info is the particular wikipedia page for the exact query
    #ytd is the youtube link for searching the given query
    #goog_url is the google search results url







def sendmail(email):

    #in gmail settings of your account make sure to 'allow less secure apps' option to be 'ON'

    #to parse csv file

    #to get login credentials
    eid='researchme50@gmail.com'
    epass='researchmecs50'

    #to set up SMTP server and login
    mail=smtplib.SMTP('smtp.gmail.com',587) #to inititalise smtp server and port

    mail.ehlo()                     #for ESMTP encryption

    mail.starttls()                 # transport security layer for encryption


    try:
        mail.login(eid,epass)    #login credentials
    except:
        return 1


    #to set up content of the mail
    msg=MIMEMultipart()

    msg['Subject']="Re-Se@rch Welcomes you"

    body="Extent your search with Re-Se@rch. Make yourself at home"

    msg.attach( MIMEText(body,'plain') )



    #to send mail
    try:
        mail.sendmail('Re-Se@rch',email,msg.as_string() )        #to send a mail
    except:     # to raise an exception when there is failure in mail delivery
        return 2


    mail.close()
    return 0



