#!/usr/bin/env python

from bs4 import BeautifulSoup
import requests
import re
import math
from geopy.distance import vincenty
import smtplib
import datetime

def getPlace(pl):

    apt = {'price':pl.select("span.price")[0].text, 'loc':pl["se:map:point"], "id":pl["data-id"]}
    apt["addr"] = pl.select("div.details-title a")[0].text
    apt["broker_fee"] = len(pl.select("div.banner.no_fee")) > 0
    apt["dist"] = getDistFromC(apt['loc'])

    apt_size = pl.select("span.last_detail_cell")[0] if len(pl.select("span.last_detail_cell")) > 0 else None
    if apt_size is not None:
        apt["size"] = apt_size.text
    
    apt["nbh"] = pl(text=re.compile(r' in '))[0]
    apt["href"] = "http://streeteasy.com"+pl.select("div.details-title a")[0]["href"]
    
    return apt

def getDistFromC(coords):
    splt = coords.split(",")
    clmb = (40.807511,-73.9647077) #columbia 
    dist = vincenty(clmb, splt).miles
    return dist

def sendMail(apt):
    fromMy = 'cdpconrad2119@yahoo.com' 
    to  = 'conrad.depeuter@gmail.com'
    subj='New Apt: ' + apt["price"] + ", Dist: "+str(apt["dist"])
    message_text=str(apt).encode('ascii', 'ignore')
    msg = "From: %s\nTo: %s\nSubject: %s\n\n%s" % ( fromMy, to, subj, message_text )

    username = str() #your email  
    password = str() #your pass  
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
                print("FOUND APT", p["id"])
                sendMail(p)
                f.write(p["id"]+",")
        f.close()


    #last updated time
    with open("time.txt", 'w+') as wr:
        fmt='%Y-%m-%d-%H-%M-%S'
        wr.write(datetime.datetime.now().strftime(fmt));

    print("DONE")


if __name__ == "__main__":
    main()