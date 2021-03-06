import sys
from bs4 import BeautifulSoup
import urllib.request
import re
import time
import random

def getRateLimit():
    base = 240
    r = base*random.random()
    return base + r

class Posting:
    def __init__(self, title, date, contact):
        self.title = title
        self.date = date
        self.contact = contact
    def __str__(self):
        return "Title: %s\nDate: %s\nContact: %s" % (self.title, self.date, self.contact)

def soupPage(url):
    time.sleep(getRateLimit())
    data = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(data)
    return soup

def log(s):
    print("[Peek]: %s" % s)

class Scraper:
    RATE_LIMIT = 10
    def __init__(self, baseUrl):
        self.baseUrl = baseUrl

    def run(self, areas):
        allPosts = []
        for a in areas:
            allPosts += self.scrapeArea(a)
        return allPosts

    def scrapeArea(self, area):

        searchPart1 = "/erhegqey+"
        searchPart2 = "sac/n?ur="
        searchPart = interleave(searchPart1, searchPart2)
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
        contact = None
        for link in soup.find_all('a'):
            href = link.get('href')
            if re.search("^/reply", href):
                contact = href
        if contact is None:
            raise Exception("Didnt find contact info.")
        replyUrl = self.baseUrl % (area, contact)
        email = self.getEmail(replyUrl)
        return Posting(title, posted, email)

    def getEmail(self, replyUrl):
        log("Searching for contact info from %s" % replyUrl)
        soup = soupPage(replyUrl)
        for link in soup.find_all("input"):
            email = link.get("value")
            log("Found contact information: " + email)
            return email
        return None

def interleave(s1, s2):
    return "".join(i for j in zip(s1, s2) for i in j)

def main():
    baseUrl1 = "tp/%.risitogs"
    baseUrl2 = "ht:/scagls.r%"
    baseUrl = interleave(baseUrl2, baseUrl1)
    areas = sys.argv[1].split(" ")
    scraper = Scraper(baseUrl)
    posts = scraper.run(areas)
    s = ""
    for p in posts:
        s += str(p) + "\n"

    print(s)

if __name__ == '__main__':
    main()
