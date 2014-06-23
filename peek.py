import sys
from bs4 import BeautifulSoup
import urllib.request
import re
import time
RATE_LIMIT = 10 #seconds

class Posting:
    def __init__(self, title, date, contact):
        self.title = title
        self.date = date
        self.contact = contact
    def __str__(self):
        return "Title: %s\nDate: %s\nContact: %s" % (self.title, self.date, self.contact)

def soupPage(url):
    time.sleep(RATE_LIMIT)
    data = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(data)
    return soup

def log(s):
    print(str(s))

class Scraper:
    RATE_LIMIT = 10
    def __init__(self, baseUrl):
        self.baseUrl = baseUrl

    def run(self, areas):
        allPosts = []
        for a in areas:
            posts = self.scrapeArea(a)
            allPosts += posts
        return allPosts

    def scrapeArea(self, area):
        searchPart = "/search/eng?query=+"
        searchUrl = self.baseUrl % (area, searchPart)
        soup = soupPage(searchUrl)
        pages = []
        for link in soup.find_all('a'):
            href = link.get('href')
            link = self.baseUrl % (area, href)
            if re.search("^/eng", href):
                pages.append(link)
        pages = list(set(pages))
        postings = []
        for link in pages:
            postings.append(self.scrapePage(link, area))
        return postings

    def scrapePage(self, url, area):
        log("Scraping %s" % url)
        soup = soupPage(url)
        title = soup.find('h2').text.strip(' \t\n\r')
        log(title)
        posted = soup.find('time').text
        log(posted)
        replyPlace = None
        for link in soup.find_all('a'):
            href = link.get('href')
            if re.search("^/reply", href):
                replyPlace = href
        if replyPlace is None:
            raise Exception("Didnt find reply place")
        replyUrl = self.baseUrl % (area, replyPlace)
        email = self.getEmail(replyUrl)
        return Posting(title, posted, email)

    def getEmail(self, replyUrl):
        log("Searching for contact from %s" % replyUrl)
        soup = soupPage(replyUrl)
        for link in soup.find_all("input"):
            email = link.get("value")
            log("Found contact information: " + email)
            return email
        return None

def main():
    baseUrl = sys.argv[1]
    area = sys.argv[2]
    scraper = Scraper(baseUrl)
    posts = scraper.run([area])

    for p in posts:
        print(p)



if __name__ == '__main__':
    main()
