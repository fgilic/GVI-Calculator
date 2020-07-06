# This script is used to convert the green view index results saved in txt to Shapefile
# considering the facts many people are more comfortable with shapefile and GIS
# Copyright(C) Xiaojiang Li, Ian Seiferling, Marwa Abdulhai, Senseable City Lab, MIT


def read_gsv_info_text(gvi_res_txt, pano_id_list_all):
    """
    This function is used to read the information in text files or folders
    the function will remove the duplicate sites and only select those sites
    have GSV info in green month.

    Return:
        pano_id_lst, pano_date_lst, pano_lon_lst, pano_lat_lst, green_view_lst

    Parameters:
        gvi_res_txt: the file name of the GSV information txt file
        pano_id_list_all: list of processed panorama id (for removing duplicates)
    """

    # empty list to save the GVI result and GSV metadata
    pano_id_lst = []
    pano_date_lst = []
    pano_lon_lst = []
    pano_lat_lst = []
    green_view_lst = []

    # read the green view index result txt files
    lines = open(gvi_res_txt, "r")
    for line in lines:
        # check the completeness of each line, each line include attribute of, panoDate, lon, lat, greenview
        if "panoDate" not in line or "greenview" not in line:
            continue

        pano_id = line.split(" panoDate")[0][-22:]
        pano_date = line.split(" longitude")[0][-7:]
        coordinate = line.split("longitude: ")[1]
        lon = coordinate.split(" latitude: ")[0]
        lat_view = coordinate.split(" latitude: ")[1]
        lat = lat_view.split(', greenview:')[0]
        green_view = line.split("greenview:")[1]

        # check if the greeView data is valid
        if len(green_view) < 2:
            continue

        elif float(green_view) < 0:
            print(f'{pano_id}: {green_view}')
            continue

        # remove the duplicated panorama id
        if (pano_id not in pano_id_lst) and (pano_id not in pano_id_list_all):
            pano_id_lst.append(pano_id)
            pano_date_lst.append(pano_date)
            pano_lon_lst.append(lon)
            pano_lat_lst.append(lat)
            green_view_lst.append(green_view)

    return pano_id_lst, pano_date_lst, pano_lon_lst, pano_lat_lst, green_view_lst


# read the green view index files into list, the input can be file or folder
def read_gvi_res(gvi_res):
    """
        This function is used to read the information in text files or folders
        the function will remove the duplicate sites and only select those sites
        have GSV info in green month.

        Return:
            pano_id_lst,pano_date_lst,pano_lon_lst,pano_lat_lst,green_view_lst

        Parameters:
            gvi_res: the file name of the GSV information text, could be folder or txt file

        last modified by Xiaojiang Li, March 27, 2018
    """

    import os.path

    # empty list to save the GVI result and GSV metadata
    pano_id_lst = []
    pano_date_lst = []
    pano_lon_lst = []
    pano_lat_lst = []
    green_view_lst = []

    # if the input gvi result is a folder
    if os.path.isdir(gvi_res):
        all_txt_files = os.listdir(gvi_res)

        for txt_file in all_txt_files:
            # print('k')
            # only read the text file
            if not txt_file.endswith('.txt'):
                continue

            txtfilename = os.path.join(gvi_res, txt_file)

            # call the function to read txt file to a list
            [pano_id_lst_tem, pano_date_lst_tem, pano_lon_lst_tem, pano_lat_lst_tem, green_view_lst_tem] = \
                read_gsv_info_text(txtfilename, pano_id_lst)

            pano_id_lst = pano_id_lst + pano_id_lst_tem
            pano_date_lst = pano_date_lst + pano_date_lst_tem
            pano_lon_lst = pano_lon_lst + pano_lon_lst_tem
            pano_lat_lst = pano_lat_lst + pano_lat_lst_tem
            green_view_lst = green_view_lst + green_view_lst_tem

    elif gvi_res.endswith('.txt'):  # for single txt file
        [pano_id_lst, pano_date_lst, pano_lon_lst, pano_lat_lst, green_view_lst] = read_gsv_info_text(gvi_res, [])

    else:
        print('Input is not a folder nor a txt file.')

    return pano_id_lst, pano_date_lst, pano_lon_lst, pano_lat_lst, green_view_lst


