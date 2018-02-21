# -*- coding: utf-8 -*-
"""
Created on Fri Oct 13 13:07:27 2017

@author: walfaelschung
"""

# -*- coding: utf-8 -*-
"""

@author: walfaelschung
"""


#%% required packages:
import urllib.request
import json
import csv
import re
import time
import sys
import networkx as nx
from networkx.algorithms import bipartite
# pandas and os is only needed for the like network: TODO: get rid of it:
import pandas
import os

#%%  like scripts that need review

def getlikes(token,seed):
    data = urllib.request.urlopen("https://graph.facebook.com/v2.9/"+seed+"/likes?limit=100&access_token="+token).read()
    data = json.loads(data)
    list = data
    while "paging" in data and "next" in data["paging"]:
                        url = str(data["paging"]["next"])
                        data = urllib.request.urlopen(url).read()
                        data = json.loads(data)
                        for entry in data["data"]:
                            list["data"].append(entry)
    likenetwork = parselikes(list,seed, token)
    print ("..one more page found...")
    return likenetwork

def depthone(token,seed):
    a = getlikes(token,seed)
    #return a
    for page in a:
        getlikes(token,str(page["targetid"]))
# open the first file manually
    dtype_dic= {'sourceid': str, 'sourcename' : str, "targetid" : str, "targetname" : str}
    k = pandas.read_csv("likenetwork_"+seed+".csv", header=0, sep=";", dtype = dtype_dic)
# and append every following file
    for page in a:
        l = pandas.read_csv("likenetwork_"+page["targetid"]+".csv", header=0, sep=";", dtype = dtype_dic)
        k = k.append (l, ignore_index=True)

    k.to_csv("likenetwork_depth_one_"+seed+".csv", index=False, sep= ";",encoding='utf-8')
    os.remove("likenetwork_"+seed+".csv")
    for page in a:
        os.remove("likenetwork_"+page["targetid"]+".csv")

def getlikenetwork (idlist, token):
    for seed in idlist:
        print("Fetching page likes for page with ID "+seed)
        depthone (token,seed)
    dtype_dic= {'sourceid': str, 'sourcename' : str, "targetid" : str, "targetname" : str}
    p = pandas.read_csv("likenetwork_depth_one_"+seed+".csv", header=0, sep=";", dtype = dtype_dic)
    for page in idlist:
        o = pandas.read_csv("likenetwork_depth_one_"+page+".csv", header=0, sep=";", dtype = dtype_dic)
        p = p.append (o, ignore_index=True)
    p.to_csv("likenetwork_merged.csv", index=False, sep= ";", encoding='utf-8')

    # now read in the csv and create the like network
    dicti = []
    pageids = []
    targetids = []
    with open ("likenetwork_merged.csv", encoding="utf-8") as file:
        readCSV = csv.reader(file, delimiter=';')
        next(readCSV)
        for row in readCSV:
            pageid=row[0]
            targetid=row[2]
            pageids.append(pageid)
            targetids.append(targetid)

    for i in range(len(pageids)):
        if pageids[i] in idlist and targetids[i] in idlist:
            zeile = (pageids[i], targetids[i])
            dicti.append(zeile)

    # use networkx to make a file out of it and write to disk
    G=nx.Graph()
    G.add_edges_from(dicti)
    pagenames = []
    for i in idlist:
        a = getpageinfo(token,i)
        pagenames.append (a["name"])
    mapping = dict(zip(idlist, pagenames))
    G=nx.relabel_nodes(G,mapping)
    nx.write_graphml(G, "like_network_pages.graphml")
    nx.write_weighted_edgelist(G, 'like_network_edgelist.csv', delimiter=";", encoding="utf-8")
    print("Done with the page likes - You'll find an edgelist in csv-format and a graphml-file in your working directory.")
    dicti = []
    pageids = []
    targetids = []
    with open ("likenetwork_merged.csv", encoding="utf-8") as file:
        readCSV = csv.reader(file, delimiter=';')
        next(readCSV)
        for row in readCSV:
            pageid=row[0]
            targetid=row[2]
            pageids.append(pageid)
            targetids.append(targetid)
    for i in range(len(pageids)):
        if pageids[i] in idlist or targetids[i] in idlist:
            if pageids[i] in idlist and targetids[i] in idlist:
                pass
            else:
                zeile = (pageids[i], targetids[i])
                dicti.append(zeile)
    G=nx.Graph()
    G.add_edges_from(dicti)
    F = bipartite.weighted_projected_graph(G, idlist, ratio=False)
    pagenames = []
    for i in idlist:
        a = getpageinfo(token,i)
        pagenames.append (a["name"])
    mapping = dict(zip(idlist, pagenames))
    F=nx.relabel_nodes(F,mapping)
    nx.write_graphml(F, "allies_network_pages.graphml")
    nx.write_weighted_edgelist(F, 'allies_network_edgelist.csv', delimiter=";", encoding="utf-8")
    print("Done with the allies (page like overlap) - You'll find an edgelist in csv-format and a graphml-file in your working directory.")



