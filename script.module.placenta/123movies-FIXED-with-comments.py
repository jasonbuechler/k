import urlparse,traceback,urllib,re,json,xbmc

from resources.lib.modules import client
from resources.lib.modules import cleantitle
from resources.lib.modules import directstream
from resources.lib.modules import log_utils
from resources.lib.modules import source_utils

class source:
	def __init__(self):
		self.priority = 1
		self.language = ['en']
		self.domains = ['123movies.ph']
		self.base_link = 'https://123movies.ph/'
		self.source_link = 'https://123movies.ph/'
		self.episode_path = '/episodes/%s-%sx%s/'
		self.movie_path0 = '/movies/%s-watch-online-free-123movies-%s/'
		self.movie_path = '/movies/%s/'
#		self.decode_file = '/decoding_v2.php'
#		self.decode_file = '/decoding_v3.php'
		self.decode_file = 'https://gomostream.com/decoding_v3.php'
#		self.grabber_file = '/get.php'
#		self.grabber_file = '/getv2.php'
		self.grabber_file = 'https://gomostream.com/getv2.php'
		# $.ajax({ type: "POST",  url: "https://gomostream.com/decoding_v3.php" .....
		# $.ajax({ type: "POST",  url: "https://gomostream.com/getv2.php" .....
		
	def movie(self, imdb, title, localtitle, aliases, year):
		log_utils.log(imdb)
		log_utils.log("********************* 123: AT MOVIE DEF")
		log_utils.log("********************* 123: year = " + year)
		log_utils.log("********************* 123: title = " + title)
		url = {'title': title, 'year': year}
		log_utils.log(url)
		log_utils.log("after orig url")

		try:
			log_utils.log("in movie-try now ... !!")
			url = {'title': title, 'year': year}
			log_utils.log("CAN GET HERE?!?!??!?! url = vvv")
			log_utils.log(url)
			bob = urllib.urlencode(url)
			log_utils.log("bob = vvv")
			log_utils.log(bob)
			
			return urllib.urlencode(url)

		except Exception:
			return

	def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
		log_utils.log("INSIDE TVSHOW")
		try:
			data = {'tvshowtitle': tvshowtitle, 'year': year, 'imdb': imdb}
			return urllib.urlencode(data)

		except Exception:
			return

	def episode(self, url, imdb, tvdb, title, premiered, season, episode):
		log_utils.log("INSIDE ep")
		try:
			log_utils.log("in episode now ... !!")
			data = urlparse.parse_qs(url)
			data = dict((i, data[i][0]) for i in data)
			data.update({'season': season, 'episode': episode, 'title': title, 'premiered': premiered})

			return urllib.urlencode(data)

		except Exception:
			return

	def sources(self, url, hostDict, hostprDict):
		log_utils.log("INSIDE sources")
		try:
			sources = []
			log_utils.log("********************* 123: sources = nada")
			data = urlparse.parse_qs(url)
			log_utils.log(data)
			log_utils.log("^^^ data")
			data = dict((i, data[i][0]) for i in data)
			log_utils.log(data)

			if 'episode' in data:
				url = self.__get_episode_url(data)
				get_body = 'type=episode&%s=%s&imd_id=%s&seasonsNo=%02d&episodesNo=%02d'
			else:
				url = self.__get_movie_url(data)

			log_utils.log(url)
			log_utils.log("^^^ url AFTER get-movie-url")
			response = client.request(url)
			log_utils.log("^^^ past client request")

			url = re.findall('<iframe .+? src="(.+?)"', response)[0]
			log_utils.log(url)
			log_utils.log("^^^ url AFTER re.findall")

			response = client.request(url)
#			log_utils.log(response)

			token = re.findall('var tc = \'(.+?)\'', response)[0]
			
			# _tsd_tsd_ds(s) ~~~  .slice(3,29) ~~~~ "29"+"341404";   <----- seeds phrase has changed