def create_point_feature_ogr(output_shapefile, lon_lst, lat_lst, pano_id_list, pano_date_list, green_view_lst, lyrname):
    """
    Create a shapefile based on the template of inputShapefile
    This function will delete existing outpuShapefile and create a new shapefile containing points with
    pano_id, pano_date, and green view as respective fields.

    Parameters:
    output_shapefile: the file path of the output shapefile name, example 'd:\\greenview.shp'
      lon_lst: the longitude list
      lat_lst: the latitude list
      pano_id_list: the panorama id list
      pano_date_list: the panodate list
      green_view_lst: the green view index result list, all these lists can be generated from the function
      of 'Read_GVI_res'

    Copyright(c) Xiaojiang Li, Senseable city lab

    last modified by Xiaojiang li, MIT Senseable City Lab on March 27, 2018
    """

    import ogr
    import osr

    # create shapefile and add the above chosen random points to the shapfile
    driver = ogr.GetDriverByName("ESRI Shapefile")

    # create new shapefile
    if os.path.exists(output_shapefile):
        driver.DeleteDataSource(output_shapefile)

    data_source = driver.CreateDataSource(output_shapefile)
    target_spatial_ref = osr.SpatialReference()
    target_spatial_ref.ImportFromEPSG(4326)

    out_layer = data_source.CreateLayer(lyrname, target_spatial_ref, ogr.wkbPoint)
    num_pnt = len(lon_lst)

    print('the number of points is:', num_pnt)

    if num_pnt > 0:
        # create a field
        id_field = ogr.FieldDefn('PntNum', ogr.OFTInteger)
        pano_id_field = ogr.FieldDefn('panoID', ogr.OFTString)
        pano_date_field = ogr.FieldDefn('panoDate', ogr.OFTString)
        green_view_field = ogr.FieldDefn('greenView', ogr.OFTReal)
        out_layer.CreateField(id_field)
        out_layer.CreateField(pano_id_field)
        out_layer.CreateField(pano_date_field)
        out_layer.CreateField(green_view_field)

        for idx in range(num_pnt):
            # create point geometry
            point = ogr.Geometry(ogr.wkbPoint)

            # in case of the returned panoLon and PanoLat are invalid
            if len(lon_lst[idx]) < 3:
                continue

            point.AddPoint(float(lon_lst[idx]), float(lat_lst[idx]))

            # Create the feature and set values
            feature_defn = out_layer.GetLayerDefn()
            out_feature = ogr.Feature(feature_defn)
            out_feature.SetGeometry(point)
            out_feature.SetField('PntNum', idx)
            out_feature.SetField('panoID', pano_id_list[idx])
            out_feature.SetField('panoDate', pano_date_list[idx])

            if len(green_view_lst) == 0:
                out_feature.SetField('greenView', -999)
            else:
                out_feature.SetField('greenView', float(green_view_lst[idx]))

            out_layer.CreateFeature(out_feature)
            out_feature.Destroy()

        data_source.Destroy()

    else:
        print('You created a empty shapefile')


# ----------------- Main function ------------------------
if __name__ == "__main__":
    import os

    inputGVIres = '..\\kastela\\GVI_values'
    output_shapefile = '..\\kastela\\GVI_points.shp'
    lyrname = 'greenView'
    [pano_id_list, pano_date_list, lon_lst, lat_lst, green_view_lst] = read_gvi_res(inputGVIres)
    print('The length of the panoIDList is:', len(pano_id_list))

    create_point_feature_ogr(output_shapefile, lon_lst, lat_lst, pano_id_list, pano_date_list, green_view_lst, lyrname)

    print('Done!!!')