#%%

def parselikes(list, seed, token):
    namelist = getpagename(token,seed)
    likeslist = []
    for entry in list["data"]:
        zeile = {"sourceid":namelist["id"], "sourcename":namelist["name"],"targetid":entry["id"],"targetname":entry["name"]}
        likeslist.append(zeile)
    with open("likenetwork_"+seed+".csv","w", newline='', encoding="utf-8") as file:
        columns = ["sourceid", "sourcename", "targetid","targetname"]
        writer = csv.writer(file, delimiter=";")
        writer.writerow(columns)
        for entry in likeslist:
            writer.writerow([entry["sourceid"], entry["sourcename"], entry["targetid"], entry["targetname"]])
    return likeslist
#%%
def tryRequestData(url, errorcount):
    if errorcount == 5:
         print ("Still can't establish connection. Log in and out of Facebook and try again later.")
         sys.exit()

    try:
        data= requestdata(url)
    except urllib.error.URLError as error:
        e = json.loads(error.read())
        if e["error"]["code"] == 190:
            print("There seems to be a problem with your access token. Please enter valid token or enter q to quit:")
            token = input()
            if token == "q":
                print(token)
                sys.exit()
            url = re.sub(r"token=.+", "token="+token, url)
            errorcount = errorcount + 1
            data= tryRequestData(url, errorcount)
        else:
            print("Unknown Facebook error. Trying again...")
            time.sleep(10)
            errorcount = errorcount + 1
            data = tryRequestData(url, errorcount)
    except:

        print ("Can't establish connection. Trying again.")
        time.sleep(10)
        errorcount = errorcount + 1
        data= tryRequestData(url, errorcount)
    return data

def getpageinfo(token,seed):
    try:
        data = urllib.request.urlopen("https://graph.facebook.com/v2.9/"+seed+"/?fields=id,name,about,category,cover,fan_count,rating_count,talking_about_count&access_token="+token).read()
        data = json.loads(data)
        return data
    except:
        pass
def requestdata(url):
    data = urllib.request.urlopen(url).read()
    return data
def getpagename(token,seed):
    data = urllib.request.urlopen("https://graph.facebook.com/v2.9/"+seed+"/?fields=id,name&access_token="+token).read()
    data = json.loads(data)
    return data

def grab (idlist, token):
    for seed in idlist:
        getdata (token,seed)


def getdata(token, seed, n):
    #global data
    url = "https://graph.facebook.com/v2.9/"+seed+"/feed?fields=from,link,permalink_url,message,type,created_time,reactions.limit(1000),comments.limit(100){created_time,from,message}&limit=1&access_token="+token
    datalist = []
    rounds = 1
    postcount = 1
    reactioncount = 0
    commentcount = 0
    errorcount = 0
    # get data from facebook graph api
    print("Loading post 1")
    data = tryRequestData(url, errorcount)

    data = json.loads(data)
    # here's our first post with 100 comments and 1000 reactions. Before we move to the next post, we want to retrieve all comments and reactions
    # get the comments:
    for post in data["data"]:
        if "comments" in post:
            if "paging" in post["comments"] and "next" in post["comments"]["paging"]:
                urlc = str(post["comments"]["paging"]["next"])
                print("More than 100 comments found...Let's get them all!")
                datac = tryRequestData(urlc, errorcount)
                #datac = urllib.request.urlopen(urlc).read()
                datac = json.loads(datac)
                for entry in datac["data"]:
                    data["data"][0]["comments"]["data"].append(entry)
                while "paging" in datac and "next" in datac["paging"]:
                    print ("...and another 100...")
                    urld = str(datac["paging"]["next"])
                    datac = tryRequestData(urld, errorcount)
                    datac = json.loads(datac)
                    for entry in datac["data"]:
                        data["data"][0]["comments"]["data"].append(entry)
            print ("I've got "+str(len(data["data"][0]["comments"]["data"]))+" comments, let's move on..")
            commentcount = commentcount + len(data["data"][0]["comments"]["data"])
    # get the reactions
    for post in data["data"]:
        if "reactions" in post:
            if "paging" in post["reactions"] and "next" in post["reactions"]["paging"]:
                urlr = str(post["reactions"]["paging"]["next"])
                print("More than 1000 reactions found...Let's get them all!")
                datar = tryRequestData(urlr, errorcount)
                #datar = urllib.request.urlopen(urlr).read()
                datar = json.loads(datar)
                for entry in datar["data"]:
                    data["data"][0]["reactions"]["data"].append(entry)
                while "paging" in datar and "next" in datar["paging"]:
                    print ("...and another 1000...")
                    urlt = str(datar["paging"]["next"])
                    datar = tryRequestData(urlt, errorcount)
                    #datar = urllib.request.urlopen(urlt).read()
                    datar = json.loads(datar)
                    for entry in datar["data"]:
                        data["data"][0]["reactions"]["data"].append(entry)
            print ("I've got "+str(len(data["data"][0]["reactions"]["data"]))+" reactions, let's move on..")
            reactioncount = reactioncount + len(data["data"][0]["reactions"]["data"])
    datalist.append(data)
