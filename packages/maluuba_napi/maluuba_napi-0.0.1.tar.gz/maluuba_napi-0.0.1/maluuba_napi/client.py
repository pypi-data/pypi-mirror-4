import datetime
import json
import logging

import requests

class NAPINormalizeType(object):
	"""
	The types of entities that the normalize endpoint can work with.
	"""
	Time, DateRange, TimeRange = ('time', 'daterange', 'timerange')

class NAPIClient(object):
	"""
	A connection to the Maluuba NAPI.
	"""
	BASE_URL = 'http://napi.maluuba.com'
	VERSION  = 'v0'

	class InterpretResponse(object):
		"""
		A wrapper object for responses from the /interpret endpoint.
		"""
		def __init__(self, action, category, entities={}):
			self.action = action
			self.category = category
			self.entities = entities
			if 'dateRange' in self.entities:
				self.entities['dateRange'] = map(NAPIClient._parse_dateRange, self.entities['dateRange'])
			if 'timeRange' in self.entities:
				self.entities['timeRange'] = map(NAPIClient._parse_timeRange, self.entities['timeRange'])

	class NormalizeResponse(object):
		"""
		A wrapper object for the responses from the /normalize endpoint.
		"""
		def __init__(self, entities={}, context={}):
			self.entities = entities
			self.context = context
			if 'dateRange' in self.entities:
				self.entities['dateRange'] = map(NAPIClient._parse_dateRange, self.entities['dateRange'])
			if 'timeRange' in self.entities:
				self.entities['timeRange'] = map(NAPIClient._parse_timeRange, self.entities['timeRange'])


	@staticmethod
	def _parse_dateRange(dateRange):
		return {x: datetime.datetime.strptime(dateRange[x], '%Y-%m-%d').date() for x in dateRange}

	@staticmethod
	def _parse_timeRange(timeRange):
		return {x: datetime.datetime.strptime(timeRange[x], '%I:%M:%S%p').time() for x in timeRange}

	def __init__(self, api_key):
		self.api_key = api_key

	def __query(self, endpoint, **kwargs):
		kwargs['apikey'] = self.api_key
		r = requests.get(self.__generate_url(endpoint), params=kwargs)
		logging.debug("Called %s" % r.url)
		if r.status_code == 200:
			try:
				return json.loads(r.content)
			except Exception as e:
				logging.warn("Failed to parse response: %s" % r.content)
				pass
		else:
			logging.warn("Failure: %s" % r.status_code)

	def __generate_url(self, endpoint):
		return '%s/%s/%s' % (NAPIClient.BASE_URL, NAPIClient.VERSION, endpoint)

	def interpret(self, phrase):
		"""
		The primary endpoint of the NAPI. Classifies the given phrase, and extracts
		entities.
		"""
		return NAPIClient.InterpretResponse(**(self.__query('interpret', phrase=phrase)))

	def normalize(self, phrase, _type, timezone=''):
		"""
		Normalizes a time, date, or range.
		"""
		return NAPIClient.NormalizeResponse(**(self.__query('normalize', phrase=phrase, type=_type, timezone=timezone)))