# This function is used to collect the metadata of the GSV panoramas based on the sample point shapefile

# Copyright(C) Xiaojiang Li, Ian Seiferling, Marwa Abdulhai, Senseable City Lab, MIT


def gsv_pano_metadata_collector(samples_feature_class, num, output_text_folder):
    """
    This function is used to call the Google API url to collect the metadata of
    Google Street View Panoramas. The input of the function is the shpfile of the create sample site, the output
    is the generate panoinfo metrics stored in the text file

    Parameters:
        samples_feature_class: the shapefile of the create sample sites
        num: the number of sites processed every time
        output_text_folder: the output folder for the panoinfo
    """

    from urllib import request
    import xmltodict
    import ogr
    import osr
    import time
    import os.path
    import math

    if not os.path.exists(output_text_folder):
        os.makedirs(output_text_folder)

    driver = ogr.GetDriverByName('ESRI Shapefile')

    # change the projection of shapefile to the WGS84
    dataset = driver.Open(samples_feature_class)
    layer = dataset.GetLayer()

    source_proj = layer.GetSpatialRef()
    target_proj = osr.SpatialReference()
    target_proj.ImportFromEPSG(4326)
    transform = osr.CoordinateTransformation(source_proj, target_proj)

    # loop all the features in the featureclass
    # feature = layer.GetNextFeature()
    feature_num = layer.GetFeatureCount()
    batch = int(math.ceil(feature_num / num))
    print(batch)

    for b in range(batch):
        # for each batch process num GSV site
        start = b * num
        end = (b + 1) * num
        if end > feature_num:
            end = feature_num

        output_text_file = 'Pnt_start%s_end%s.txt' % (start, end)
        output_gsv_info_file = os.path.join(output_text_folder, output_text_file)

        # skip over those existing txt files
        if os.path.exists(output_gsv_info_file):
            continue

        time.sleep(1)

        with open(output_gsv_info_file, 'w') as panoInfoText:
            # process num feature each time
            for i in range(start, end):
                feature = layer.GetFeature(i)
                geom = feature.GetGeometryRef()

                # transform the current projection of input shapefile to WGS84
                # WGS84 is Earth centered, earth fixed terrestrial ref system
                geom.Transform(transform)
                # TODO check what is happening with axis order
                lon = geom.GetY()
                lat = geom.GetX()

                # get the meta data of panoramas
                url_address = 'http://maps.google.com/cbk?output=xml&ll=%s,%s' % (lat, lon)

                time.sleep(0.05)
                # the output result of the meta data is a xml object
                meta_dataxml = request.urlopen(url_address)
                meta_data = meta_dataxml.read()

                data = xmltodict.parse(meta_data)

                # in case there is not panorama in the site, therefore, continue
                if data['panorama'] is None:
                    continue
                else:
                    pano_info = data['panorama']['data_properties']

                    # get the meta data of the panorama
                    pano_date = list(pano_info.items())[4][1]
                    pano_id = list(pano_info.items())[5][1]
                    pano_lat = list(pano_info.items())[8][1]
                    pano_lon = list(pano_info.items())[9][1]

                    print('The coordinate (%s,%s), panoId is: %s, panoDate is: %s' % (pano_lon, pano_lat, pano_id,
                                                                                      pano_date))
                    line_txt = 'panoID: %s panoDate: %s longitude: %s latitude: %s\n' % (pano_id, pano_date, pano_lon,
                                                                                         pano_lat)
                    panoInfoText.write(line_txt)

        panoInfoText.close()


# ------------Main Function -------------------
if __name__ == "__main__":
    import os.path

    root = '..\\kastela\\'
    inputShp = os.path.join(root, 'osm_points.shp')
    outputTxt = root + '\\metadata'

    gsv_pano_metadata_collector(inputShp, 1000, outputTxt)