# after the first post, we start writing the data to csv. This way, if something crashes during retrieval, the progress ist saved to disk.
    namelist = getpagename(token,str(seed))
    parsedata_first (datalist, seed,namelist)
# as long as there are posts left, the loop shall continue:

    while "paging" in data and "next" in data["paging"]:
        url = str(data["paging"]["next"])
        datalist_new = []
        rounds += 1
        postcount += 1
        print("Loading post "+ str(rounds))
        data = tryRequestData(url, errorcount)
        #data = urllib.request.urlopen(url).read()
        data = json.loads(data)
        # get the comments:
        for post in data["data"]:
            if "comments" in post:
                if "paging" in post["comments"] and "next" in post["comments"]["paging"]:
                    urlc = str(post["comments"]["paging"]["next"])
                    print("More than 100 comments found...Let's get them all!")
                    datac = tryRequestData(urlc, errorcount)
                    #datac = urllib.request.urlopen(urlc).read()
                    datac = json.loads(datac)
                    for entry in datac["data"]:
                        data["data"][0]["comments"]["data"].append(entry)
                    while "paging" in datac and "next" in datac["paging"]:
                        print ("...and another 100...")
                        urld = str(datac["paging"]["next"])
                        datac = tryRequestData(urld, errorcount)
                        #datac = urllib.request.urlopen(urld).read()
                        datac = json.loads(datac)
                        for entry in datac["data"]:
                            data["data"][0]["comments"]["data"].append(entry)
                print ("I've got "+str(len(data["data"][0]["comments"]["data"]))+" comments, let's move on..")
                commentcount = commentcount + len(data["data"][0]["comments"]["data"])
        # get the reactions
        for post in data["data"]:
            if "reactions" in post:
                if "paging" in post["reactions"] and "next" in post["reactions"]["paging"]:
                    urlr = str(post["reactions"]["paging"]["next"])
                    print("More than 1000 reactions found...Let's get them all!")
                    datar = tryRequestData(urlr, errorcount)
                    #datar = urllib.request.urlopen(urlr).read()
                    datar = json.loads(datar)
                    for entry in datar["data"]:
                        data["data"][0]["reactions"]["data"].append(entry)
                    while "paging" in datar and "next" in datar["paging"]:
                        print ("...and another 1000...")
                        urlt = str(datar["paging"]["next"])
                        datar = tryRequestData(urlt, errorcount)
                        #datar = urllib.request.urlopen(urlt).read()
                        datar = json.loads(datar)
                        for entry in datar["data"]:
                            data["data"][0]["reactions"]["data"].append(entry)
                print ("I've got "+str(len(data["data"][0]["reactions"]["data"]))+" reactions, let's move on..")
                reactioncount = reactioncount + len(data["data"][0]["reactions"]["data"])
        datalist_new.append(data)
        datalist.append(data)
        parsedata (datalist_new, seed,namelist)
        if rounds == n:
            break
    print("Retrieved "+str(postcount)+" posts")
    print("Retrieved "+str(commentcount)+" comments")
    print("Retrieved "+str(reactioncount)+" reactions")
    print("Let me write a csv-file to your working directory...")
    print("Done.")
    #parsedata (datalist, seed)
    return datalist

def parsedata_first(datalist, seed,namelist):
    list = []
    for entry in datalist:
        for post in entry["data"]:
            zeile = {"id":post["from"]["id"],"name":post["from"]["name"],"time":post["created_time"],"type":post["type"], "permalink":"", "link":"","message":""}
            try:
                zeile["message"] = post["message"]
            except:
                pass
            try:
                zeile["permalink"] = post["permalink_url"]
            except:
                pass

            try:
                zeile["link"] = post["link"]
            except:
                pass
            list.append(zeile)

# dealing with comments
            if "comments" in post:
                for comment in post["comments"]["data"]:
                    zeile = {"id":comment["id"],"name":comment["id"],"time":comment["created_time"],"type":"comment", "permalink":"", "link":"","message":comment["message"]}
                    list.append(zeile)

# dealing with reactions
            if "reactions" in post:
                for reaction in post["reactions"]["data"]:
                    zeile = {"id":reaction["id"],"name":reaction["name"],"time":post["created_time"],"type":reaction["type"], "permalink":"", "link":"", "message":""}
                    list.append(zeile)

    with open("posts_from_"+seed+".csv","w", newline='', encoding="utf-8") as file:
        columns = ["page_id", "page_name", "user_id","timestamp","type","link","permalink","message"]
        writer = csv.writer(file, delimiter=";")
        writer.writerow(columns)
        for entry in list:
            writer.writerow([namelist["id"], namelist["name"], entry["id"], entry["time"], entry["type"], entry["link"], entry["permalink"], entry["message"]])
    return list

