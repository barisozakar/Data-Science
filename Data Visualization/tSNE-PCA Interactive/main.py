# -*- coding: utf-8 -*-
import glob
import os
import numpy as np
from PIL import Image

from sklearn.manifold import TSNE
from sklearn.decomposition import PCA

from bokeh.plotting import figure, curdoc
from bokeh.models import ColumnDataSource
from bokeh.layouts import layout

# Dependencies
# Make sure to install the additional dependencies noted in the requirements.txt using the following command:
# pip install -r requirements.txt

# You might want to implement a helper function for the update function below or you can do all the calculations in the
# update callback function.

# Only do this once you've followed the rest of the instructions below and you actually reach the part where you have to
# configure the callback of the lasso select tool. The ColumnDataSource containing the data from the dimensionality
# reduction has an on_change callback routine that is triggered when certain parts of it are selected with the lasso
# tool. More specifically, a ColumnDataSource has a property named selected, which has an on_change routine that can be
# set to react to its "indices" attribute and will call a user defined callback function. Connect the on_change routine
# to the "indices" attribute and an update function you implement here. (This is similar to the last exercise but this
# time we use the on_change function of the "selected" attribute of the ColumnDataSource instead of the on_change
# function of the select widget).
# In simpler terms, each time you select a subset of image glyphs with the lasso tool, you want to adjust the source
# of the channel histogram plot based on this selection.
# Useful information:
# https://docs.bokeh.org/en/latest/docs/reference/models/sources.html
# https://docs.bokeh.org/en/latest/docs/reference/models/tools.html
# https://docs.bokeh.org/en/latest/docs/reference/models/selections.html#bokeh.models.selections.Selection


# Fetch the number of images using glob or some other path analyzer
N = len(glob.glob("static/*.jpg"))

# Find the root directory of your app to generate the image URL for the bokeh server
ROOT = os.path.split(os.path.abspath("."))[1] + "/"

# Number of bins per color for the 3D color histograms
N_BINS_COLOR = 16
# Number of bins per channel for the channel histograms
N_BINS_CHANNEL = 50

# Define an array containing the 3D color histograms. We have one histogram per image each having N_BINS_COLOR^3 bins.
# i.e. an N * N_BINS_COLOR^3 array
color_histograms=np.zeros((N, N_BINS_COLOR**3))

# Define an array containing the channel histograms, there is one per image each having 3 channel and N_BINS_CHANNEL
# bins i.e an N x 3 x N_BINS_CHANNEL array
channel_histograms=np.zeros((N, 3, N_BINS_CHANNEL))

# initialize an empty list for the image file paths
image_paths=[]


# Compute the color and channel histograms
for idx, f in enumerate(glob.glob("static/*.jpg")):
    # open image using PILs Image package
    image = Image.open(f)
    
    # Convert the image into a numpy array and reshape it such that we have an array with the dimensions (N_Pixel, 3)
    image_array=np.asarray(image);
    image_array=np.reshape(image_array, (image_array.shape[0]*image_array.shape[1],3))
    
    
    # Compute a multi dimensional histogram for the pixels, which returns a cube
    # reference: https://numpy.org/doc/stable/reference/generated/numpy.histogramdd.html
    multi_histogram, edges=np.histogramdd(image_array, bins=(N_BINS_COLOR, N_BINS_COLOR, N_BINS_COLOR))

    # However, later used methods do not accept multi dimensional arrays, so reshape it to only have columns and rows
    # (N_Images, N_BINS^3) and add it to the color_histograms array you defined earlier
    # reference: https://numpy.org/doc/stable/reference/generated/numpy.reshape.html
#     color_histograms.append(multi_histogram)
    multi_histogram=np.reshape(multi_histogram, (1,N_BINS_COLOR**3))
    color_histograms[idx]=multi_histogram

    # Append the image url to the list for the server
    url = ROOT + f

    # Compute a "normal" histogram for each color channel (rgb)
    # reference: https://numpy.org/doc/stable/reference/generated/numpy.histogram.html
    red_hist, red_edges=np.histogram(image_array[:,0], bins=N_BINS_CHANNEL)
    green_hist, green_edges=np.histogram(image_array[:,1], bins=N_BINS_CHANNEL)
    blue_hist, blue_edges=np.histogram(image_array[:,2], bins=N_BINS_CHANNEL)

    # and add them to the channel_histograms
    channel_histograms[idx, 0, :]=red_hist
    channel_histograms[idx, 1, :]=green_hist
    channel_histograms[idx, 2, :]=blue_hist
    
    image_paths.append(url)

# Calculate the indicated dimensionality reductions
# references:
# https://scikit-learn.org/stable/modules/generated/sklearn.manifold.TSNE.html
# https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.PCA.html
color_tsne = TSNE(n_components=2, random_state=7).fit_transform(color_histograms)
color_pca = PCA(n_components=2, random_state=7).fit_transform(color_histograms)