#			seeds = re.findall('_tsd_tsd\(s\) .+\.slice\((.+?),(.+?)\).+ return .+? \+ \"(.+?)\"\+\"(.+?)";', response)[0]
			seeds = re.findall('_tsd_tsd_ds\(s\) .+\.slice\((.+?),(.+?)\).+ return .+? \+ \"(.+?)\"\+\"(.+?)\";', response)[0]
			log_utils.log("seeds vvv")
			log_utils.log(seeds)
			pair = re.findall('\'type\': \'.+\',\s*\'(.+?)\': \'(.+?)\'', response)[0]
			log_utils.log("pair vvv")
			log_utils.log(pair)			
			
			

			header_token = self.__xtoken(token, seeds)
			body = 'tokenCode=' + token
			log_utils.log("header token = " + header_token)
			log_utils.log("body = " + body)

			headers = {
				'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
				'x-token': header_token
			}

			log_utils.log(self.source_link + " <*********> " + self.decode_file)
			url = self.decode_file
			log_utils.log(url)
			log_utils.log("^^^ url")
			response = client.request(url, XHR=True, post=body, headers=headers)
			log_utils.log("^^ response acquired ^^")

			sources_dict = json.loads(response)
			log_utils.log("DIDN'T FAIL JSON LOADS???")
			log_utils.log("vvv sources_dict vvv")
			log_utils.log(sources_dict)
#			[u'https://video.xx.fbcdn.net/v/t42.9040-2/10000000_226259417967008_8033841240334139392_n.mp4?_nc_cat=0&efg=eyJybHIiOjE1MDAsInJsYSI6NDA5NiwidmVuY29kZV90YWciOiJzdmVfaGQifQ%3D%3D&rl=1500&vabr=616&oh=27f4d11aec3aa54dbe1ca72c81fbaa03&oe=5B4C6DF5', u'https://movienightplayer.com/tt0253754', u'https://openload.co/embed/ALXqqto-fQI', u'https://streamango.com/embed/pndcsolkpnooffdk']
			for source in sources_dict:
				log_utils.log("source = " + source)
				log_utils.log("source (str) = " + str(source))
				try:
#					if 'vidushare.com' in source:
					if '.mp4' in source:
						sources.append({
							'source': 'CDN',
							'quality': 'HD',
							'language': 'en',
							'url': source,
							'direct': True,
							'debridonly': False
						})
				except Exception:
					pass

			body = get_body % (pair[0], pair[1], data['imdb'], int(data['season']), int(data['episode']))

			url = urlparse.urljoin(self.source_link, self.grabber_file)
			response = client.request(url, XHR=True, post=body, headers=headers)

			sources_dict = json.loads(response)

			for source in sources_dict:
				try:
					quality = source_utils.label_to_quality(source['label'])
					link = source['file']

					if 'lh3.googleusercontent' in link:
						link = directstream.googleredirect(link)

					sources.append({
						'source': 'gvideo',
						'quality': quality,
						'language': 'en',
						'url': link,
						'direct': True,
						'debridonly': False
					})

				except Exception:
					pass


			return sources

		except Exception:
			return sources

	def resolve(self, url):
		return url

	def __get_episode_url(self, data):
		try:
			clean_title = cleantitle.geturl(data['tvshowtitle'])
			query = self.episode_path % (clean_title, data['season'], data['episode'])

			url = urlparse.urljoin(self.base_link, query)
			html = client.request(url)

			token = re.findall('\/?watch-token=(.*?)\"', html)[0]

			return url + ('?watch-token=%s' % token)

		except Exception:
			return

	def __get_movie_url(self, data):
			log_utils.log("get movie url!!!!!!!!!!!!!!")
			log_utils.log(data)
			clean_title = cleantitle.geturl(data['title'])
			
			query0 = self.movie_path0 % (clean_title,data['year'])	# the "long" version appears to use year (and its optional)
			query = self.movie_path % clean_title					# no fancy stuff should work fine (at least almost always)
			log_utils.log(query0)
			log_utils.log(query)
			url = urlparse.urljoin(self.base_link, query)
			log_utils.log("url = " + url)
			html = client.request(url)

			token = re.findall('\/?watch-token=(.*?)\"', html)[0]

			return url + ('?watch-token=%s' % token)
	def __xtoken(self, token, seeds):
		try:
			xtoken = token[int(seeds[0]):int(seeds[1])]
			xtoken = list(xtoken)
			xtoken.reverse()

			return ''.join(xtoken) + seeds[2] + seeds[3]

		except Exception:
			return
