#!/usr/bin/env python 
# -- coding: utf-8 --

import mechanize
from BeautifulSoup import BeautifulSoup, NavigableString
from sys import exit
from email.mime.text import MIMEText
import time
import datetime
import getpass 
from colorama import Fore



WEB_BASE = "http://www.cambiatuscromos.org/"
WEB_INTERCAMBIO = "http://www.cambiatuscromos.org/intercambios/"
HEADER = 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1'
USER_AGENT = 'User-agent'
WEB_USER = ""
WEB_PASS = ""



def getDivContent():
	a = mechanize.Browser()
	a.open(WEB_BASE)
	a.select_form(nr = 2)  
	a["user"] = WEB_USER
	a["pass"] = WEB_PASS
	a.addheaders = [(USER_AGENT, HEADER )]
	a.submit()

	a.open(WEB_INTERCAMBIO)

	soup = BeautifulSoup(a.response().read())
	content = soup.find('div', attrs={'class': 'scroll_box'})

	return content


def run():

	WEB_USER = raw_input("Usuario de cambiatuscromos: ")
	WEB_PASS = getpass.getpass("Password de cambiatuscromos: ") 

	content1 = getDivContent()

	if content1 == "":
		print "Ha ocurrido un error al conectar con la web. Revise usuario y password."
		exit()

	time.sleep( 5 )

	while True:
		content2 = getDivContent()

		if content2 == "":
			print "Ha ocurrido un error al conectar con la web. Revise usuario y password."
			exit()

		if content1 == content2:
			now = datetime.datetime.now()
			print Fore.RED + now.strftime("%Y-%m-%d %H:%M") + " ||| No hay novedades." + Fore.RESET
			content2 = ""
			time.sleep( 3600 )
		else:
			now = datetime.datetime.now()
			print Fore.GREEN + now.strftime("%Y-%m-%d %H:%M") + " ||| Tienes intercambios pendientes !!!!" + Fore.RESET
			exit()
		