#for all following posts, we use append mode
def parsedata(datalist, seed,namelist):
    list = []
    for entry in datalist:
        for post in entry["data"]:
            zeile = {"id":post["from"]["id"],"name":post["from"]["name"],"time":post["created_time"],"type":post["type"], "permalink":"", "link":"","message":""}
            try:
                zeile["message"] = post["message"]
            except:
                pass

            try:
                zeile["link"] = post["link"]
            except:
                pass
            try:
                zeile["permalink"] = post["permalink_url"]
            except:
                pass
            list.append(zeile)

# dealing with comments
            if "comments" in post:
                for comment in post["comments"]["data"]:
                    zeile = {"id":comment["id"],"name":comment["id"],"time":comment["created_time"],"type":"comment", "permalink":"", "link":"","message":comment["message"]}
                    list.append(zeile)

# dealing with reactions
            if "reactions" in post:
                for reaction in post["reactions"]["data"]:
                    zeile = {"id":reaction["id"],"name":reaction["name"],"time":post["created_time"],"type":reaction["type"], "permalink":"", "link":"", "message":""}
                    list.append(zeile)

    with open("posts_from_"+seed+".csv","a", newline='', encoding="utf-8") as file:
        writer = csv.writer(file, delimiter=";")
        for entry in list:
            writer.writerow([namelist["id"], namelist["name"], entry["id"], entry["time"], entry["type"], entry["link"], entry["permalink"], entry["message"]])
    return list

def getdatar(token, seed, since, until):
    #global data
    url = "https://graph.facebook.com/v2.9/"+seed+"/feed?fields=from,link,permalink_url,message,type,created_time,reactions.limit(1000),comments.limit(100){created_time,from,message}&limit=1&since="+since+"&until="+until+"&access_token="+token
    datalist = []
    rounds = 1
    postcount = 1
    reactioncount = 0
    commentcount = 0
    errorcount = 0
    # get data from facebook graph api
    print("Loading post 1")
    data = tryRequestData(url, errorcount)
        #data = urllib.request.urlopen("https://graph.facebook.com/v2.9/"+seed+"/feed?fields=from,link,permalink_url,message,type,created_time,reactions.limit(1000),comments.limit(100){created_time,from,message}&limit=1&access_token="+token).read()

    data = json.loads(data)
    # here's our first post with 100 comments and 5000 reactions. Before we move to the next post, we want to retrieve all comments and reactions
    # get the comments:
    for post in data["data"]:
        if "comments" in post:
            if "paging" in post["comments"] and "next" in post["comments"]["paging"]:
                urlc = str(post["comments"]["paging"]["next"])
                print("More than 100 comments found...Let's get them all!")
                datac = tryRequestData(urlc, errorcount)
                #datac = urllib.request.urlopen(urlc).read()
                datac = json.loads(datac)
                for entry in datac["data"]:
                    data["data"][0]["comments"]["data"].append(entry)
                while "paging" in datac and "next" in datac["paging"]:
                    print ("...and another 100...")
                    urld = str(datac["paging"]["next"])
                    datac = tryRequestData(urld, errorcount)
                    #datac = urllib.request.urlopen(urld).read()
                    datac = json.loads(datac)
                    for entry in datac["data"]:
                        data["data"][0]["comments"]["data"].append(entry)
            print ("I've got "+str(len(data["data"][0]["comments"]["data"]))+" comments, let's move on..")
            commentcount = commentcount + len(data["data"][0]["comments"]["data"])
    # get the reactions
    for post in data["data"]:
        if "reactions" in post:
            if "paging" in post["reactions"] and "next" in post["reactions"]["paging"]:
                urlr = str(post["reactions"]["paging"]["next"])
                print("More than 1000 reactions found...Let's get them all!")
                datar = tryRequestData(urlr, errorcount)
                #datar = urllib.request.urlopen(urlr).read()
                datar = json.loads(datar)
                for entry in datar["data"]:
                    data["data"][0]["reactions"]["data"].append(entry)
                while "paging" in datar and "next" in datar["paging"]:
                    print ("...and another 1000...")
                    urlt = str(datar["paging"]["next"])
                    datar = tryRequestData(urlt, errorcount)
                    #datar = urllib.request.urlopen(urlt).read()
                    datar = json.loads(datar)
                    for entry in datar["data"]:
                        data["data"][0]["reactions"]["data"].append(entry)
            print ("I've got "+str(len(data["data"][0]["reactions"]["data"]))+" reactions, let's move on..")
            reactioncount = reactioncount + len(data["data"][0]["reactions"]["data"])
    datalist.append(data)
