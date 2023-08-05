#
# placefinder-py
# version 0.3
# 10/26/2012
# Adam Presley (adam@adampresley.com)
#
# History:
#    11/07/2012
#       - Added function to reverse-geocode latitude/longitude
#       - Changed unit tests to be able to be run by nose
#       - Incremented version to 0.3
#
#    10/26/2012
#       - Initial release of basic geocoding methods
#
import oauth2 as oauth
import time, json
import urllib

RESULT_FORMAT_JSON = "J"
RESULT_FORMAT_XML = ""

class InvalidSearchQueryException(Exception):
	pass


class PlaceFinder():
	_key = None
	_secret = None
	_appId = None
	_resultFormat = None
	_locale = None

	_baseUrl = "http://where.yahooapis.com/geocode?"
	_signatureMethod = oauth.SignatureMethod_HMAC_SHA1()
	_lastResponse = None

	_qualityMapping = {
		"99": "Coordinate",
		"90": "POI",
		"87": "Address match with street match",
		"86": "Address mismatch with street match",
		"85": "Address match with street mismatch",
		"84": "Address mismatch with street mismatch",
		"82": "Intersection with street match",
		"80": "Intersection with street mismatch",
		"75": "Postal unit/segment (Zip+4 in US)",
		"74": "Postal unit/segment, street ignored (Zip+4 in US)",
		"72": "Street match",
		"71": "Street match, address ignored",
		"70": "Street mismatch",
		"64": "Postal zone/sector, street ignored (Zip+2 in US)",
		"63": "AOI",
		"62": "Airport",
		"60": "Postal district (Zip Code in US)",
		"59": "Postal district, street ignored (Zip Code in US)",
		"50": "Level4 (Neighborhood)",
		"49": "Level4, street ignored (Neighborhood)",
		"40": "Level3 (City/Town/Locality)",
		"39": "Level3, level4 ignored (City/Town/Locality)",
		"30": "Level2 (County)",
		"29": "Level2, level3 ignored (County)",
		"20": "Level1 (State/Province)",
		"19": "Level1, level2 ignored (State/Province)",
		"10": "Level0 (Country)",
		"9": "Level0, level1 ignored (Country)",
		"0": "Not an address"
	}


	def __init__(self, key, secret, appId, resultFormat = RESULT_FORMAT_JSON, locale = "en_US"):
		self._key = key
		self._secret = secret
		self._appId = appId
		self._resultFormat = resultFormat
		self._locale = locale

	############################################################################
	# Section: Public methods
	############################################################################

	def geocode(self, flags = "", gflags = "", **kwargs):
		flags = flags + self._resultFormat

		if not self._validateQuery(**kwargs):
			raise InvalidSearchQueryException("Invalid search query")

		consumer = self._getConsumer()
		client = self._getClient(consumer)
		self._signRequest(self._buildUrl(flags, gflags, **kwargs), self._buildOAuthParams(flags, gflags, **kwargs), consumer)

		response, content = client.request(self._buildUrl(flags, gflags, **kwargs), "GET")
		
		self._lastResponse = response
		content = json.loads(content)
		results = [] if "Results" not in content["ResultSet"] else content["ResultSet"]["Results"]

		return response, content, results

	def geocodeAirportCode(self, airportCode, flags = "", gflags = "", **kwargs):
		kwargs["q"] = airportCode
		return self.geocode(flags, gflags, **kwargs)

	def geocodeFreeform(self, query, flags = "", gflags = "", **kwargs):
		kwargs["q"] = query
		return self.geocode(flags, gflags, **kwargs)

	def geocodeMultiline(self, address, city, state, zip, line3 = "", flags = "", gflags = "", **kwargs):
		kwargs["line1"] = address
		kwargs["line2"] = "%s, %s %s" % (city, state, zip)

		if line3:
			kwargs["line3"] = line3

		return self.geocode(flags, gflags, **kwargs)

	def geocodePOI(self, poi, flags = "", gflags = "", **kwargs):
		kwargs["q"] = poi
		return self.geocode(flags, gflags, **kwargs)

	def getLastResponse(self):
		return self._lastResponse

	def getQualityDescription(self, qualityNumber):
		return self._qualityMapping[str(qualityNumber)]

	def reverseGeocode(self, latitude, longitude, **kwargs):
		kwargs["q"] = "%s,%s" % (str(latitude), str(longitude))
		return self.geocode("", "R", **kwargs)


	############################################################################
	# Section: Private methods
	############################################################################

	def _buildOAuthParams(self, flags, gflags, **kwargs):
		params = {
			"oauth_version": "1.0",
			"oauth_nonce": oauth.generate_nonce(),
			"oauth_timestamp": int(time.time()),
			"oauth_consumer_key": self._key,
			"appid": self._appId,
			"flags": flags,
			"gflags": gflags
		}

		for arg in kwargs:
			params[arg] = kwargs[arg]

		return params

	def _buildUrl(self, flags, gflags, **kwargs):
		return "%s?appid=%s&flags=%s&gflags=%s&%s" % (self._baseUrl, self._appId, flags, gflags, urllib.urlencode(kwargs))

	def _getClient(self, consumer):
		return oauth.Client(consumer)

	def _getConsumer(self):
		return oauth.Consumer(key = self._key, secret = self._secret)

	def _signRequest(self, url, params, consumer):
		request = oauth.Request(method = "GET", url = url, parameters = params)
		request.sign_request(self._signatureMethod, consumer, None)

	def _validateQuery(self, **kwargs):
		validSearchTermFound = False

		fieldReqsCheck1 = (
			"q",
			"location",
			"name",
			"line1",
			"addr",
			"woeid"
		)

		fieldReqsCheck2 = (
			("street", "city", "country"),
			("street", "city", "state"),
			("latitude", "longitude")
		)

		for req in fieldReqsCheck1:
			if req in kwargs:
				validSearchTermFound = True
				break

		if not validSearchTermFound:
			for combo in fieldReqsCheck2:
				expectedMatches = len(combo)
				matches = 0

				for req in combo:
					if req in kwargs:
						matches += 1

				if matches == expectedMatches:
					validSearchTermFound = True
					break

		return validSearchTermFound

