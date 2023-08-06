import re, urllib2, urllib
from xml.dom.minidom import parseString

from pastebin_options import OPTION_PASTE, OPTION_LIST, \
OPTION_TRENDS, OPTION_DELETE, \
OPTION_USER_DETAILS

from pastebin_constants import PASTEBIN_API_POST_URL, PASTEBIN_API_LOGIN_URL
from pastebin_exceptions import PastebinBadRequestException, PastebinNoPastesException, \
PastebinFileException

class PastebinPython(object):

	def __init__(self, **kwargs):

		self.api_dev_key = kwargs.get('api_dev_key','')
		self.__api_user_key = ""
		self.__api_user_paste_list = []

	@property
	def api_user_key(self):
		return self.__api_user_key

	@property
	def api_user_paste_list(self):
		return self.__api_user_paste_list

	def createPaste(self, api_paste_code, api_paste_name='', api_paste_format='', api_paste_private='', api_paste_expire_date=''):

		api_user_key = self.api_user_key if self.api_user_key else ""

		postData = {
			'api_option':OPTION_PASTE,
			'api_dev_key':self.api_dev_key
		}

		localVar = locals()

		for k,v in localVar.items():
			if re.search('^api_', k) and v != "":
				postData[k] = v

		return self.__processPost(PASTEBIN_API_POST_URL, postData)

	def createPasteFromFile(self, filename, api_paste_name='', api_paste_format='', api_paste_private='', api_paste_expire_date=''):

		try:
			fileToOpen = open(filename, 'r')
			fileToPaste = fileToOpen.read()
			fileToOpen.close()

			return self.createPaste(fileToPaste, api_paste_name, api_paste_format, api_paste_private, api_paste_expire_date)
		except IOError as e:
			raise PastebinFileException(str(e))


	def __processPost(self, url, data):

		request = urllib2.urlopen(url, urllib.urlencode(data))
		response = str(request.read())
		request.close()

		if re.search('^Bad API request', response):
			raise PastebinBadRequestException(response)
		elif re.search('^No pastes found', response):
			raise PastebinNoPastesException

		return response

	def getUserKey(self, api_user_name, api_user_password):

		postData = {
			'api_dev_key':self.api_dev_key,
			'api_user_name':api_user_name,
			'api_user_password':api_user_password
		}

		self.__api_user_key = self.__processPost(PASTEBIN_API_LOGIN_URL, postData)
		self.__api_user_paste_list = []
		return self.__api_user_key

	def listUserPastes(self, api_results_limit=50):

		postData = {
			'api_dev_key':self.api_dev_key,
			'api_user_key': self.api_user_key,
			'api_results_limit': api_results_limit,
			'api_option':OPTION_LIST
		}

		pastesList = self.__processPost(PASTEBIN_API_POST_URL, postData)
		self.__api_user_paste_list = self.__parseXML(pastesList)
		
		return self.__api_user_paste_list 

	def listTrendingPastes(self):

		postData = {
			'api_dev_key':self.api_dev_key,
			'api_option':OPTION_TRENDS
		}

		trendsList = self.__processPost(PASTEBIN_API_POST_URL, postData)
		trendsList = self.__parseXML(trendsList)

		return trendsList

	def __parseUser(self, xmlString):
		retList = []
		userElements = xmlString.getElementsByTagName('user')

		retList.append({
			'user_name':userElements[0].getElementsByTagName('user_name')[0].childNodes[0].nodeValue,
			'user_format_short':userElements[0].getElementsByTagName('user_format_short')[0].childNodes[0].nodeValue,
			'user_expiration':userElements[0].getElementsByTagName('user_expiration')[0].childNodes[0].nodeValue,
			'user_avatar_url':userElements[0].getElementsByTagName('user_avatar_url')[0].childNodes[0].nodeValue,
			'user_private':userElements[0].getElementsByTagName('user_private')[0].childNodes[0].nodeValue,
			'user_website':userElements[0].getElementsByTagName('user_website')[0].childNodes[0].nodeValue,
			'user_email':userElements[0].getElementsByTagName('user_email')[0].childNodes[0].nodeValue,
			'user_location':userElements[0].getElementsByTagName('user_location')[0].childNodes[0].nodeValue,
			'user_account_type':userElements[0].getElementsByTagName('user_account_type')[0].childNodes[0].nodeValue
		})

		return retList

	def __parsePaste(self, xmlString):
		retList = []
		pasteElements = xmlString.getElementsByTagName('paste')

		for pasteElement in pasteElements:

			try:
				paste_title = pasteElement.getElementsByTagName('paste_title')[0].childNodes[0].nodeValue
			except IndexError:
				paste_title = ""

			retList.append({
				'paste_title':paste_title,
				'paste_key':pasteElement.getElementsByTagName('paste_key')[0].childNodes[0].nodeValue,
				'paste_date':pasteElement.getElementsByTagName('paste_date')[0].childNodes[0].nodeValue,
				'paste_size':pasteElement.getElementsByTagName('paste_size')[0].childNodes[0].nodeValue,
				'paste_expire_date':pasteElement.getElementsByTagName('paste_expire_date')[0].childNodes[0].nodeValue,
				'paste_private':pasteElement.getElementsByTagName('paste_private')[0].childNodes[0].nodeValue,
				'paste_format_long':pasteElement.getElementsByTagName('paste_format_long')[0].childNodes[0].nodeValue,
				'paste_format_short':pasteElement.getElementsByTagName('paste_format_short')[0].childNodes[0].nodeValue,
				'paste_url':pasteElement.getElementsByTagName('paste_url')[0].childNodes[0].nodeValue,
				'paste_hits':pasteElement.getElementsByTagName('paste_hits')[0].childNodes[0].nodeValue,
			})

		return retList


	def __parseXML(self, xml, isPaste=True):
		retList = []
		xmlString = parseString("<pasteBin>%s</pasteBin>" % xml)
		
		if isPaste:
			retList = self.__parsePaste(xmlString)
		else:
			retList = self.__parseUser(xmlString)

		return retList


	def deletePaste(self, api_paste_key):
		postData = {
			'api_dev_key':self.api_dev_key,
			'api_user_key':self.api_user_key,
			'api_paste_key':api_paste_key,
			'api_option':OPTION_DELETE
		}

		try:
			retMsg = self.__processPost(PASTEBIN_API_POST_URL, postData)
		except PastebinBadRequestException as e:
			retMsg = str(e)

		if re.search('^Paste Removed', retMsg):
			return True

		return False


	def getUserInfos(self):
		
		postData = {
			'api_dev_key':self.api_dev_key,
			'api_user_key':self.api_user_key,
			'api_option':OPTION_USER_DETAILS
		}

		retData = self.__processPost(PASTEBIN_API_POST_URL, postData)
		retData = self.__parseXML(retData, False)

		return retData