# after the first post, we start writing the data to csv. This way, if something crashes during retrieval, the progress ist saved to disk.
    namelist = getpagename(token,str(seed))
    parsedata_first (datalist, seed,namelist)
# as long as there are posts left, the loop shall continue:

    while "paging" in data and "next" in data["paging"]:
        url = str(data["paging"]["next"])
        datalist_new = []
        rounds += 1
        postcount += 1
        print("Loading post "+ str(rounds))
        data = tryRequestData(url, errorcount)
        #data = urllib.request.urlopen(url).read()
        data = json.loads(data)
        # get the comments:
        for post in data["data"]:
            if "comments" in post:
                if "paging" in post["comments"] and "next" in post["comments"]["paging"]:
                    urlc = str(post["comments"]["paging"]["next"])
                    print("More than 100 comments found...Let's get them all!")
                    datac = tryRequestData(urlc, errorcount)
                    #datac = urllib.request.urlopen(urlc).read()
                    datac = json.loads(datac)
                    for entry in datac["data"]:
                        data["data"][0]["comments"]["data"].append(entry)
                    while "paging" in datac and "next" in datac["paging"]:
                        print ("...and another 100...")
                        urld = str(datac["paging"]["next"])
                        datac = tryRequestData(urld, errorcount)
                        #datac = urllib.request.urlopen(urld).read()
                        datac = json.loads(datac)
                        for entry in datac["data"]:
                            data["data"][0]["comments"]["data"].append(entry)
                print ("I've got "+str(len(data["data"][0]["comments"]["data"]))+" comments, let's move on..")
                commentcount = commentcount + len(data["data"][0]["comments"]["data"])
        # get the reactions
        for post in data["data"]:
            if "reactions" in post:
                if "paging" in post["reactions"] and "next" in post["reactions"]["paging"]:
                    urlr = str(post["reactions"]["paging"]["next"])
                    print("More than 1000 reactions found...Let's get them all!")
                    datar = tryRequestData(urlr, errorcount)
                    #datar = urllib.request.urlopen(urlr).read()
                    datar = json.loads(datar)
                    for entry in datar["data"]:
                        data["data"][0]["reactions"]["data"].append(entry)
                    while "paging" in datar and "next" in datar["paging"]:
                        print ("...and another 1000...")
                        urlt = str(datar["paging"]["next"])
                        datar = tryRequestData(urlt, errorcount)
                        #datar = urllib.request.urlopen(urlt).read()
                        datar = json.loads(datar)
                        for entry in datar["data"]:
                            data["data"][0]["reactions"]["data"].append(entry)
                print ("I've got "+str(len(data["data"][0]["reactions"]["data"]))+" reactions, let's move on..")
                reactioncount = reactioncount + len(data["data"][0]["reactions"]["data"])
        datalist_new.append(data)
        datalist.append(data)
        parsedata (datalist_new, seed,namelist)
#        if rounds == n:
#            break
    print("Retrieved "+str(postcount)+" posts")
    print("Retrieved "+str(commentcount)+" comments")
    print("Retrieved "+str(reactioncount)+" reactions")
    print("Let me write a csv-file to your working directory...")
    print("Done.")
    #parsedata (datalist, seed)
    return datalist

#%% auxiliary scripts not for data-collection but for the user-input
def listinput ():
    prompt = '> '
    idlist = []
    print ("Please input the first Facebook page ID you want to collect information about")
    a = input(prompt)
    idlist.append(a)
    print ("And the next one please...")
    a = input(prompt)
    idlist.append(a)
    nextinput (idlist)
    return idlist

def nextinput (idlist):
    prompt = '> '
    while True:
        print ("Add another ID or press [s]tart to collect data")
        strt = set(['start','s'])
        a = input(prompt).lower()
        if a in strt:
            return idlist
        else:
            idlist.append(a)
            continue
#%% change id deals with the problem of bipartite networks if user-id and page-id are identical due to admins posting on a site
            # admin id is replaced here.

def change_id(idlist, userids):
    output = []
    for i in userids:
        if i in idlist:
            i= i.replace(str(i),str(i+"admin"))
            output.append(i)
        else:
            output.append(i)
    return output
#%% the scripts for the network creation once the data is collected:


