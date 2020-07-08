def calculate_interuptions(gvi_points, shp_corridors, outshp, dist):

    import fiona
    from fiona import crs
    from shapely.geometry import shape, mapping
    from shapely.ops import substring
    from shapely.ops import transform
    from pyproj import Transformer, CRS
    from statistics import mean

    with fiona.open(gvi_points, 'r', encoding='UTF-8') as points:
        with fiona.open(shp_corridors, 'r', encoding='UTF-8') as corridors:
            wgs84 = CRS('EPSG:4326')
            pseudo_mercator = CRS('EPSG:3857')
            projection1 = Transformer.from_crs(wgs84, pseudo_mercator, always_xy=True).transform
            projection2 = Transformer.from_crs(pseudo_mercator, wgs84, always_xy=True).transform

            points_lst = []
            for point in points:
                points_lst.append([shape(point['geometry']), point['properties']['greenView']])

            corridors_lst = []
            for corridor in corridors:
                corridors_lst.append(transform(projection1, shape(corridor['geometry'])))

            shp_schema = {'geometry': 'Polygon', 'properties': {'gvi': 'float', 'greening': 'int'}}
            with fiona.open(outshp, 'w', encoding='UTF-8', schema=shp_schema, driver='ESRI Shapefile',
                            crs=crs.from_epsg(4326)) as corridor_interuptions:
                for corridor in corridors_lst:
                    buffer_gvi = []
                    min_dist = 0

                    for max_dist in range(dist, int(corridor.length)+dist, dist):
                        buffer_zone = transform(
                            projection2, substring(corridor, min_dist, max_dist).buffer(30, cap_style=2))

                        gvi_values = []
                        for point, gvi in points_lst:
                            if point.within(buffer_zone):
                                gvi_values.append(gvi)

                        if len(gvi_values) == 0:
                            min_dist += dist
                            continue
                        buffer_gvi.append([buffer_zone, mean(gvi_values)])
                        min_dist += dist

                    gvi_lst = []
                    greening = 0
                    for idx, (buffer, gvi) in enumerate(buffer_gvi):
                        new_buffer = {}
                        gvi_lst.append(gvi)
                        new_buffer['geometry'] = mapping(buffer)
                        if idx < 2:
                            new_buffer['properties'] = {'gvi': gvi, 'greening': greening}
                            corridor_interuptions.write(new_buffer)
                        else:
                            if gvi < 0.7 * mean(gvi_lst[idx-2:idx]):
                                greening = 1
                            elif gvi > 1.3 * mean(gvi_lst[idx-2:idx]):
                                greening = 0
                            new_buffer['properties'] = {'gvi': gvi, 'greening': greening}
                            corridor_interuptions.write(new_buffer)


if __name__ == "__main__":
    import os.path

    dist = 25
    root = '..\\kastela'
    inshp_gvi_points = os.path.join(root, 'GVI_points_clean.shp')
    inshp_corridors = os.path.join(root, 'main_streets.shp')
    outshp = os.path.join(root, 'corridor_interuptions.shp')
    calculate_interuptions(inshp_gvi_points, inshp_corridors, outshp, dist)
