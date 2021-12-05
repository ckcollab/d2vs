import os
#from cv2 import correctMatches
dir = ".\d2vs\PICKIT"


pickfiles = os.listdir(dir)

#ItemsToKeep = {'name' : 'amulet', 'type' : 'amulet', 'quality' : 'rare', 'stats' : {'life' : '30', 'allres' : '20'}}
ItemstoKeep = [{}]
NametoType = {}

##This is a place to define item types
#2 handed weapons
TwoHPoleArm = "lance","polearm","colossusvolge"
TwoHMace = "marteldefer", "battlehammer"

#1 handed weapons 
OneHSword = "ancientsword","sword"
OneHAxe = "naga", "ancientaxe", "executionersword", "grimscythe", 
OneHMace = "mace","hammer"

#Bows
Bows = "gothicbow","longbow","shortbow"

#Wand

#Scepter

#Armors
Armor = "mageplate", "ornateplate"
Gloves = "wargauntlets", "gloves"
Helms = "grimhelm", "bonehelm", "corona"
Belts = "warbelt", "belt", "sash"
Charms = "grandcharm","largecharm","smallcharm"

for i in TwoHPoleArm: NametoType.update({i:"twohpolearm"})
for i in TwoHMace: NametoType.update({i:'twohmace'})
for i in OneHSword: NametoType.update({i:'onehsword'})
for i in OneHAxe: NametoType.update({i:'onehaxe'})
for i in OneHMace: NametoType.update({i:'onehmace'})
for i in Bows: NametoType.update({i:'bows'})
for i in Armor: NametoType.update({i:'armor'})
for i in Gloves: NametoType.update({i:'gloves'})
for i in Helms: NametoType.update({i:'helms'})
for i in Belts: NametoType.update({i:'belt'})
for i in Charms: NametoType.update({i:'charm'})    



def GetType(name):
    
    try:
        if name in NametoType:
            type = NametoType[name]
            return type
        else:
            if "amulet" in name:
                return "amulet"
            elif "ring" in name:
                return "ring"
    except ValueError:
        return "error"
    
    


for i in pickfiles:
    #print(i)
    dirWithFile = os.path.join(dir,i)
    file = open(dirWithFile)
    for line in file:
        if not line.startswith("//"): 
            if line.startswith("[name]"):
                #print(line)
                tmp = line.split("&&")
                name = tmp[0].strip("[name]")
                name = name.strip(" ==")
                name = name.strip()
            
            
                qualityANDstats = tmp[1].split("#")
                quality = qualityANDstats[0]

                if not qualityANDstats[1]:
                    print("error")
                else:
                    stats = qualityANDstats[1]

            
                quality = quality.strip("[quality] ")
                quality = quality.strip(" ==")
                #print("Name: " + name + " Quality = " + quality + " Stats = " + stats)
            
            
                ItemstoKeep.append({'name' : name, 'type' : GetType(name), 'quality' : quality, 'stats' :stats})

            if line.startswith("[type]"):
                tmp = line.split("&&")
                type = tmp[0].strip("[type]")
                type = type.strip(" ==")
                type = type.strip()
            
                name = ""

                qualityANDstats = tmp[1].split("#")
                quality = qualityANDstats[0]

                if not qualityANDstats[1]:
                    print("error")
                else:
                    stats = qualityANDstats[1]

            
                quality = quality.strip("[quality] ")
                quality = quality.strip(" ==")
                #print("Name: " + name + " Quality = " + quality + " Stats = " + stats)
            
            
                ItemstoKeep.append({'name' : name, 'type' : type, 'quality' : quality, 'stats' :stats}) 

    print(ItemstoKeep)            





