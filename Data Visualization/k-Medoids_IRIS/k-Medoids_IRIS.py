#!/usr/bin/env python
# coding: utf-8


import numpy as np
from bokeh.models import ColumnDataSource, Button, Select, Div
from bokeh.sampledata.iris import flowers
from bokeh.plotting import figure, curdoc, show
from bokeh.layouts import column, row

# Important: You must also install pandas for the data import.


#This implementation uses array computations and no for loop takes 3.96ms
# calculate the cost of the current medoid configuration
# The cost is the sum of all minimal distances of all points to the closest medoids
#1) The distance of a data point to a medoid is the sum of the absolute differences between the parameters petal length, petal width, sepal length and sepal width. This is also called the Manhattan distance.
#2) The cost of a single data point is the minimum of its distances to all medoids.
#3) The cost of the clustering is the sum of the costs of all data points i.e. the sum of all minimal distances of data points to their closest medoid.
def get_cost(meds):
    desired_columns=["sepal_length","sepal_width","petal_length","petal_width"]
    all_data=np.array(data.loc[:,desired_columns])
    all_data_new=all_data[:, np.newaxis]
    data_meds=np.array(data.loc[meds,desired_columns])
    total_cost=np.sum(np.min(np.sum(abs(all_data_new-data_meds), axis=2), axis=1))
    return total_cost


def change_colors(meds):
    desired_columns=["sepal_length","sepal_width","petal_length","petal_width"]
    data_meds=data.loc[meds, desired_columns]
    red="#E74C3C"
    green="#58D68D"
    blue="#3498DB"
    colors=[red, green, blue]
    for i in range(len(data)):
        row=data.loc[i, desired_columns]
        row_costs=np.sum(abs(row-data_meds), axis=1)
        data.loc[i,"color"]=colors[np.argmin(np.array(row_costs))]


# implement the k-medoids algorithm in this function and hook it to the callback of the button in the dashboard
# check the value of the select widget and use random medoids if it is set to true and use the pre-defined medoids
# if it is set to false.
def k_medoids():
    # number of clusters:
    k = 3
    # Use the following medoids if random medoid is set to false in the dashboard. These numbers are indices into the
    # data array.
    isRandom=dropdown.value
    if isRandom=="True":
        medoids=[]
        for i in range(3):
            while(True):
                r=np.random.randint(len(data))
                if r not in medoids: 
                    medoids.append(r)
                    break
    else:
        medoids = [24, 74, 124]
    m_array=[]
    p_array=[]
    cost_array=[]
    print("starting medoids: %s" % str(medoids))
    while(True):
        nonmedoids=[i for i in range(150) if i not in medoids]
        current_cost=get_cost(medoids)
        for medoid in medoids:
            for nonmedoid in nonmedoids:
                new_medoids=[x for x in medoids if x!=medoid]+[nonmedoid]
                new_cost=get_cost(new_medoids)
                if (new_cost<current_cost):
                    m_array.append(medoid) 
                    p_array.append(nonmedoid)
                    cost_array.append(new_cost)
        if(len(cost_array)>0):
            best_index=np.argmin(cost_array)
            best_m=m_array[best_index]
            best_p=p_array[best_index]
            print("swapping medoids, new lowest cost= %f" % cost_array[best_index])
            medoids=[x for x in medoids if x!=best_m]+[best_p]
            m_array=[]
            p_array=[]
            cost_array=[]
        else:
            break
    print("Minimum found")
    print("Clustering completed")
    print("Final medoids: %s" % str(medoids))
    final_cost=get_cost(medoids)
    print("Final cost: %f" % final_cost)
    return final_cost, medoids


# read and store the dataset
data = flowers.copy(deep=True)
data = data.drop(['species'], axis=1)

# create a color column in your dataframe and set it to gray on startup
data.loc[:, "color"]="#808B96"


# Create a ColumnDataSource from the data
source=ColumnDataSource(data)


# Create a select widget, a button, a DIV to show the final clustering cost and two figures for the scatter plots.

#Here, y_ranges and x_ranges are very important, if not specified the plot will be empty
p1 = figure(title="Scatterplot of flower distribution by petal length and sepal length", 
            x_axis_label="Petal length", 
            y_axis_label="Sepal length",
            plot_width=600, 
            plot_height=600)

# Finally we add a line glyph to represent our data.
# The data can given, by referencing the column in a ColumnDataSource.
p1.scatter(x="petal_length", y="sepal_length", fill_color="color", radius=0.04, fill_alpha=0.6, line_color=None, source=source)

p2 = figure(title="Scatterplot of flower distribution by petal width and petal length", 
            x_axis_label="Petal width", 
            y_axis_label="Petal length",
            plot_width=600, 
            plot_height=600)

p2.scatter(x="petal_width", y="petal_length", fill_color="color", radius=0.017,fill_alpha=0.6, line_color=None, source=source)


def change_click():    
    final_cost, medoids=k_medoids()
    div.text= "The final cost is: " + str(final_cost)
    change_colors(medoids)
    source.data["color"]=np.array(data["color"])
    
headers=["False", "True"]

# We create the dropdown menu with the different taxons
dropdown = Select(value="False", options=headers, title="Random Medoids", width=200)

bt = Button(label='Cluster data', width=200)
bt.on_click(change_click)

div=Div(text="")

#     #this is similar to layout however easier to put two things in a row using this
#     lt=row(p, dropdown)
lt=row(column(dropdown, bt, div), p1, p2)
curdoc().add_root(lt)


# use curdoc to add your widgets to the document
#curdoc().add_root(...)
curdoc().title = "DVA_ex_3"