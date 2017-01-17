#!/usr/bin/env python

from bs4 import BeautifulSoup
import requests
import re
import math
from geopy.distance import vincenty
import smtplib
import datetime

def getPlace(pl):
    # scrape relevant info for an apartment, return as dict
    apt = {'price':pl.select_one("span.price").text, 'loc':pl["se:map:point"], "id":pl["data-id"]}
    apt["addr"] = pl.select_one("div.details-title a").text
    
    # does it have a brokers fee?
    apt["broker_fee"] = pl.select_one("div.banner.no_fee") is None
    
    # how far from Columbia?
    apt["dist"] = getDistFromColumbia(apt['loc'])
    
    # sometimes the size is not available
    apt_size = pl.select_one("span.last_detail_cell")
    if apt_size is not None:
        apt["size"] = apt_size.text
        
    # what neighborhood?
    apt["nbh"] = pl(text=re.compile(r' in '))[0]
    
    # url
    apt["href"] = "http://streeteasy.com" + pl.select_one("div.details-title a")["href"]
    
    return apt

def getDistFromColumbia(coords):
    #given a set of coordinates, how far in miles is that location from Columbia
    splt = coords.split(",")
    columbia = (40.807511,-73.9647077)
    dist = vincenty(columbia, splt).miles
    return dist



def sendMail(apt):
    # send an email with the apartment information
    fromMy = ''
    to  = ''
    subj='New Apt: ' + apt["price"] + ", Dist: "+str(apt["dist"])
    message_text=str(apt).encode('ascii', 'ignore')
    msg = "From: %s\nTo: %s\nSubject: %s\n\n%s" % ( fromMy, to, subj, message_text )

    username = ''  
    password = ''
    server = smtplib.SMTP("smtp.mail.yahoo.com",587)
    server.ehlo()
    server.starttls()
    server.login(username,password)
    server.sendmail(fromMy, to,msg)
    server.quit()
    


def main():
    steasy = "http://streeteasy.com/for-rent/nyc/price:1000-2000%7Carea:154,148,153,147%7Cbeds%3C1?sort_by=listed_desc"
    st = requests.get(steasy)
    soup = BeautifulSoup(st.text, "html.parser")
    stplaces = soup.select("div.item")

    places = [getPlace(s) for s in stplaces]
    
    #places already sent
    with open('places.txt', 'r+') as f:
        placeIds = f.read()
        for p in places:
            pSplit = placeIds.split(",")
            if p["id"] not in pSplit:
                #print("FOUND APT", p["id"])
                sendMail(p)
                f.write(p["id"]+",")
        f.close()


    #last updated time
    with open("time.txt", 'w+') as wr:
        fmt='%Y-%m-%d-%H-%M-%S'
        wr.write(datetime.datetime.now().strftime(fmt));


if __name__ == "__main__":
    main()