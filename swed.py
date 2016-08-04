from time import strftime, sleep, strptime
from random import gauss
# from swed_cookiehant import Cookiehanterare
from bs4 import BeautifulSoup
from collections import OrderedDict
import requests
import pickle
from string import capwords
import decimal


#Behöver göra felhantering för om felaktiga uppgifter matas in av användaren
global errorSoup



class Swed:
	
	#ch = None
	soup = None
	txheaders = {'User-agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1'}
	response = None
	session = None
	logFile = 'transationer.pickle'
	log = None
	
	def __init__(self):
		self.session = requests.Session()
		self.session.headers.update(self.txheaders)
		with open(self.logFile,'rb') as f:
			self.log = pickle.load(f)
	
	def login_and_fetch(self):
		self.login()
		self.chose_profile()
		self.chose_account()
		sleep(gauss(0.55,0.1))
		self.fetch_logs()
	
	def pre_login_attempt(self):
		theurl = u'https://internetbank.swedbank.se/bviPrivat/privat?ns=1'
		self.response = self.session.get(theurl)
		
	def login_attempt_authId(self,authid):
		theurl = u'https://internetbank.swedbank.se/idp/portal'
		post_data = {'authid':authid}
		self.response = self.session.post(theurl,data=post_data)
			
	def login_attempt_browserInfo(self):
		theurl = u'https://internetbank.swedbank.se/idp/portal/identifieringidp/idp/dap1/ver=2.0/action/rparam=execution=e1s1'
		post_data = {'execution':'e1s1','dapPortalWindowId':'dap1','locale':'sv_SE','IntId':'dap1','authid':'','form1:customer_plugin_java':'1,8,0,71','form1:customer_plugin_flash':'','form1:customer_plugin_adobe_reader':'15,17,20050,61080','form1:fortsett_knapp':'klicka','form1_SUBMIT':'1','javax.faces.ViewState':'rO0ABXVyABNbTGphdmEubGFuZy5PYmplY3Q7kM5YnxBzKWwCAAB4cAAAAAN0AAExcHQAIi9XRUItSU5GL2Zsb3dzL2lkcC9wcmV1c2VyaWQueGh0bWw='}
		self.response = self.session.post(theurl,data=post_data)

	def auth_first_step(self, personnummer):
		theurl = 'https://internetbank.swedbank.se/idp/portal/identifieringidp/idp/dap1/ver=2.0/rparam=execution=e1s2'
		post_data = {'execution':'e1s2','auth:kundnummer':'199103242435','auth:metod_2':'ACTCARD','auth:efield':'1','auth:fortsett_knapp':'Fortsätt','auth_SUBMIT':'1','javax.faces.ViewState':'rO0ABXVyABNbTGphdmEubGFuZy5PYmplY3Q7kM5YnxBzKWwCAAB4cAAAAAN0AAEycHQAJy9XRUItSU5GL2Zsb3dzL2lkcC91c2VyaWRfRGVmYXVsdC54aHRtbA=='}
		self.response = self.session.post(theurl,data=post_data)
			
	def auth_second_step(self, engangskod):
		theurl = 'https://internetbank.swedbank.se/idp/portal/identifieringidp/idp/dap1/ver=2.0/rparam=execution=e1s3'
		post_data = {'execution':'e1s3','form:challengeResponse':engangskod,'form:locTime':strftime('%Y%m%d%H%M%S'),'form:rendering':'152','form:efield':'1','form:fortsett_knapp':'Fortsätt','form_SUBMIT':'1','javax.faces.ViewState':'rO0ABXVyABNbTGphdmEubGFuZy5PYmplY3Q7kM5YnxBzKWwCAAB4cAAAAAN0AAEzcHQAJy9XRUItSU5GL2Zsb3dzL2FjdGNhcmQvYWN0Y2FyZE9UUC54aHRtbA=='}
		self.response = self.session.post(theurl,data=post_data)
	
	def find_authid(self):
		interRes = self.response.text
		interRes = interRes[interRes.find('authid'):]
		interRes = interRes[interRes.find('value')+7:]
		interRes = interRes[:interRes.find(u'"')]
		authid   = interRes.encode()
		return authid
		
	def auth_fourth_step(self,authid):
		theurl = 'https://internetbank.swedbank.se/bviPrivat/privat?_new_flow_=false'
		post_data = {'dapPortalWindowId':'dap1','locale':'sv_SE','IntId':'dap1','authid':authid}
		self.response = self.session.post(theurl,data=post_data)
	
	def login(self):
		self.pre_login_attempt()
		# print()
		# print()
		# print(authid)
		authid1 = self.find_authid()
		# print()
		print(authid1)
		# print()
		self.login_attempt_authId(authid1)
		# time.sleep(1)
		self.login_attempt_browserInfo()
		# time.sleep(2)
		# print(self.response.text)_
		personnummer = input('Skriv in ditt personnummer (ååååmmddxxxx):')
		self.auth_first_step(personnummer)
		# print(self.response.text)
		engangskod = input(u'Skriv in din engångskod från dosan:')
		# time.sleep(0.5)
		self.auth_second_step(engangskod)
		# print(self.response.text)
		# time.sleep(1)
		# print(authid1)
		# authid = self.response.text
		# print()
		# print(authid)
		# print()
		# authid = authid[authid.find('authid'):]
		# authid2 = authid[authid.find('value')+7:authid.find('"')]
		authid2 = self.find_authid()
		# print(authid2)
		self.auth_fourth_step(authid2)
		self.soup = BeautifulSoup(self.response.text, 'html.parser')

	def chose_profile(self):
		profiles = []
		for rawProfile in self.soup.select(".tabell-cell-topp-botten > a"):
			profile = {'name':rawProfile.get_text(),'link':rawProfile.get('href')}
			profiles.append(profile)
			
		print("Möjliga profiler att välja mellan")
		print("Nr.\tNamn")
		for i in range(len(profiles)):
			print(str(i) + '\t' + profiles[i]['name'])
			
		profile_nbr = int(input("Skriv numret på profilen du vill använda: "))
		link = profiles[profile_nbr]['link']
		self.response = self.session.get(link)
		
		self.soup = BeautifulSoup(self.response.text, 'html.parser')
		
	def chose_account(self):
		accounts = []
		for rawAccount in self.soup.select(".tabell a"):
			if rawAccount.get('title') == 'Till sidan med kontohistorik.':
				profile = {'name':rawAccount.get_text(),'link':rawAccount.get('href')}
				accounts.append(profile)
		
		if len(accounts) > 0:
			print("Möjliga konton att välja mellan")
			print("Nr.\tNamn")		
			for i in range(len(accounts)):
				print(str(i) + '\t' + accounts[i]['name'])
					
			account_nbr = int(input("Skriv numret på kontot du vill använda: "))
			
			link = 'https://internetbank.swedbank.se/bviforetagplus/PortalBvIForetagPlus' + accounts[account_nbr]['link']
			self.response = self.session.get(link)
			self.soup = BeautifulSoup(self.response.text, 'html.parser')
		else:
			print()
			print("ERROR, Inget konto har hittats")
			print("Listan med möliga konton:")
			print(self.soup.select(".tabell a"))
		
	def fetch_logs(self):
		"""Hämtar alla transaktioner, bör ändras så att
		datum kan användas för att begränsa hämtningen"""
		transactionLinks = self.soup.select(".tabell-cell-topp > a, .tabell-cell > a, .tabell-cell-botten > a")
		transactions = []
		nav = self.soup.select(".tabell-fot a")
		next = None
		linkbase = u'https://internetbank.swedbank.se/bviforetagplus/PortalBvIForetagPlus'
		for link in nav:
			if link.get_text() == 'Nästa':
				next = link.get('href')
		sleep(gauss(0.55,0.1))
		while True:
			transaction = {}
			for link in transactionLinks:
				# print('Follow link to transaction')
				tranRes = self.session.get(linkbase + link.get('href'),headers = self.txheaders)
				try:
					transaction = self.fetch_log(link.get_text(), tranRes.text)
				except IndexError as e:
					print(e)
					print('tranRes.status_code: ' + str(tranRes.status_code))
					#print(tranRes.text)
					
				sleep(gauss(0.55,0.1))
				if transaction == {}:
					print()
					print('Beskrivning: ' + link.get_text())
					print()
					print('Return soup')
					#return BeautifulSoup(tranRes.text, 'html.parser')
					break
				else:
					print('Transaktion inlagd ' + str(transaction))
					transactions.append(transaction)
			
			if transaction == {}:
				break	
			if next == None:
				break
			self.response = self.session.get(linkbase + next)
			self.soup = BeautifulSoup(self.response.text, 'html.parser')
			transactionLinks = self.soup.select(".tabell-cell-topp > a, .tabell-cell > a, .tabell-cell-botten > a")
			nav = self.soup.select(".tabell-fot a")
			next = None
			for link in nav:
				if link.get_text() == 'Nästa':
					next = link.get('href')
		self.log = transactions
		return transactions
		
	def fetch_log(self,beskrivning,logHtml):
		transaction = {}
		soup = BeautifulSoup(logHtml, 'html.parser')
		if beskrivning == 'Bankgiro inbetalning':
			return self.fetch_bg(soup)
		elif beskrivning[0:7] == 'swish +':
			try:
				return self.fetch_swish(soup)
			except requests.exceptions.ConnectionError:
				sleep(gauss(0.85,0.1))
				return self.fetch_swish(soup)
		else:
			return self.fetch_normal(soup)
	
	def fetch_swish(self, soup):
		# print()
		# print('fetch_swish: ')
		htmlString = str(soup)
		#print('1 ' + htmlString)
		htmlString = htmlString[htmlString.find('location.replace('):]
		#print('2 ' + htmlString)
		htmlString = htmlString[htmlString.find('"')+1:]
		#print('3 ' + htmlString)
		htmlString = htmlString[:htmlString.find('"')]
		link = u'https://internetbank.swedbank.se' + htmlString
		# print('First link ' + str(link))
		# print()
		response = self.session.get(link)
		sleep(gauss(0.35,0.1))
		soup = BeautifulSoup(response.text, 'html.parser')
		
		if soup.form.get('name') == 'redirectForm':
			# print(soup)
			# print()
			# First step complete now to the post request from form
			post_data = {}
			for input in soup.select('input'):
				if input.get('value') == 'Återbetalning':
					raise Exception('Alvarligt fel ska inte skicka återbetalning')
				post_data[input.get('name')] = input.get('value')
			link = u'https://internetbank.swedbank.se' + soup.form.get('action')
			# print()
			# print()
			print('Second link ' + str(link))
			print(post_data)
			# print()
			response = self.session.post(link, data = post_data)
			soup = BeautifulSoup(response.text, 'html.parser')
			
			
			# print(soup)
			sleep(gauss(0.55,0.1))
			# Step three
			# global errorSoup
			# errorSoup = soup
			# raise NotImplementedError('Swish - Denna transkationstyp är inte implementerad soup in global errorSoup')
			
			if soup.form.get('name') == 'redirectForm':
				post_data = {}
				for input in soup.select('input'):
					if input.get('value') == 'Återbetalning':
						raise Exception('Alvarligt fel ska inte skicka återbetalning')
					post_data[input.get('name')] = input.get('value')
				print()
				
				# print()
				link = u'https://internetbank.swedbank.se' + soup.form.get('action')
				print('Third link ' + str(link))
				print()
				print('post_data: ' +str(post_data))
				print()
				
				response = self.session.post(link, data = post_data)
				

				soup = BeautifulSoup(response.text, 'html.parser')
				print(soup)
				print()
				print()
		
		# global errorSoup
		# errorSoup = soup
		# raise NotImplementedError('Swish - Denna transkationstyp är inte implementerad soup in global errorSoup')
		
		transaction = {}
		data = soup.select("dl")[4:]
		for post in data:
			transaction[post.get_text().split('\n')[0]] = post.get_text().split('\n')[1]
		
		return transaction

	def fetch_bg(self,soup):
		transaction = {}
		data = soup.select(".felt-uppstellning > tr > td")
		for i in range(10,28,2):
			try:
				transaction[data[i].get_text().strip('\n\t ')] = data[i+1].get_text().strip('\n\t ')
			except IndexError:
				global errorSoup
				errorSoup = soup
				raise Exception('Något gick fel soup i errorSoup')
		linkbase = u'https://internetbank.swedbank.se/bviforetagplus/PortalBvIForetagPlus'
		linktoBGdetails = linkbase + soup.select("form")[0].get('action')
		transaction['bgDetail'] = self._fetch_bg_detail(linktoBGdetails,transaction)
		return transaction

	def fetch_normal(self, soup):
		transaction = {}
		data = soup.select(".felt-uppstellning > tr > td")
		for i in range(10,28,2):
			transaction[data[i].get_text().strip('\n\t ')] = data[i+1].get_text().strip('\n\t ')
		return transaction
	
	def _fetch_bg_detail(self, url, transaction):
		sleep(gauss(0.15,0.02))
		bgDetails = []
		# post_data = OrderedDict([('bankgironummer',transaction['Referens']),('valuta','SEK'),('datumTransdag',transaction['Transaktionsdatum'])])
		post_data = {'bankgironummer': transaction['Referens'],'valuta':'SEK','datumTransdag':transaction['Transaktionsdatum']}
		res = self.session.post(url,data = post_data, allow_redirects = True)
		soup = BeautifulSoup(res.text, 'html.parser')
		print(res.status_code)
		print(res.history)
		print(url)
		print('post_data: ')
		print(post_data)
		global errorSoup
		errorSoup = soup
		raise NotImplementedError('Denna transkationstyp är inte implementerad soup in global errorSoup')
		for bgDetailLink in soup.select():
			pass
		
	def upgrade_from_old(self, old):
		"""Finns för att man ska kunna uppgradera koden
		efter att modulen laddats om kan denna köras för
		det nya Swed-objektet så att det för det tidigares
		session och variabler"""
		self.soup = old.soup
		self.response = old.response
		self.session = old.session
		self.log = old.log
		return self
		
	def save_log(self):
		with open(self.logFile,'wb') as f:
			pickle.dump(self.log,f)
			
	def print_log(self, filename,fromyyyymmdd):
		infilename = filename + '-intäkter.csv'
		utfilename = filename + '-utgifter.csv'
		inString = ''
		utString = ''
		seperator = ';'
		fromdate = strptime(fromyyyymmdd,'%Y%m%d')
		printLog = [post for post in self.log[::-1] if strptime(post['Bokföringsdatum'], '%Y-%m-%d') > fromdate] 
		
		for i in range(len(printLog)):
			logPost = printLog[i]
			if logPost['Transaktionstyp'] == 'Insättning':
				"Beskrivning Intäkt"
				inString += logPost['Meddelande'] + seperator
				
				"Medlem"
				if logPost['Beskrivning'] == 'Insättning':
					inString += seperator
				elif logPost['Beskrivning'] == 'Swish':
					inString += formatName(logPost['Från']) + seperator
				elif logPost['Beskrivning'] == 'Överföring via internet':
					inString += seperator
				else:
					print(logPost)
					raise NotImplementedError('Inte implementerad')
					
				"Budgetpost"
				inString += seperator
				
				"Bokföringsdatum"
				inString += logPost['Bokföringsdatum'] + seperator
				
				"Summa"
				inString += logPost['Belopp'].replace(' ','').replace(',','.') + seperator
				
				"Bokfört saldo"
				inString += seperator
				
				"nr."
				inString += str(i+1) # + seperator
				
				"Kommentar"
				# inString += str(logPost)
				
				inString += '\n'
				
			elif logPost['Transaktionstyp'] == 'Uttag':
				"Beskrivning Utgifter"
				utString += logPost['Meddelande'] + seperator
				
				"Budgetpost"
				utString += seperator
				"Bokföringsdatum"
				utString += logPost['Bokföringsdatum'] + seperator
				"Summa"
				utString += str(-decimal.Decimal(logPost['Belopp'].replace(' ','').replace(',','.'))) + seperator
				"Bokfört saldo"
				utString += seperator
				"nr."
				utString += str(i+1) + seperator
				"Budgetpost"
				#utString += seperator
				"Kommentar"
				#utString += str(logPost)
				utString += '\n'

			else:
				print(logPost)
				raise Exception('Ska inte kunna komma hit')
		with open(infilename,'w') as f:
			f.write(inString)
		with open(utfilename,'w') as f:
			f.write(utString)
			
def formatName(nameString):
	if len(nameString.split(',')) == 2:
		splitName = nameString.split(',')
		newNameString = splitName[1].replace(' ','') + ' ' + splitName[0]
	else:
		newNameString = nameString
	return capwords(newNameString)
	
		