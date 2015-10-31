import requests
import location
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import xml.etree.ElementTree as ET
from threading import Thread
import time

maxDistance = 10000000

def findattrib(elements, tag):
    for element in elements:
        if (element.tag == tag):
            return element.text
    return ""

def get_stores(tree):
    root = tree.getroot()
    stores = {}
    for store in root.getchildren(): #getchildren():
        storeinfo = store.getchildren()
        name = findattrib(storeinfo, "Namn")
        
        if False == isinstance(name, str):
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
            #print(store_dict)
            store_and_rt[store] = [float(store_dict["RT90x"]), float(store_dict["RT90y"])]
        except:
            continue
    return store_and_rt

def get_closest_store(loc, stores_and_rt):
    distance = maxDistance
    store_key = 0

    for store in stores_and_rt:
        store_location = (stores_and_rt[store][0], stores_and_rt[store][1])
        store_location = location.rt90_to_wgs84(store_location)
        d = location.distanceRound(loc, store_location)

        if(d < distance):
            distance = d
            store_key = store
    
    return (distance, store_key)

def get_store_name(store_key, stores):
    return stores[store_key]["name"]

def get_best_match(article_dict, key):
    best_keys = []
    for k in article_dict.keys():
        m_r = fuzz.ratio(k,key)
        if m_r == 100:
            best_keys = [k]
            break
        if m_r > 70:
            best_keys += [k]
    return best_keys

def main():

    thread = Thread(target = printSplash, args = ())
    thread.start()


    #stock = requests.get("http://www.systembolaget.se/api/assortment/stock/xml").text
    #products = requests.get("http://www.systembolaget.se/api/assortment/products/xml").text
    #stores = requests.get("http://www.systembolaget.se/api/assortment/products/xml").text
    stores = get_stores(ET.parse("stores.xml"))
    store_articles = get_store_articles(ET.parse("store_articles.xml"))
    articles = get_articles(ET.parse("articles.xml"))

    #Load data from API
     
    not_exit = True


    coordinates = (0, 0)
    article_searched = ""
    thread.join()

    while not_exit:
        print("commands is:\n 1 - enter address \n 2 - Enter beverage \n 3 - start search \n 0 - quit")
        cmd = input("enter cmd: ")

        if cmd == "0":
            not_exit = False
        elif cmd == "1":
            inp = input("enter address or coordinates (lat, lng): ");
            checkCoordinates = inp.split()
            if len(checkCoordinates) == 2 and checkCoordinates[0].isdigit() and checkCoordinates[1].isdigit(): 
                coordinates = (float(checkCoordinates[0]), float(checkCoordinates[1]))

                print(coordinates)
            else:
                addressResults = location.getAddressLocation(inp)
                selectedAddress = 0
                if len(addressResults) > 1:
                    print("multiple addresses")
                    for i in range(0, len(addressResults)):
                        print("{} - {}".format(i+1, addressResults[i][0]))
                    selectedAddress = int(input("Select address: ")) - 1
                print(addressResults[selectedAddress][0])
                coordinates = (addressResults[selectedAddress][1]["lat"], addressResults[selectedAddress][1]["lng"])
                print(coordinates)
            
        elif cmd =="2":
            while True:
                article_searched = input("enter the name of the beverage: ")
                matching_articles = get_best_match(articles, article_searched)
                if (len(matching_articles) > 0):
                    if fuzz.ratio(matching_articles[0], article_searched) == 100:
                        break
                    print("Which one did you mean?")
                    i = 0
                    for a in matching_articles:
                        print("(" + str(i) + ") " + a)
                        i += 1
                    index = input("Enter index: ")
                    index = int(index)# Catch not number exception
                    article_searched = matching_articles[index]
                    break
                else:
                    print("Not found")
            stores_with_article = get_stores_with_article(store_articles, articles[article_searched])
            stores_and_rt = get_stores_and_rt(stores, stores_with_article)

        elif cmd =="3":
            if coordinates[0] == 0 and coordinates[1] == 0:
                print("\tyou have not entered an address")
            elif article_searched == "":
                print("\tyou have not entered an article")
            else:
                (distance, key) = get_closest_store(coordinates, stores_and_rt)
                if distance == maxDistance:
                    print("\tNo store found")
                else:
                    print("\t\tClosest store is: {}".format(get_store_name(key, stores)))
                    print("\t\t{} metres away".format(int(distance)))

        else:
            print("not a command")



