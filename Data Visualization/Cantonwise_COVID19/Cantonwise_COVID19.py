#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd 
from math import pi
import numpy as np
from bokeh.io import output_file, show, save
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, HoverTool,FactorRange
import bokeh.palettes as bp
 
# Goal: Draw a line chart displaying averaged daily new cases for all cantons in Switzerland.
# Dataset: covid19_cases_switzerland_openzh-phase2.csv
# Interpretation: value on row i, column j is either the cumulative covid-19 case number of canton j on date i or null value


# In[2]:


### Task 1: Data Preprocessing


## T1.1 Read data into a dataframe, set column "Date" to be the index 

url = 'https://raw.githubusercontent.com/daenuprobst/covid19-cases-switzerland/master/covid19_cases_switzerland_openzh-phase2.csv'
raw = pd.read_csv(url, index_col="Date", usecols=range(0,28))

# Initialize the first row with zeros, and remove the last column 'CH' from dataframe
raw.loc[raw.index[0]]=0
raw = raw.drop(columns="CH")


# Fill null with the value of previous date from same canton
# https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.fillna.html
df=raw.fillna(method="ffill")


# In[3]:


## T1.2 Calculate and smooth daily case changes

# Compute daily new cases (dnc) for each canton, e.g. new case on Tuesday = case on Tuesday - case on Monday;
# Fill null with zeros as well
dnc = df.diff(axis=0, periods=1)
dnc = dnc.fillna(value=0)

# Smooth daily new case by the average value in a rolling window, and the window size is defined by step
# Why do we need smoothing? How does the window size affect the result?
# https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.rolling.html
step = 3
dnc_avg = dnc.rolling(window=step).mean().fillna(0)


# In[4]:


## T1.3 Build a ColumnDataSource 

# Extract all canton names and dates
# NOTE: be careful with the format of date when it is used as x input for a plot
cantons = df.columns
date = df.index.values


# Create a color list to represent different cantons in the plot, you can either construct your own color patette or use the Bokeh color pallete
color_palette = bp.plasma(26)

# Build a dictionary with date and each canton name as a key, i.e., {'date':[], 'AG':[], ..., 'ZH':[]}
# For each canton, the value is a list containing the averaged daily new cases
source_dict={}
for canton in cantons:
    source_dict[canton]=dnc_avg[canton].values
source_dict["date"]=date

#Here I change the date values to be processed as datetime objects
source_dict["date"]=pd.to_datetime(source_dict['date'])


# In[5]:


### Task 2: Data Visualization

## T2.1: Draw a group of lines, each line represents a canton, using date, dnc_avg as x,y. Add proper legend.
# https://docs.bokeh.org/en/latest/docs/reference/models/glyphs/line.html?highlight=line#bokeh.models.glyphs.Line
# https://docs.bokeh.org/en/latest/docs/user_guide/interaction/legends.html
## T2.2 Add hovering tooltips to display date, canton and averaged daily new case

p = figure(plot_width=1000, plot_height=800, x_axis_type="datetime")
p.title.text = 'Daily New Cases in Switzerland'

source = ColumnDataSource(data=source_dict)

#Here I am plotting the lines using each canton, color pair with the corresponding case number, also including hover tooltips
for canton,color in zip(cantons, color_palette): 
    canton_name=str(canton)
    renderer=p.line(x="date", y=canton_name, color= color, line_width=2, alpha=0.8, legend_label=canton, source=source)
    p.add_tools(HoverTool(renderers=[renderer],
                          tooltips=[
                              ("date", "@date{%Y-%m-%d}"),
                              ("canton", canton),
                              ("cases", "@"+canton_name+"{int}")],
                          formatters={
                              "@date" : "datetime"
                          }
                          ))
# Make the legend of the plot clickable, and set the click_policy to be "hide"
p.legend.location = "top_left"
p.legend.click_policy="hide"


# In[6]:


#Here I am displaying the plot and saving it as a file.
show(p)
output_file("dvc_ex2.html")
save(p)

