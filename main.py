import location

def main():
    
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