def printSplash():
    print("                `.----//////////++o+ooo+o+oosssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssyso+++++++++++++/:.                ")
    print("              .-/yyyyyyyyyyyyyyyyyyyyyyysssssssssssssssssssssssssssssssssssoosssssoosssssssoossooooooooooooooooooooooooooooo-`              ")
    print("            ``/syyysssssoooooo++++++//////////:::::::::::::::-----------------------:::::::::::::::::::::::::://////////ooooo/-`            ")
    print("           ./oyyys+-------:::--------------------------------------------::::::::::::::::--------------------------------/ooooo:.           ")
    print("         `-+yyyyo:-::+oooooossssssssyyyyyyyyyyhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhyyyyyyyyyyo---:+oooo/:`         ")
    print("       `.+yyyyo::::+hdddddhhhhhhhhhhhyyyyyyyyyssssssssssssoooooooooooooooooooooooooooooooooossssssssssssssyyyyyyyyyyhddh+---:+oooo/.`       ")
    print("      :/yyyys/:::/yddh+//::::::::::::::::::::::::-:-----------------------------------------------------------------:ohddy/---:+oooo+:`     ")
    print("    ./shhhy+:::/shdho::::::::::::::::::::::::::::::::-----------------------------------------------------------------:sddds:---/ooooo/`    ")
    print("  `-ohhhho:-::ohdds/::::::::::::::::::::::::::::::::::-::---------------------------------::::::::::::::::::-::---------/yddho:---/oooo+/.  ")
    print("`:/yhhhs:--:+hddy+::::::::::::::::::::::::::::::::::::::--------------------------------:---:::::::::::--::---------------+yddh+--.-+ooos+-.")
    print(":ydhhy/---/yhhh+:::::::::::::::::::::::::::::::::::::::-----------------------------------:-:::::-:::::-::------------------+hddy/-..:ooosso")
    print("hddho---:shhho:::::::::::::::::::::::::::::::::::::::-------------------------------------:-::-:::::::::::-------------------:ohdhs:...+ssss")
    print("hddh:--/hhhs/:::::::::::::::::::::::::::::::::://///::::/++++/:/:-:+++++++++++/-/+++++++++//:-://////::---:::::::--------------:yhhy-../ssss")
    print("hhhh:--/hhy::::::::::::::::oysooossho-+shddds/:ohdyo::sho////oyh/-ohs+/hdh+/+hy:/+yddy++++yd/-:osdhdds:--:shdddys:--------------ohhy-../ssss")
    print("hhhy:--/hhy:::::::::::::::sds::::::so::::shdy/:sh/:--+dds++///:o:-/+---ydh/--/+:--+dds::os:o/---:dosdd+--oh+hdh:----------------odhy-../ssss")
    print("hhhy:--/hhy:::::::::::::::ohdhhhhhyo/:--:-/ydhho:----:oyhhhhddhs:------hdh/-------+ddhsydy:-----:do:ydh:/h+:hdh:----------------ohhy-..+ssss")
    print("hhhy:--+hhy:::::::::::::::///++++oydy::::::/ddy::-:::/s:-::::/hdo-----:hdh/-------+dds::+o/s/--::do-/hdyhs::hdh:----------------ohhy.../ssss")
    print("hhhy:--+hhy:::::::::::::::yh+::::/sdo:::::+sddho+::::+dyo+//+shs:---:osdddyo/--:+ohddyoooshd+:/osdy+:oddy:/+hddo/:--------------odhy...+ssss")
    print("hhhy:--+hhy:::::::::::::::oo+ssssso/:::::/+++++++:::::/::/+++/:-----:///////:--::///////////:::///++::/+::+++++++:--------------odhy...+ssss")
    print("hhhy:--+hhy:::::::::::::::::::::::::::::::::::::::::::::::::::--------------::::::::::::::::::::::::::::::::::::----------------sdhy...+ssss")
    print("hhhy:--+hhy::::::::::::::::::::::::::::::::::::::::::::::::::::::-:-:--:::::::::::::::::::::::::::::::::::::::::::--------------shhy...+ssss")
    print("hhhy:--+hhy::::::::::::::::::::::::::://++++/:::::+++++++:::::::::::/++/:::::::::/oosoo+/+/::/+++++++++//::://////::::::--------sdhy...+ssso")
    print("hhhy:--+hhy::::::::/yyhhhsssyhho:::/ohhso++shhs/:/osddds+::::::::::/hydd+::::::shds+/:/+ydo::/+sddho++oydo:/dhsoyddyoshh:-------sdhy...+ssss")
    print("hhhy:--+hhy::::::::::+ddy/::/hdh/:/hdd+:::::/hdd+::/hdh:::::::::::/hs:sdh/::::ydd+:::::::o/::::/ddh::+y/o+:/s/::sddo::/y:-------sdhs...+ssss")
    print("hhhy:--+hdy::::::::::/ddhssyhdy+::+ddh:::::::sdds::/hdh::::::::::/hy:::ydh/::/ddh/:::/ssssss+::/dddyydh/::::::::sddo::::::------sdhs...+ssso")
    print("hhhy:--ohdy:::::::::/+ddh////sdds:/ddh/:::::/hdd+::/hdh::::+y:::/hhssssshdh/::sdds::::/+ddy/:::/ddh/:+s/so::::::sddo:::::::-----sdds...+ssso")
    print("hhhy:--ohhy:::::::://oddh//++yddo::+ydhs+++shdy+:/sydddsssydh:+shdy+:::oyddhs+:+yhhsoosyhds::/sydddsooshdo::::+ohddy+/:::::-----ydds...+ssss")
    print("hhhy:-:ohdy::::::::+sssssssooo+/:::::/+oooo+/::::://////////:::/:::::::::::::::::://++/:::::::///////++++/::::+++oooo+:::::-----ydds...+ooso")
    print("hhhs:::ohhy/:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::----/hdds...+osss")
    print("hhhy:-:/hhdho:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::---:sdddy/...+ssss")
    print("hhhhs/:::ohddh+:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::-:sdddy+-..:ossso:")
    print(":shhhhs/:::shddy+:::::::::::::::::::::::::::::::::::::::::::::::::::---:::::::::::::::::::::::::::::::::::::::::::::::::::shddh+---:ossss/.`")
    print("`./shyyys/::/sdddy/::::::::::::::::::::::::::::::::::::::::::---------------:--:::::::::::::::::::::::::::::::::::::::::ohddh+---:ossss/.`  ")
    print("   .:syyyyo/::/yddds/:::::::::::::::::::::::::::::::::::-------------------------:::::::::::::::::::::::::::::::::::::ohddho:--:+ssss+-`    ")
    print("    `:/oyyyyo:::/yddho/::::::::::////////////++++++++++++++++++++++++++++oooooooooooooo++++++++++++++++++//////////:ohddho:--:+ssso/:-      ")
    print("       .:syyyy+:::+yddhhhhhhhdddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddho:--:+ssso+.`        ")
    print("         -/yyyyy+:::+ssssooooooooo++++++++++//////////////////:::::::::::::::::::::::////////////////////+++++++++++o+:--:+osso+-.          ")
    print("          ..oyyyyy+::--::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::----------:+ssss+-`            ")
    print("            .:+yyyyyyyyyyyyyyyyyyyyyyysssssssssoooooooooooooooooooooooooooooooooooooooo++++o+oooooooooooooooooooooooooossss+-`              ")
    print("              `:oyyyyyyyyyyyyyyyyysssssssssosooooooooooooooooooooooooooooooo++oo+++++++++++++o+++++++oooo+ooooooooooossss+:-`               ")


    #time.sleep(2)
    #print("\n\n\n\n\n\nStuff is loading for ya, please wait typ")
main()
