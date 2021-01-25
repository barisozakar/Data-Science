#!/usr/bin/env python
# coding: utf-8

import pandas as pd
from bokeh.layouts import row
from bokeh.models import ColumnDataSource, HoverTool, Select
from bokeh.plotting import figure, curdoc, show

# This exercise will be graded using the following Python and library versions:
###############
# Python 3.8
# Bokeh 2.2.1
# Pandas 1.1.2
###############

# read data from .csv file
df = pd.read_csv('AZA_MLE_Jul2018_utf8.csv', encoding='utf-8')
# construct list of indizes to remove unnecessary columns
cols = [1, 3]
cols.extend([i for i in range(7, 15)])
df.drop(df.columns[cols], axis=1, inplace=True)


# task 1
df.rename(columns={'Species Common Name': 'species',
                    'TaxonClass': 'taxon_class',
                    'Overall CI - lower': 'ci_lower',
                    'Overall CI - upper': 'ci_upper',
                    'Overall MLE': 'mle',
                    'Male Data Deficient': 'male_deficient',
                    'Female Data Deficient': 'female_deficient'}, 
                     inplace=True)


#I filtered the outliers here
df=df[(df["male_deficient"]!="yes") & (df["female_deficient"]!="yes")] 
df=df.drop(columns=["male_deficient","female_deficient"])


#I split the dataframe into three according to taxon class
df_mammal=df[df["taxon_class"]=="Mammalia"]
df_aves=df[df["taxon_class"]=="Aves"]
df_reptile=df[df["taxon_class"]=="Reptilia"]


#Here I sort the mammal by the 10 highest mle and reset the index
df_mammal=df_mammal.sort_values(by="mle",ascending=False)
df_mammal=df_mammal.reset_index(drop=True)
df_mammal=df_mammal.nlargest(10, "mle")
df_mammal=df_mammal.sort_values(by="mle",ascending=True)
df_mammal=df_mammal.reset_index(drop=True)

#Here I sort the aves by the 10 highest mle and reset the index
df_aves=df_aves.sort_values(by="mle",ascending=False)
df_aves=df_aves.reset_index(drop=True)
df_aves=df_aves.nlargest(10, "mle")
df_aves=df_aves.sort_values(by="mle",ascending=True)
df_aves=df_aves.reset_index(drop=True)

#Here I rename the 4th entry species to 'Penguin, Rockhopper'
df_aves.loc[5, "species"]='Penguin, Rockhopper'


#Here I sort the reptile by the 10 highest mle and reset the index
df_reptile=df_reptile.sort_values(by="mle",ascending=False)
df_reptile=df_reptile.reset_index(drop=True)
df_reptile=df_reptile.nlargest(10, "mle")
df_reptile=df_reptile.sort_values(by="mle",ascending=True)
df_reptile=df_reptile.reset_index(drop=True)


#I constructed a ColumDataSource for each of the dataframes
mammal_source=ColumnDataSource(df_mammal)
aves_source = ColumnDataSource(data=df_aves)
reptile_source= ColumnDataSource(data=df_reptile)
init_source = ColumnDataSource(data=df_mammal)

# task 2:
    
    #Here, y_ranges and x_ranges are very important, if not specified the plot will be empty
p = figure(title="Medium Life Expectancy of Animals in Zoos", 
            x_axis_label="Medium Life Expectancy (Years)", 
            y_axis_label="Species",
            y_range=init_source.data["species"].tolist(),
            x_range=[0,50.5],
            plot_width=1300, 
            plot_height=700,
            toolbar_location=None)

# Finally we add a line glyph to represent our data.
# The data can given, by referencing the column in a ColumnDataSource.
p.hbar(y="species", left="ci_lower", right="ci_upper", height=0.6, source=init_source)

#Here, I add the hover tool for ci_lower and ci_upper
hover = HoverTool()
hover.tooltips=[
('low', '@ci_lower'),
('high', '@ci_upper')]

p.add_tools(hover)

def update(attr, old, new):
    # Instead of using the new parameter, it is often better to 
    # fetch all current settings directly, especially when having multiple buttons/sliders etc.
    current_taxon = dropdown.value

    if current_taxon=="Reptilia":
        new_source=reptile_source
    elif current_taxon=="Aves":
        new_source=aves_source
    else:
        new_source=mammal_source

    init_source.data.update(new_source.data)

    #this line allows the ylabels to change accordingly, otherwise the plot looks empty
    p.y_range.factors=init_source.data["species"].tolist()

headers=["Mammalia", "Aves", "Reptilia"]

# We create the dropdown menu with the different taxons
dropdown = Select(value="Mammalia", options=headers, title="Select Taxon Class", width=100)
dropdown.on_change('value', update)

#this is similar to layout however easier to put two things in a row using this
lt=row(p, dropdown)

curdoc().add_root(lt)


