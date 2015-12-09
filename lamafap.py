#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#  
#  lamafap.py
#  
#  Copyright 2015 dihamon <mas_b@epitech.eu>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  

import sys
import os		# for file manipulation
import http.client	# for http requests
import json		# for python parsing
import re		# for string manipulation
import urllib.request	# for file downloading

__version__ =	"1.0.0"
OAUTH_KEY =	"YOUR KEY HERE"
CACHE_PATH =	os.path.expanduser("~/.fap")
DOWNLOAD_PATH =	os.path.expanduser("~/Downloads/")

def get_next_likes(co, addr):
	"""main processing function for LikeStatus object
	retrieve 20 next likes each time it get called"""

	addr += "/likes?limit=20&offset=" + str(get_next_likes.ct) + "&api_key=" + OAUTH_KEY
	get_next_likes.ct += 20
	co.request("GET", addr)
	r = json.loads(co.getresponse().read().decode("utf-8"))
	posts = len(r["response"]["liked_posts"])
	photos = 0
	pics = []
	for post in r["response"]["liked_posts"]:
		if post["type"] == "photo":
			photos += 1
			for pic in post["photos"]:
				pics += [ pic["original_size"]["url"] ]
	if posts:
		print(posts, "posts and", len(pics), "photos in", photos, "posts", end="")
	return (posts, photos, pics)

class LikesStatus:
	"""parsing object for likes
	contains user likes specific informations"""

	pics = []
	ok = True
	def __init__(self, user):
		"""LikeStatus constructor
		init attributes"""

		path = CACHE_PATH + "_" + user
		self.cache = open(path, "r+" if os.access(path, os.F_OK) else "w+")
		tmp = self.cache.read()
		nbr = "0" if not len(tmp) else tmp
		print("=== infos loaded for user %s ===" % (user))
		print("=== content of %s ===\n%s" % (self.cache.name, nbr))
		co = http.client.HTTPConnection("api.tumblr.com", 80)
		addr = "/v2/blog/" + user + ".tumblr.com"
		co.request("GET", addr + "/info?api_key=" + OAUTH_KEY)
		tmp = co.getresponse().read().decode("utf-8")
		self.newNbr = int(re.sub(r'.*"likes":([^,}]+).*', r"\1", tmp))
		if int(nbr) == self.newNbr:
			print("=== Nothing to do. ===")
			self.ok = False
			return
		print("=== waiting for", self.newNbr, "posts ===")
		get_next_likes.ct = posts = photos = tmp = 0
		while True:
			tmp = get_next_likes(co, addr)
			if not tmp[0]: break
			posts += tmp[0]
			photos += tmp[1]
			self.pics += tmp[2]
			print(" - " + str(int(posts / self.newNbr * 100)) + "%")
		print("=== get", posts, "posts and", len(self.pics), "photos in", photos, "posts ===")

	def dl_new(self):
		"""downloader method
		download and save pic list to the default path"""

		for pic in self.pics:
			fname = DOWNLOAD_PATH + re.sub(r'.*/', r"", pic)
			if os.access(fname, os.F_OK):
				print("=== file already exists:", fname, "===")
			else:
				f = open(fname, "wb")
				f.write(urllib.request.urlopen(pic).read())
				f.close()
				print("=== writing to", fname, "===")
		self.cache.truncate()
		self.cache.write(str(self.newNbr))
		self.cache.close()

def usage():
	print("Usage: lamafap username...")
	return (1)

def main(argv):
	"""entry point
	browse the user list to process"""

	if not(len(argv)):
		return (usage())
	for user in argv:
		likes = LikesStatus(user)
		if likes.ok: likes.dl_new()
	return (0)

if __name__ == '__main__':
	sys.exit(main(sys.argv[1:]))
