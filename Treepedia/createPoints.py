# This program is used in the first step of the Treepedia project to get points along street
# network to feed into GSV python scripts for metadata generation.
# Copyright(C) Ian Seiferling, Xiaojiang Li, Marwa Abdulhai, Senseable City Lab, MIT
# First version July 21 2017


# now run the python file: createPoints.py, the input shapefile has to be in projection of WGS84, 4326
def create_points(inshp, outshp, mini_dist):

    """
    This function will parse through the street network of provided city and
    clean all highways and create points every mini_dist meters (or as specified) along
    the linestrings
    Required modules: Fiona and Shapely

    parameters:
        inshp: the input linear shapefile, must be in WGS84 projection, ESPG: 4326
        output: the result point feature class
        mini_dist: the minimum distance between two created point

    last modified by Xiaojiang Li, MIT Senseable City Lab
    """

    import fiona
    import os.path
    from shapely.geometry import shape, mapping
    from shapely.ops import transform
    from pyproj import Transformer
    from fiona.crs import from_epsg

    s = {'trunk_link', 'tertiary', 'motorway', 'motorway_link', 'steps', None, ' ', 'pedestrian', 'primary',
         'primary_link', 'footway', 'tertiary_link', 'trunk', 'secondary', 'secondary_link', 'tertiary_link',
         'bridleway', 'service'
         }

    # the temporary file of the cleaned data
    root_dir = os.path.dirname(inshp)
    basename = 'clean_' + os.path.basename(inshp)
    temp_cleaned_streetmap = os.path.join(root_dir, basename)

    # if the tempfile exist then delete it
    if os.path.exists(temp_cleaned_streetmap):
        fiona.remove(temp_cleaned_streetmap, 'ESRI Shapefile')

    # clean the original street maps by removing highways, if it the street map not from Open street data, users'd
    # better to clean the data themselves
    with fiona.open(inshp) as source, fiona.open(temp_cleaned_streetmap, 'w', driver=source.driver,
                                                 crs=source.crs, schema=source.schema) as dest:

        for feat in source:
            try:
                i = feat['properties']['highway']  # for the OSM street data
                if i in s:
                    continue
            except:
                # if the street map is not osm, do nothing. You'd better to clean the street map, if you don't want
                # to map the GVI for highways
                # get the field of the input shapefile and duplicate the input feature
                key = list(dest.schema['properties'].keys())[0]
                i = feat['properties'][key]
                if i in s:
                    continue

            dest.write(feat)

    schema = {
        'geometry': 'Point',
        'properties': {'id': 'int'},
    }

    # Create points along the streets
    with fiona.Env():
        # with fiona.open(outshp, 'w', 'ESRI Shapefile', crs=source.crs, schema) as output:
        with fiona.open(outshp, 'w', crs=from_epsg(4326), driver='ESRI Shapefile', schema=schema) as output:
            transformation1 = Transformer.from_crs('EPSG:4326', 'EPSG:3857', always_xy=True).transform
            transformation2 = Transformer.from_crs('EPSG:3857', 'EPSG:4326', always_xy=True).transform
            for line in fiona.open(temp_cleaned_streetmap):
                first = shape(line['geometry'])

                try:
                    # convert degree to meter, in order to split by distance in meter
                    # EPSG:3857 is pseudo WGS84 the unit is meter
                    line2 = transform(transformation1, first)
                    # print(line2.coords)
                    # linestr = list(line2.coords)
                    dist = mini_dist  # set
                    for distance in range(0, int(line2.length), dist):
                        point = line2.interpolate(distance)

                        # convert the local projection back to the WGS84 and write to the output shp
                        point = transform(transformation2, point)
                        output.write({'geometry': mapping(point), 'properties': {'id': 1}})
                except:
                    print("You should make sure the input shapefile is WGS84")
                    raise

    print("Process Complete")

    # delete the temporary cleaned shapefile
    fiona.remove(temp_cleaned_streetmap, 'ESRI Shapefile')


# Example to use the code,
# Note: make sure the input linear featureclass (shapefile) is in WGS 84 or ESPG: 4326
# ------------main ----------
if __name__ == "__main__":
    import os.path

    root = '..\\kastela'
    inshp = os.path.join(root, 'streets_wgs84.shp')
    outshp = os.path.join(root, 'osm_points.shp')
    mini_dist = 20  # the minimum distance between two generated points in meter
    create_points(inshp, outshp, mini_dist)
