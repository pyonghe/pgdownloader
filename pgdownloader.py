'''
@author : Pang Yong He
@purpose : To download guides from Proving Grounds
@todo : keep track of a list of machine and update if there is new machine to download
@Created on : June 2021
'''


import sys, requests, re
import httpx
import pdfkit
from tqdm import tqdm

def login(url, username, password):
	
	#proxies = {'https://' : 'http://127.0.0.1:8080'}
	s = httpx.Client(verify=False,http2=True)
	r = s.get(url + "accounts/login/")
	res = r.text
	x = str(re.findall("csrfmiddlewaretoken\".*=.*", res)).split("=")[1].split("\"")[1]
	headers = {
	'Referer' :  'https://cp.megacorpone.net/accounts/login/'
	}
	data = {
	'csrfmiddlewaretoken': x,
	'username' : username,
	'password' : password,
	'next' : ""
	 }
	 
	result = s.post(url + "accounts/login/", data=data,headers=headers)
	if 'try again' in result.text:
		print("(+) Wrong password! Please enter the correct password")
		sys.exit(0)
	else: 
		print("(+) Login Success!")
		return s
	
def download(url, session):
	print("(+) Downloading guides and saving them as PDFs")
	url = url + "guides/"
	r = session.get(url)
	x = str(re.findall("<i class=\"mdi mdi-desktop-classic\"></i>\n.*", r.text)).split("</i>")
	
	options = {
			'background': None,
			'quiet' : None,
			'cookie' : [
			('csrftoken', session.cookies['csrftoken']),
			('sessionid', session.cookies['sessionid'])
			]}
	machinename = ""
	
	for i in tqdm(range(1, len(x))):
		machinename = x[i].split(",")[0].split("\\n")[1].strip(' \']')
		pdfkit.from_url(url + machinename + "/", machinename +'.pdf', options=options)
	session.close()
	print("(+) Download Completed")
	
def main():
	if len(sys.argv) != 3:
		print ("(+) usage: %s <username> <password>" % sys.argv[0])
		print ("(+) eg: %s username password" %sys.argv[0])
		sys.exit(-1)
	
	url = "https://cp.megacorpone.net/"
	username = sys.argv[1]
	password = sys.argv[2]
	
	s = login(url, username, password)
	download(url, s)
	
if __name__ == "__main__":
	main()
	
