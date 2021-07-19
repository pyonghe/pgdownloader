'''
@author : Pang Yong He
@purpose : To download guides from Proving Grounds
@todo : keep track of a list of machine and update if there is new machine to download
@Created on : June 2021
'''
'''
v0.2 : Update July 2021
Added feature to keep track of current guides using a config file on disk
Added feature to only download guides that are missing currently
Added feature to show what are the files that are new

'''



import sys, requests, re, os
import httpx
import pdfkit
from tqdm import tqdm
from os.path import exists

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
	
def checkForNewUpdates(currGuideCount):
	print("(+) Checking for updates ...")
	# Check if there is config file
	if (exists("config.txt")):
		# If yes then i will read the first line of the file and convert to integer.
		with open("config.txt") as f:
			count = int(f.readline().strip())
			f.close()
			if (currGuideCount > count):
				#return true and update file
				f = open("config.txt", "w")
				f.write(str(currGuideCount))
				f.close()
				return True;
			elif (currGuideCount == count):
				#guide are updated do not need to download
				return False;
	else:
		# Create a new file and add the currGuideCount
		with open("config.txt", 'w') as f:
			f.write(str(currGuideCount))
			f.close()
		return True;

def currGuidesName():
	# check current guide names store in array
	# return the array and check if the machine name is in the array
	# if yes do not download, else download
	files = os.listdir(".")
	filelist = list()
	for f in files: 
		if ((f != "pgdownloader.py") or ( f!="config.txt")):
			filelist.append(f.replace(".pdf",""))

	return filelist

def download(url, session):
	
	dlist = list()
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
	
	# len(x) -1 because the first element in x is ['<i class="mdi mdi-desktop-classic"> which is not what we want
	if(checkForNewUpdates(len(x)-1)):
		
		filelist = currGuidesName()
		
		for i in range(1, len(x)):
			machinename = x[i].split(",")[0].split("\\n")[1].strip(' \']')
			if(machinename not in filelist):
				dlist.append(machinename)
				#pdfkit.from_url(url + machinename + "/", machinename +'.pdf', options=options)
		if len(dlist) > 0: 
			print("(+) Updates available")
			print("(+) Downloading guides and saving them as PDFs")
			for i in tqdm(range(0,len(dlist))):
				pdfkit.from_url(url + dlist[i] + "/", dlist[i] +'.pdf', options=options)

			print("(+) Download Completed")
			print("(+) Newly added machine :")
			for dfile in dlist:
				print(dfile)
		else:
			print("(+) Guides are up to date!")

		session.close()
		

	else:
		session.close()
		print("(+) Guides are up to date!")

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
	
