# Treepedia
## Sustainable Societies, CHP@UCI

<hr>

### About this project 
Sustainable Socieites is a six-quarter course sequence dedicated to an interdisciplinary exploration of sustainability. For our capstone project, we are comparing urban greenspace in Santa Ana, CA, and Long Beach, CA, and we hope to correlate differences in greenspace to health and economic impacts in the two cities. 

To investigate greenspace, we will be looking at 1) policy, 2) parkscore, and 3) urban tree canopy cover. And this repo contains the code that performs these calculations using Google streetview images, as well as preliminary results. 

<hr>

### Technical modifications to original
The original Treepedia code has been modified in the following ways:
<ul>
  <li>Python 2.7 -> Python 3.5</li>
  <li>Instead of Ostu's method from pymeanshift, used [Felzenszwaib](https://scikit-image.org/docs/dev/api/skimage.segmentation.html?highlight=felzenszwalb#skimage.segmentation.felzenszwalb) (which uses MST clustering) from SciKit to segment streetview images</li>
  <li>Make box-plots of result GVI</li>
</ul>

Our Santa Ana boundary & street shape files came from: http://gis-santa-ana.opendata.arcgis.com/search?tags=transportation

Our Long Beach boundary & street shape files came from: http://datalb.longbeach.gov/datasets/0cabfa8dcd7a4aebb4cbfaece861697b_2
(Note: that needs to be converted to ERSI WGS84, which you can do with QGIS)

### Findings and conclusions
<p align="center">
  <img width="460" height="300" src="https://github.com/the-rango/Treepedia_Public/images/master/Comp_nofrwy.png">
  A box-plot of GVI distributions
</p>
<div>
  <div style="float: left; width: 50%; padding: 5px;">
  <img style="width:100%" src="https://github.com/the-rango/Treepedia_Public/SA/SA_GVR.png">
    <p>Santa Ana</p>
</div>
  
<div>
  <div style="float: left; width: 50%; padding: 5px;">
  <img style="width:100%" src="https://github.com/the-rango/Treepedia_Public/LB/LB_GVR_nofrwy.png">
    <p>Santa Ana</p>
</div>

#### Discussion and insights
Under construction!! Will update soon with all the things we learned about getting the data and removing freeways...

<hr>

### Treepedia's original readme:
Developed by the MIT [Senseable City Lab](https://senseable.mit.edu/), *Treepedia* aims to raise a proactive awareness of urban vegetation improvement, using computer vision techniques applied to Google Street View images. Our focus is on street trees: Treepedia doesn't map parks, as GSV doesn't venture into them as it does on average streets.

*Treepedia* measures and maps the amount of vegetation cover along a city's streets by computing the Green View Index (GVI) on Google Street View (GSV) panoramas. This method considers the obstruction of tree canopies and classifies the images accordingly. The GVI presented here is on a scale of 0-100, showing the percentage of canopy coverage of a particular location. Explore the maps on the [*Treepedia*](http://senseable.mit.edu/treepedia/) website to see how the GVI changes across a city, and how it compares across cities and continents.

The following repo provides a <a href="https://github.mit.edu/abdulhai/Treepedia/wiki/Analyze-Your-City"> library to implement the GVI computation</a> for a city or region defined by a boundary shapefile, given that GSV imagery is available for the street network within it. It also includes documentation of the workflow of the project so that stakeholders, municipalities, researchers or public alike may run the analysis for their cities. We will continue to grow the *Treepedia* database to span cities all over the globe. What does your green canopy look like? If you'd like to answer this question please install this python library and run the analysis for your area. 

If you are a government, researcher or stakeholder that has used this library to compute the GVI for your city and would like us to include a mapping of it on the *Treepedia* website, please contact us at: senseable-trees@mit.edu

<br />

<p align="center">
  <img width="460" height="300" src="https://github.com/ianseifs/Treepedia_Public/blob/master/img.jpg">
</p>

#### Workflow 

The project has the following workflow:

##### Step 1: Point Sampling on Street Network of City 
With the street network and boundary shapefile for your city as input, a shapefile containing points every 20m (which can be changed depending on the size of the city) will be generated to be fed into the Google API to retrieve Google Street View Images. 

<p align="center">
  <img width="460" height="300" src="https://github.com/ianseifs/Treepedia_Public/blob/master/images/img2.jpg">
</p>

<p align="center">
  <img width="460" height="300" src="https://github.com/ianseifs/Treepedia_Public/blob/master/images/img1.jpg">
</p>

Note that spatial files must be in the projected WGS84 system.

Example:
You can just run the code of "createPoints.py" [here](https://github.com/ianseifs/Treepedia_Public/blob/master/Treepedia/createPoints.py)

python createPoints.py

In the example, I use Cambridge as example. At the buttom of the code, you can specify the input shapefile of the street map, the minimum distance for sampling, and the number of the output shapefile for your cities.



##### Step 2: Metadata containing GSV panoID's

With the shapefile as input, metadata containing the panoID, panoDate, latitude, longitude and tilt specifications for the image will be stored in textfiles to be later used to calculate the Green View Index. 

<p align="center">
  <img width="460" height="300" src="https://github.com/ianseifs/Treepedia_Public/blob/master/images/img3.jpg">
</p>

Example:
You can just run the code of "metadataCollector.py" [here](https://github.com/ianseifs/Treepedia_Public/blob/master/Treepedia/metadataCollector.py)

python metadataCollector.py

The input of this code is created sample site shapefile. In the example, I use Cambridge20m.shp in the sample-spatialdata folder. You can generate your own sample sites based on the createPnt.py. At the buttom of the code, you can specify different sample site file. The batch size is 1000, which means the code will save metadata of every 1000 point to a txt file.



##### Step 3: GVI Calculation of points with final shapefile display 
Using Otsu's method and the pymeanshift package, the Green View Index is computed for all 6 images at each sampling point; for each sampling point the GVI values are then averaged to provide a single GVI value for every point along the street network. Finally, a shapefile will be generated containing all attributes, including the GVI, of the points on the street network. 

<p align="center">
  <img width="460" height="300" src="https://github.com/ianseifs/Treepedia_Public/blob/master/images/img4.jpg">
</p>

Example:

You can just run the code of "GreenView_Calculate.py" [here](https://github.com/ianseifs/Treepedia_Public/blob/master/Treepedia/GreenView_Calculate.py)

python GreenView_Calculate.py

The input of this code is the collected metadata of GSV. By reading the metadat, this code will collect GSV images and segmente the greenery, and calculate the green view index. Considering those GSV images captured in winter are leafless, thiwh are not suitable for the analysis. You also need to specific the green season, for example, in Cambridge, the green months are May, June, July, August, and September.

You can open several process to run this code simutaniously, because the output will be saved as txt files in folder. If the output txt file is already there, then the code will move to the next metadata txt file and generate the GVI for next 1000 points.

After finishing the computing, you can run the code of "Greenview2Shp.py" [here](https://github.com/ianseifs/Treepedia_Public/blob/master/Treepedia/Greenview2Shp.py), and save the result as shapefile, if you are more comfortable with shapefile.


### Contributors
Project Co-Leads: Xiaojiang Li and Ian Seiferling

Researchers: Bill Cai, Marwa Abdulhai

Website and Visualization: Wonyoung So