def networks(idlist, token):
#    print ("Let me calculate a network of co-usership between the pages you provided...")
#    pageids = []
#    userids = []
#    udict = {}
#    actdict = {}
#    cdict = {}
#    pdict = {}
#    rdict = {}
#    ids = idlist
#    for i in ids:
#        if os.path.isfile("posts_from_"+i+".csv"):
#
#            with open ("posts_from_"+i+".csv", encoding="utf-8") as file:
#                readCSV = csv.reader((x.replace('\0', '') for x in file), delimiter=';')
#                next(readCSV)
#                rows = 0
#                typesof = []
#                users = []
#                for row in readCSV:
#                    pageid=row[0]
#                    userid=row[2]
#                    typeof=row[4]
#                    pageids.append(pageid)
#                    userids.append(userid)
#                    users.append(userid)
#                    typesof.append(typeof)
#                    rows = rows+1
#                udict.update({i: len(set(users))})
#                actdict.update({i: rows})
#                cdict.update({i: typesof.count("comment")})
#                pdict.update({i: typesof.count("status") + typesof.count("photo") + typesof.count("video") + typesof.count("link") + typesof.count("event")})
#                rdict.update({i: typesof.count("LIKE") + typesof.count("SAD") + typesof.count("HAHA") + typesof.count("LOVE") + typesof.count("ANGRY")+ typesof.count("WOW")})
#
#        else:
#            print("The Facebook ID"+i+"has no matching file in the working directory. Has data been collected correctly?")
#
#
#    print("Handled "+str(len(actdict))+" page IDs.")
#
#    # trim idlist and dicts for empty entries:
#    actdict = {k: v for k, v in actdict.items() if v != 0}
#    ids = list(actdict.keys())
#    udict = {k: v for k, v in udict.items() if k in ids}
#    cdict = {k: v for k, v in cdict.items() if k in ids}
#    pdict = {k: v for k, v in pdict.items() if k in ids}
#    rdict = {k: v for k, v in rdict.items() if k in ids}
## the problem is: admin and page_id are identical: when admin from page A posts on page B,
## the graph is not strictly bipartite anymore, as now we do not ONLY have user-page connection,
## but page-page connection.
## those users that are page_admins (i.e. have the same user_id as page_id) will get little "admin" remark
## and applied it:
#    userids = change_id(ids, userids)
## write out to a bipartite edgelist
#    with open("edgelist_user.csv", "w", newline='', encoding="utf-8") as file:
#            writer = csv.writer(file, delimiter=";")
#            writer.writerow(["Source","Target"])
#            for i in range(len(userids)):
#
#                writer.writerow([userids[i], pageids[i]])
#
##
#    dicti = []
#    for i in range(len(userids)):
#        zeile = (userids[i], pageids[i])
#        dicti.append(zeile)
#
## and get us our networks:
#
#    G=nx.MultiGraph()
#    G.add_edges_from(dicti)
#    for u,v,data in G.edges(data=True):
#        w = data['weight'] = 1.0
#        G.edges(data=True)
#
#    H = nx.Graph()
#    for u,v,data in G.edges(data=True):
#        w = data['weight']
#        if H.has_edge(u,v):
#            H[u][v]['weight'] += w
#        else:
#           H.add_edge(u, v, weight=w)
##    H.edges(data=True)
##    H.is_directed()
##    nx.is_bipartite(H)
#    F = bipartite.weighted_projected_graph(H, ids, ratio=False)
#    nx.set_node_attributes(F, actdict, 'total_activities')
#    nx.set_node_attributes(F, udict, 'unique_users')
#    nx.set_node_attributes(F, cdict, 'comments')
#    nx.set_node_attributes(F, pdict, 'posts')
#    nx.set_node_attributes(F, rdict, 'reactions')
#    elist = list(F.edges())
#    for i in elist:
#        F[i[0]][i[1]]['sfrac'] = F[i[0]][i[1]]['weight'] / udict.get(i[0])
#        F[i[0]][i[1]]['tfrac'] = F[i[0]][i[1]]['weight'] / udict.get(i[1])
#        if F[i[0]][i[1]]['sfrac'] < F[i[0]][i[1]]['tfrac']:
#            F[i[0]][i[1]]['maxfrac'] = F[i[0]][i[1]]['sfrac']
#        else:
#            F[i[0]][i[1]]['maxfrac'] = F[i[0]][i[1]]['tfrac']
#    pagenames = []
#    for i in ids:
#        a = getpageinfo(token,i)
#        pagenames.append (a["name"])
#    mapping = dict(zip(ids, pagenames))
#    F=nx.relabel_nodes(F,mapping)
#    nx.write_graphml(F, "user_projection_pages.graphml")
#    nx.write_weighted_edgelist(F, 'user_projection_edgelist.csv', delimiter=";", encoding="utf-8")
#    print("Done with the user-overlap - You'll find a weighted edgelist in csv-format and a graphml-file in your working directory.")


    print ("Let me calculate a network of content overlap between the pages you provided...")
    # next we set a regular expression to extract links. MIT license from Diego Perini (https://gist.github.com/dperini/729294)
    #URL_REGEX = r'^(?:(?:https?|ftp)://)(?:\S+(?::\S*)?@)?(?:(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])){2}(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))|(?:(?:[a-z\u00a1-\uffff0-9]+-?)*[a-z\u00a1-\uffff0-9]+)(?:\.(?:[a-z\u00a1-\uffff0-9]+-?)*[a-z\u00a1-\uffff0-9]+)*(?:\.(?:[a-z\u00a1-\uffff]{2,})))(?::\d{2,5})?(?:/[^\s]*)?$'
    URL_REGEX = re.compile(
        u"^"
        # protocol identifier
        u"(?:(?:https?|ftp)://)"
        # user:pass authentication
        u"(?:\S+(?::\S*)?@)?"
        u"(?:"
        # IP address exclusion
        # private & local networks
        u"(?!(?:10|127)(?:\.\d{1,3}){3})"
        u"(?!(?:169\.254|192\.168)(?:\.\d{1,3}){2})"
        u"(?!172\.(?:1[6-9]|2\d|3[0-1])(?:\.\d{1,3}){2})"
        # IP address dotted notation octets
        # excludes loopback network 0.0.0.0
        # excludes reserved space >= 224.0.0.0
        # excludes network & broadcast addresses
        # (first & last IP address of each class)
        u"(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])"
        u"(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])){2}"
        u"(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))"
        u"|"
        # host name
        u"(?:(?:[a-z\u00a1-\uffff0-9]-?)*[a-z\u00a1-\uffff0-9]+)"
        # domain name
        u"(?:\.(?:[a-z\u00a1-\uffff0-9]-?)*[a-z\u00a1-\uffff0-9]+)*"
        # TLD identifier
        u"(?:\.(?:[a-z\u00a1-\uffff]{2,}))"
        u")"
        # port number
        u"(?::\d{2,5})?"
        # resource path
        u"(?:/\S*)?"
        u"$"
        , re.UNICODE)
    content_edgelist = []
    idict = {}
    actdict = {}
    cdict = {}
    pdict = {}
    rdict = {}
    ids = idlist
    for i in ids:
        linkids = []
        messageids = []
        pageids = []

        with open ("posts_from_"+i+".csv", encoding="utf-8") as file:
            readCSV = csv.reader((x.replace('\0', '') for x in file), delimiter=';')
            next(readCSV)
            rows = 0
            typesof = []
            for row in readCSV:
                pageid=row[0]
                typeof=row[4]
                linkid=row[5]
                messageid=row[7]
                pageids.append(pageid)
                linkids.append(linkid)
                messageids.append(messageid)
                typesof.append(typeof)
                rows = rows+1
            actdict.update({i: rows})
            cdict.update({i: typesof.count("comment")})
            pdict.update({i: typesof.count("status") + typesof.count("photo") + typesof.count("video") + typesof.count("link") + typesof.count("event")})
            rdict.update({i: typesof.count("LIKE") + typesof.count("SAD") + typesof.count("HAHA") + typesof.count("LOVE") + typesof.count("ANGRY")+ typesof.count("WOW")})
            urls = []
            for x in messageids:
                if isinstance(x, str) == True:
                    for url in re.findall(URL_REGEX, x):
                        urls.append(url)
            for x in linkids:
                if isinstance(x, str) == True:
                    for url in re.findall(URL_REGEX, x):
                        urls.append(url)
            urlset = set(urls)
            uniqueurls = list(urlset)
            idict.update({i: len(urlset)})
            for i in range(len(uniqueurls)):
                zeile = (uniqueurls[i], pageids[0])
                content_edgelist.append(zeile)
     # trim idlist and dicts for empty entries:
    actdict = {k: v for k, v in actdict.items() if v != 0}
    ids = list(actdict.keys())
