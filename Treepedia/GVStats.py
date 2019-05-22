# This script is used to calculate some statistics for the Green View Results
# Copyright(C) Xiaojiang Li, Ian Seiferling, Marwa Abdulhai, Senseable City Lab, MIT


def Read_GSVinfo_Text(GVI_Res_txt):
    '''
    This function is used to read the information in text files or folders
    the fundtion will remove the duplicate sites and only select those sites
    have GSV info in green month.

    Return:
        panoIDLst,panoDateLst,panoLonLst,panoLatLst,greenViewLst

    Pamameters:
        GVI_Res_txt: the file name of the GSV information txt file
    '''

    import os,os.path

    # empty list to save the GVI result and GSV metadata
    panoIDLst = []
    panoDateLst = []
    panoLonLst = []
    panoLatLst = []
    greenViewLst = []

    # read the green view index result txt files
    lines = open(GVI_Res_txt,"r")
    for line in lines:
        # check the completeness of each line, each line include attribute of, panoDate, lon, lat,greenView
        if "panoDate" not in line or "greenview" not in line:
            continue

        panoID = line.split(" panoDate")[0][-22:]
        panoDate = line.split(" longitude")[0][-7:]
        coordinate = line.split("longitude: ")[1]
        lon = coordinate.split(" latitude: ")[0]
        latView = coordinate.split(" latitude: ")[1]
        lat = latView.split(', greenview:')[0]
        greenView = line.split("greenview:")[1]

        # check if the greeView data is valid
        if len(greenView)<2:
            continue

        elif float(greenView) < 0:
##            print(greenView)
            continue

        # remove the duplicated panorama id
        if panoID not in panoIDLst:
            panoIDLst.append(panoID)
            panoDateLst.append(panoDate)
            panoLonLst.append(lon)
            panoLatLst.append(lat)
            greenViewLst.append(greenView)

    return panoIDLst,panoDateLst,panoLonLst,panoLatLst,greenViewLst



# read the green view index files into list, the input can be file or folder
def Read_GVI_res(GVI_Res):
    '''
        This function is used to read the information in text files or folders
        the fundtion will remove the duplicate sites and only select those sites
        have GSV info in green month.

        Return:
            panoIDLst,panoDateLst,panoLonLst,panoLatLst,greenViewLst

        Pamameters:
            GVI_Res: the file name of the GSV information text, could be folder or txt file

        last modified by Xiaojiang Li, March 27, 2018
        '''

    import os,os.path

    # empty list to save the GVI result and GSV metadata
    panoIDLst = []
    panoDateLst = []
    panoLonLst = []
    panoLatLst = []
    greenViewLst = []


    # if the input gvi result is a folder
    if os.path.isdir(GVI_Res):
        allTxtFiles = os.listdir(GVI_Res)

        for txtfile in allTxtFiles:
            print('k')
            # only read the text file
            if not txtfile.endswith('.txt'):
                continue

            txtfilename = os.path.join(GVI_Res,txtfile)

            # call the function to read txt file to a list
            [panoIDLst_tem,panoDateLst_tem,panoLonLst_tem,panoLatLst_tem,greenViewLst_tem] = Read_GSVinfo_Text(txtfilename)

            panoIDLst = panoIDLst + panoIDLst_tem
            panoDateLst = panoDateLst + panoDateLst_tem
            panoLonLst = panoLonLst + panoLonLst_tem
            panoLatLst = panoLatLst + panoLatLst_tem
            greenViewLst = greenViewLst + greenViewLst_tem

    else: #for single txt file
        [panoIDLst_tem,panoDateLst_tem,panoLonLst_tem,panoLatLst_tem,greenViewLst_tem] = Read_GSVinfo_Text(txtfilename)


    return panoIDLst,panoDateLst,panoLonLst,panoLatLst,greenViewLst



## ----------------- Main function ------------------------
if __name__ == "__main__":
    import os
    import sys
    import numpy as np
    import matplotlib.pyplot as plt
    import seaborn as sns


    inputGVIres = r'C:\\Users\\rangu_uhpmatw\\Documents\\GitHub\\customs\\Treepedia_Public\\SA\\SA_GVR'
    outputShapefile = 'C:\\Users\\rangu_uhpmatw\\Documents\\GitHub\\customs\\Treepedia_Public\\SA\\SA_GVR.shp'
    lyrname = 'greenView'
    [_,_,_,_,SA] = Read_GVI_res(inputGVIres)
    print ('The length of the SA is:', len(SA))
    SA = np.array(SA).astype(np.float)
    print(np.average(SA))

    inputGVIres = r'C:\\Users\\rangu_uhpmatw\\Documents\\GitHub\\customs\\Treepedia_Public\\LB\\LB_GVR'
    outputShapefile = 'C:\\Users\\rangu_uhpmatw\\Documents\\GitHub\\customs\\Treepedia_Public\\LB\\LB_GVR.shp'
    [_,_,_,_,LB] = Read_GVI_res(inputGVIres)
    print ('The length of the LB is:', len(LB))
    LB = np.array(LB).astype(np.float)
    print(np.average(LB))

    sns.set_style('whitegrid')
    sns.distplot(SA)
    plt.show()
    sns.distplot(LB)
    plt.show()
    

    plt.boxplot([SA,LB], vert=False, whis=3.1)
    plt.yticks([1, 2], ['Santa Ana', 'Long Beach'])
    plt.show()

##    plt.boxplot(LB, vert=False)
##    plt.show()

    print('Done!!!')
