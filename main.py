import requests
import location
import xml.etree.ElementTree as ET


def findattrib(elements, tag):
    for element in elements:
        if (element.tag == tag):
            return element.text

def get_stores(tree):
    root = tree.getroot()
    stores = {}
    for store in root.getchildren(): #getchildren():
        storeinfo = store.getchildren()
        name = findattrib(storeinfo, "Address1")
        store_num = findattrib(storeinfo, "Nr")
        rt90x = findattrib(storeinfo, "RT90x")
        rt90y = findattrib(storeinfo, "RT90y")
        stores[store_num] = {"name": name, "RT90x" : rt90x, "RT90y": rt90y}

    return stores

def get_store_articles(tree):
    root = tree.getroot()
    store_articles = {}
    for store in root.getchildren():
        articles = []
        for article in store.getchildren():
            articles = articles + [article.text] 
        store_num = store.attrib.get("ButikNr")
        store_articles[store_num] = articles

    return store_articles

def get_articles(tree):
    root = tree.getroot()
    articles = {}
    for article in root.getchildren():
        articleinfo = article.getchildren() 
        name = findattrib(articleinfo, "Namn")
        nr = findattrib(articleinfo, "nr")
        articles[name] = nr;

    return articles

def get_stores_with_article(stores, article):
    stores_with_article = []
    #print(stores)
    for store in stores:
        articles = stores[store]
        if article in articles:
            stores_with_article += [store]
    return stores_with_article

def get_stores_and_rt(stores, stores_with_article):
    store_and_rt = {}
    for store in stores_with_article:
        try:
            store_dict = stores[store]
            print(store_dict)
            store_and_rt[store] = [store_dict["RT90x"], store_dict["RT90y"]]
        except:
            continue
    return store_and_rt

    
    


def main():
    
    #stock = requests.get("http://www.systembolaget.se/api/assortment/stock/xml").text
    #products = requests.get("http://www.systembolaget.se/api/assortment/products/xml").text
    #stores = requests.get("http://www.systembolaget.se/api/assortment/products/xml").text
    stores = get_stores(ET.parse("stores.xml"))
    store_articles = get_store_articles(ET.parse("store_articles.xml"))
    articles = get_articles(ET.parse("articles.xml"))

    article_searched = "Renat"
    stores_with_article = get_stores_with_article(store_articles, articles[article_searched])
    stores_and_rt = get_stores_and_rt(stores, stores_with_article)
    #Load data from API
    print("commands is:\n 1 - enter address \n 2 - Enter beverage \n 3 - start search \n 0 - quit")
    
    notExit = True


    coordinates = (0, 0)
    beverage = ""

    while notExit:
        cmd = input("enter cmd: ")

        if cmd == "0":
            notExit = False
        elif cmd == "1":
            inp = input("enter address or coordinates (lat, lng): ");
            checkCoordinates = inp.split()
            if len(checkCoordinates) == 2 and checkCoordinates[0].isdigit and checkCoordinates[1].isdigit: 
                coordinates = (float(checkCoordinates[0]), float(checkCoordinates[1]))

                print(coordinates)
            else:
                addressResults = location.getAddressLocation(inp)
                print(addressResults[0][0])
                coordinates = (addressResults[0][1]["lat"], addressResults[0][1]["lng"])
                print(coordinates)
            
        elif cmd =="2":
            beverage = input("enter the exact name of the beverage: ")
            #Todo find stores
        elif cmd =="3":
            if coordinates[0] == 0 and coordinates[1] == 0:
                print("you have not entered an address")
            elif beverage =="":
                print("you have not entered a beverage")
            else:
                print("todo")
                #Find da stuff
        else:
            print("not a command")

main()