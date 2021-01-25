#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd 
from math import pi
from bokeh.io import output_file, show, save
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, HoverTool,FactorRange,CustomJS
import bokeh.palettes as bp # uncomment it if you need special colors that are pre-defined

 
### Task 1: Data Preprocessing
 

## T1.1 Read online .csv file into a dataframe using pandas
# Reference links: 
# https://pandas.pydata.org/pandas-docs/stable/reference/frame.html
# https://stackoverflow.com/questions/55240330/how-to-read-csv-file-from-github-using-pandas 

original_url = 'https://raw.githubusercontent.com/daenuprobst/covid19-cases-switzerland/master/demographics_switzerland_bag.csv'
df = pd.read_csv(original_url)
print(df.tail())



# In[2]:


## T1.2 Prepare data for a grouped vbar_stack plot
# Reference link, read first before starting: 
# https://docs.bokeh.org/en/latest/docs/user_guide/categorical.html#stacked-and-grouped


# Filter out rows containing 'CH' 
df = df[df["canton"]!="CH"]
print(df.tail())


# In[3]:


# Extract unique value lists of canton, age_group and sex
canton = set((df["canton"].tolist()))
print(canton)
age_group = set((df["age_group"].tolist()))
print(age_group)
sex = set((df["sex"].tolist()))
print(sex)


# In[4]:


# Create a list of categories in the form of [(canton1,age_group1), (canton2,age_group2), ...]
import numpy as np
factors = [tuple(i) for i in np.unique(df[["canton", "age_group"]].get_values().tolist(), axis=0)]

# Use genders as stack names
stacks = ['male','female']

# Calculate total population size as the value for each stack identified by canton,age_group and sex
stack_val = df.groupby(["canton", "age_group", "sex"]).sum()["pop_size"]

# Build a ColumnDataSource using above information
source = ColumnDataSource(data=dict(
    x=factors,
    male=df[df["sex"]=="Männlich"].groupby(["canton", "age_group"]).sum()["pop_size"].tolist(),
    female=df[df["sex"]=="Weiblich"].groupby(["canton", "age_group"]).sum()["pop_size"].tolist()
))


# In[5]:



### Task 2: Data Visualization


## T2.1: Visualize the data using bokeh plot functions
p=figure(x_range=FactorRange(*factors), plot_height=500, plot_width=800, title='Canton Population Visualization')
p.yaxis.axis_label = "Population Size"
p.xaxis.axis_label = "Canton"
p.sizing_mode = "stretch_both"
p.xgrid.grid_line_color = None
p.xaxis.major_label_orientation = "vertical"
p.xaxis.major_label_text_font_size="5pt"

#create a vertical bar graph
renderers = p.vbar_stack(stacks, x="x",  width=0.6, alpha=0.5, color=["lightgreen", "blue"], source=source, name=stacks, legend_label=stacks)
p.legend.location = "top_left"


# In[6]:



## T2.2 Add the hovering tooltips to the plot using HoverTool
# To be specific, the hover tooltips should display “gender”, canton, age group”, and “population” when hovering.
# https://docs.bokeh.org/en/latest/docs/user_guide/tools.html#hovertool
# read more if you want to create fancy hover text: https://stackoverflow.com/questions/58716812/conditional-tooltip-bokeh-stacked-chart

for r in renderers:
    population = r.name
    hover = HoverTool(tooltips=[
        ('gender', "$name"),
        ('canton', "@x"),
        ('population', "@%s" % population),
        
    ], renderers=[r])
    p.add_tools(hover)

show(p)



# In[7]:


## T2.3 Save the plot as "dvc_ex1.html" using output_file
output_file('dvc_ex1.html', mode='inline')
save(p)

