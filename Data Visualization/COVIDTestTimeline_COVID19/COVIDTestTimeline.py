#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd 
import numpy as np
import bokeh.palettes as bp
from bokeh.plotting import figure
from bokeh.io import output_file, show, save
from bokeh.models import ColumnDataSource, HoverTool, ColorBar, RangeTool
from bokeh.transform import linear_cmap
from bokeh.layouts import gridplot


# ==========================================================================
# Goal: Visualize Covid-19 Tests statistics in Switzerland with linked plots
# Dataset: covid19_tests_switzerland_bag.csv
# Data Interpretation: 
# 		n_negative: number of negative cases in tests
# 		n_positive: number of positive cases in tests
# 		n_tests: number of total tests
# 		frac_negative: fraction of POSITIVE cases in tests
# ==========================================================================


# In[14]:


### Task1: Data Preprocessing


## T1.1 Read the data to the dataframe "raw"
# You can read the latest data from the url, or use the data provided in the folder (update Nov.3, 2020)

#the original data from the link has an error, the last column should be
#frac_positive rather than frac_negative, the provided data has already correct it.)
url = 'https://raw.githubusercontent.com/daenuprobst/covid19-cases-switzerland/master/covid19_tests_switzerland_bag.csv'
raw = pd.read_csv(url, index_col="date").drop(columns="Unnamed: 0").rename(columns = {'frac_negative': 'frac_positive'})


# In[15]:


## T1.2 Create a ColumnDataSource containing: date, positive number, positive rate, total tests
# All the data can be extracted from the raw dataframe.

date = pd.to_datetime(raw.index.tolist())
pos_num = raw["n_positive"].tolist()
pos_rate = raw["frac_positive"].tolist()
test_num = raw["n_tests"].tolist()

source = ColumnDataSource(data=dict(
    date=date,
    pos_num=pos_num,
    test_num=test_num,
    pos_rate=pos_rate))


# In[16]:


## T1.3 Map the range of positive rate to a colormap using module "linear_cmap"
# "low" should be the minimum value of positive rates, and "high" should be the maximum value

mapper = linear_cmap("pos_rate", palette=bp.Magma256, low=min(pos_rate), high=max(pos_rate))


# In[17]:


### Task2: Data Visualization
# Reference link:
# (range tool example) https://docs.bokeh.org/en/latest/docs/gallery/range_tool.html?highlight=rangetool


## T2.1 Covid-19 Total Tests Scatter Plot
# x axis is the time, and y axis is the total test number. 
# Set the initial x_range to be the first 30 days.

TOOLS = "box_select,lasso_select,wheel_zoom,pan,reset,help"
p = figure(plot_width=1200, plot_height=1000, x_axis_type="datetime", x_range=(date[0], date[29]), tools="xpan")
p.scatter(x="date", y="test_num", fill_color=mapper, source=source, size=10)


# In[18]:


p.title.text = 'Covid-19 Tests in Switzerland'
p.yaxis.axis_label = "Total Tests"
p.xaxis.axis_label = "Date"
p.sizing_mode = "stretch_both"


# In[19]:


# Add a hovertool to display date, total test number
hover = HoverTool(tooltips=[
                              ("date", "@date{%Y-%m-%d}"),
                              ("test", "@test_num")],
                          formatters={
                              "@date" : "datetime"
                          })
p.add_tools(hover)


# In[20]:


## T2.2 Add a colorbar to the above scatter plot, and encode positve rate values with colors; please use the color mapper defined in T1.3 

color_bar = ColorBar(color_mapper=mapper["transform"], title="P_Rate", location=(0,0))
p.add_layout(color_bar, 'right')


# In[21]:


## T2.3 Covid-19 Positive Number Plot using RangeTool
# In this range plot, x axis is the time, and y axis is the positive test number.

select = figure(title="Drag the middle and edges of the selection box to change the range above",
                plot_height=300, plot_width=1200,
                x_axis_type="datetime",
                tools="")


# In[22]:


# Define a RangeTool to link with x_range in the scatter plot
range_tool = RangeTool(x_range=p.x_range)
range_tool.overlay.fill_color = "navy"


# In[23]:


# Draw a line plot and add the RangeTool to the plot

select.line(x="date", y="pos_num", source=source)
select.yaxis.axis_label = "Positive Cases"
select.xaxis.axis_label = "Date"
select.add_tools(range_tool)
select.toolbar.active_multi = range_tool


# In[24]:


# Add a hovertool to the range plot and display date, positive test number
hover2 = HoverTool(tooltips=[
                      ("date", "@date{%Y-%m-%d}"),
                      ("positive", "@pos_num")],
                    formatters={
                      "@date" : "datetime"
                    })
select.add_tools(hover2)


# In[25]:


## T2.4 Layout arrangement and display

linked_p = gridplot([[p],[select]])
show(linked_p)
output_file("dvc_ex3.html")
save(linked_p)