#    udict = {k: v for k, v in udict.items() if k in ids}
    cdict = {k: v for k, v in cdict.items() if k in ids}
    pdict = {k: v for k, v in pdict.items() if k in ids}
    rdict = {k: v for k, v in rdict.items() if k in ids}

    with open("edgelist_content.csv", "w", newline='', encoding="utf-8") as file:
        writer = csv.writer(file, delimiter=";")
        writer.writerow(["Source","Target"])
        for i in range(len(content_edgelist)):
            writer.writerow(content_edgelist[i])

#
    G=nx.MultiGraph()
    G.add_edges_from(content_edgelist)
    for u,v,data in G.edges(data=True):
        w = data['weight'] = 1.0
        G.edges(data=True)
    H = nx.Graph()
    for u,v,data in G.edges(data=True):
        w = data['weight']
        if H.has_edge(u,v):
            H[u][v]['weight'] += w
        else:
            H.add_edge(u, v, weight=w)
    #    H.edges(data=True)
    #    H.is_directed()
    #    nx.is_bipartite(H)
    F = bipartite.weighted_projected_graph(H, ids, ratio=False)
    nx.set_node_attributes(F, 'total_activities', actdict)
    nx.set_node_attributes(F, 'comments', cdict)
    nx.set_node_attributes(F, 'posts', pdict)
    nx.set_node_attributes(F, 'reactions', rdict)
    elist = list(F.edges())
    for i in elist:
        F[i[0]][i[1]]['sfrac'] = F[i[0]][i[1]]['weight'] / idict.get(i[0])
        F[i[0]][i[1]]['tfrac'] = F[i[0]][i[1]]['weight'] / idict.get(i[1])
        if F[i[0]][i[1]]['sfrac'] < F[i[0]][i[1]]['tfrac']:
            F[i[0]][i[1]]['maxfrac'] = F[i[0]][i[1]]['sfrac']
        else:
            F[i[0]][i[1]]['maxfrac'] = F[i[0]][i[1]]['tfrac']
    pagenames = []
    for i in ids:
        a = getpageinfo(token,i)
        pagenames.append (a["name"])
    mapping = dict(zip(ids, pagenames))
    F=nx.relabel_nodes(F,mapping)
    nx.write_graphml(F, "content_projection_pages.graphml")
    nx.write_weighted_edgelist(F, 'content_projection_edgelist.csv', delimiter=";", encoding="utf-8")
    L = bipartite.weighted_projected_graph(H, uniqueurls, ratio=False)
    nx.write_graphml(L, "content_projection_content.graphml")
    nx.write_weighted_edgelist(F, 'content_projection_content_edgelist.csv', delimiter=";", encoding="utf-8")
    print("Done with the content overlap - You'll find a weighted edgelist in csv-format and a graphml-file in your working directory.")

    print("Do you want to collect the network of page-likes as well?")
    print("Note: This takes a while is not possible in retrospect. It will always collect the status quo.")
    print("So if you have already done it, for your set of pages, we recommend to skip.")
    print("Please provide a choice: [c]ollect page-like data or [s]kip:"),
    prompt = '>'
    skp = set(['skip','s'])
    cllct = set(['collect','c'])
    cors = input(prompt).lower()
    if cors in skp:
        pass
    if cors in cllct:
        print ("Okay, let us collect the network of page-likes")
        getlikenetwork (ids, token)