# Construct a data source containing the dimensional reduction result for both the t-SNE and the PCA and the image paths
color_source = ColumnDataSource(dict(
        tsne_x = color_tsne[:, 0],
        tsne_y = color_tsne[:, 1],
        pca_x = color_pca[:,0],
        pca_y = color_pca[:,1],
        paths = image_paths)) 

# Create a first figure for the t-SNE data. Add the lasso_select, wheel_zoom, pan and reset tools to it.

tsne_plot = figure(plot_width=500, plot_height=400, tools=['lasso_select', 'wheel_zoom', 'pan', 'reset'])
tsne_plot.title.text = 'tSNE'
tsne_plot.image_url(url="paths", x="tsne_x", y="tsne_y", h=1, w=1.5 ,source=color_source, anchor="center")
tsne_plot.circle(x="tsne_x", y="tsne_y", source=color_source, fill_alpha=0, line_alpha=0)
tsne_plot.xaxis.axis_label = 'x'
tsne_plot.yaxis.axis_label = 'y'

# And use bokehs image_url to plot the images as glyphs
# reference: https://docs.bokeh.org/en/latest/docs/reference/models/glyphs/image_url.html

# Since the lasso tool isn't working with the image_url glyph you have to add a second renderer (for example a circle
# glyph) and set it to be completely transparent. If you use the same source for this renderer and the image_url,
# the selection will also be reflected in the image_url source and the circle plot will be completely invisible.


# Create a second plot for the PCA result. As before, you need a second glyph renderer for the lasso tool.
# Add the same tools as in figure 1
pca_plot = figure(plot_width=500, plot_height=400, tools=['lasso_select', 'wheel_zoom', 'pan', 'reset'])
pca_plot.title.text = 'PCA'
pca_plot.image_url(url="paths", x="pca_x", y="pca_y", h=8000, w=10000 ,source=color_source, anchor="center")
pca_plot.circle(x="pca_x", y="pca_y", source=color_source, fill_alpha=0, line_alpha=0)
pca_plot.xaxis.axis_label = 'x'
pca_plot.yaxis.axis_label = 'y'

# Construct a datasource containing the channel histogram data. Default value should be the selection of all images.
# Think about how you aggregate the histogram data of all images to construct this data source
aggregation=channel_histograms.sum(axis=0)
red=aggregation[0]
green=aggregation[1]
blue=aggregation[2]

# Construct a datasource containing the channel histogram data. Default value should be the selection of all images.
# Think about how you aggregate the histogram data of all images to construct this data source
channel_source=ColumnDataSource(dict(
                                bins=[i for i in range(0,50)],
                                red=red,
                                green=green,
                                blue=blue))
                                
# Construct a histogram plot with three lines.
# First define a figure and then make three line plots on it, one for each color channel.
# Add the wheel_zoom, pan and reset tools to it.
channel_hist_plot= figure(plot_width=500, plot_height=400, tools=['wheel_zoom', 'pan', 'reset'])
channel_hist_plot.title.text = 'Channel Histogram'
channel_hist_plot.line(x="bins", y="red", source=channel_source, line_color="red")
channel_hist_plot.line(x="bins", y="green", source=channel_source, line_color="green")
channel_hist_plot.line(x="bins", y="blue", source=channel_source, line_color="blue")
channel_hist_plot.xaxis.axis_label = 'bin'
channel_hist_plot.yaxis.axis_label = 'Frequency'

# Connect the on_change routine of the selected attribute of the dimensionality reduction ColumnDataSource with a
# callback/update function to recompute the channel histogram. Also read the topmost comment for more information.
def update(attr, old, new):
    selected_rows = new

    # we don't want to do anything if nothing is selected 
    if len(selected_rows) == 0:
        aggregation=channel_histograms.sum(axis=0)
    else:
    	aggregation=channel_histograms[selected_rows].sum(axis=0)
    
    red=aggregation[0]
    green=aggregation[1]
    blue=aggregation[2]
    
    channel_source.data = dict(
        bins=[i for i in range(0,50)],
        red=red,
        green=green,
        blue=blue)
    
# Construct a layout and use curdoc() to add it to your document.

color_source.selected.on_change("indices", update)
lt=layout([[tsne_plot, pca_plot, channel_hist_plot]])

curdoc().add_root(lt)

# You can use the command below in the folder of your python file to start a bokeh directory app.
# Be aware that your python file must be named main.py and that your images have to be in a subfolder name "static"

# bokeh serve --show .
# python -m bokeh serve --show .

# dev option:
# bokeh serve --dev --show .
# python -m bokeh serve --dev --show .
