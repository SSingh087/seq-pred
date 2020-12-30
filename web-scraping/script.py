import urllib.request
import string
import os
from configparser import ConfigParser

def readConfigurations():
    confSettings = ConfigParser()
    confSettings.read("settings.ini")
    dictValues = {
        "iMaxTheta": confSettings.getint("angles","max_theta"),
        "iMinTheta" : confSettings.getint("angles","min_theta"),
        "iMaxPhi" : confSettings.getint("angles","max_phi"),
        "iMinPhi" : confSettings.getint("angles","min_phi"),
        "iDifference" : confSettings.getint("angles","angle_difference"),
        
        "iXCent": confSettings.getint("angles","xcent"),
        "iYCent": confSettings.getint("angles","ycent"),
        "iZoom": confSettings.getint("angles","zoom"),
        "iBright": confSettings.getint("angles","bright"),
        
        "iGas": confSettings.getint("angles","gas"),
        "iStar": confSettings.getint("angles","star"),
        "iDm": confSettings.getint("angles","dm"),
        "listShows": list(map(int,confSettings.get("experiment","shows").translate({ord(c): None for c in string.whitespace}).split(","))),
        "strFileName": confSettings.get("file","out_folder")
    }
    return dictValues

def getURLAndFile(dictValues):
    listUnF = []
    # listPairUnF = []
    strUrl = ""
    strFileName=""
    strTheta = ""
    strPhi = ""
    strShow = ""
    iXcent = dictValues["iXCent"]
    iYCent = dictValues["iYCent"]
    iZoom = dictValues["iZoom"]
    iBright = dictValues["iBright"]
    iGas = dictValues["iGas"]
    iStars = dictValues["iStar"]
    iDm = dictValues["iDm"]
    strFolderName = dictValues["strFileName"]
    i = 1
    for iShow in range(dictValues["listShows"][0], dictValues["listShows"][0]+10):
        for iThetaTemp in range(dictValues["iMinTheta"], dictValues["iMaxTheta"]+1, dictValues["iDifference"]):
            for iPhiTemp in range(dictValues["iMinPhi"], dictValues["iMaxPhi"]+1, dictValues["iDifference"]):
                strTheta = str(iThetaTemp)
                strPhi = str(iPhiTemp)
                strShow = str(iShow)
                strUrl = "http://galmer.obspm.fr/get_preview.cgi?"
                strUrl += "nbins=400"
                strUrl += "&snap_id=" + strShow
                strUrl += "&phi=" + strPhi
                strUrl += "&theta=" + strTheta
                strUrl += "&bins=" + str(1/iZoom)
                strUrl += "&bri=" + str(iBright)
                strUrl += "&xc=" + str(iXcent)
                strUrl += "&yc=" + str(iYCent)
                strUrl += "&gas=" + str(iGas)
                strUrl += "&stars=" + str(iStars)
                strUrl += "&halo=" + str(iDm)
                strUrl += "&quantity=0"
                strFileName = strFolderName +"/" + "d_" + strPhi + "_" + strTheta + "_3_" +  "(" + str(i) +").gif"
                listUnF.append([strUrl,strFileName])
        i+=1
    return listUnF

def downloadImages(dictValues):
    if not os.path.exists(dictValues["strFileName"]):
        os.makedirs(dictValues["strFileName"])
    listUnF = getURLAndFile(dictValues)
    print("Image count: ", len(listUnF))
    for strPairUnf in listUnF:
        print(strPairUnf[1])
        urllib.request.urlretrieve(strPairUnf[0], strPairUnf[1])
    

def main():
    dictValues = readConfigurations()
    downloadImages(dictValues)

if __name__ == "__main__":
    main()