#%%


#%%
def main():
    token, idlist = prep()
    user(token, idlist)


def prep():
    print ("Preparing functions.")
    print ("Done.")
    prompt = '> '
    print ("Welcome to the Sammlr application.")
    print ("This tool will allow you to collect posts, comments, and reactions from a public Facebook page or create networks from multiple public Facebook pages.")
    print ("You are required to enter an acces token to the Facebook Graph API.")
    print ("Please provide your token before we start:")
    token = input(prompt)
    print ("Thanks.")
    print ("Now tell me, do you want to collect raw data from one page, or do you want the network of multiple pages?")
    print ("Please choose [s]ingle page or [n]etwork for more than one page:")
    sngl = set(['single','s'])
    ntwrk = set(['network','n'])
    sorn = input(prompt).lower()
    if sorn in sngl:
        print ("Please input the Facebook page ID you want to collect information about")
        seed = input(prompt)
        print ("Thanks.")
        pinfo = getpageinfo(token, seed)
        print("You want to collect data from the page "+pinfo["name"])
        idlist = []
        idlist.append(seed)
        return token, idlist
    if sorn in ntwrk:
        idlist = listinput()
        return token, idlist
def user(token, idlist):
    prompt = '> '
    print("By default, Sammlr will collect information on the last 100 posts")
    print("Alternatively, you can specify a date range or the number of posts to collect.")
    dflt = set(['default','d'])
    rng = set(['range','r'])
    nmbr = set(['number','n'])
    n = 100
    print("Please choose [d]efault, [r]ange, [n]umber, or any other key to exit:")
    choice = input(prompt).lower()
    if choice in dflt:
        print("You have chosen the default setting to collect the last 100 posts.")
        for i in idlist:
            seed = i
            try:
                getdata(token,seed,n)
            except:
                pass
    if choice in nmbr:
        print("You have chosen to specify the number of latests posts you want to collect.")
        print("Please provide a whole number:")
        n = int(input(prompt))
        for i in idlist:
            seed = i
            try:
                getdata(token,seed,n)
            except:
                pass
    if choice in rng:
        print("You have chosen to specify a date range for data collection.")
        print("Please provide the starting day in the format yyyy-mm-dd:")
        since = input(prompt).lower()
        print("Please provide the finishing day in the format yyyy-mm-dd:")
        until = input(prompt).lower()
        print("Allright, you want to collect data from "+since+" until "+until)
        print("If that is correct, please enter [y]es, otherwise press [r]estart or any key to exit.")
        yes = set(['yes','y'])
        restart = set(['restart','r'])
        choicetwo = input(prompt).lower()
        if choicetwo in yes:
            print("Allright, let's go.")
            for i in idlist:
                seed = i
                try:
                    getdatar(token,seed,since,until)
                except:
                    pass
        if choicetwo in restart:
            user(idlist,seed)
        else:
            pass
        #restart
    if len(idlist) > 1:
        networks(idlist,token)

    else:
        print("Bye, thanks for using Sammlr.")
  #%%

main()
