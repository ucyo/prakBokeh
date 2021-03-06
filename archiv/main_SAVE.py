#!/usr/bin/python
from bokeh.layouts import layout, widgetbox
from bokeh.models import ColumnDataSource, Div
from bokeh.models.widgets import TextInput
from bokeh.io import curdoc
#import geoviews

import bokeh as bokeh
import pandas as pd
import xarray as xr
import holoviews as hv
import numpy as np

from cartopy import crs

from holoviews.operation.datashader import datashade, rasterize



import math

renderer = hv.renderer('bokeh').instance(mode='server',size=300)

START = 0
LOADINGMETA = 1
LOADEDMETA = 2
LOADING = 3
LOADED = 4
ERROR = 1000

state = START

urlinput = TextInput(value="default", title="netCFD/OpenDAP Source URL:")
slVar = None
slMesh = None
slHeight = None
slCMap = None
variable = ""
height = 0
n = None
n4 = None
tris = None
verts = None

freedims = []

COLORMAPS = ["Inferno","Magma","Plasma","Viridis","BrBG","PiYG","PRGn","PuOr","RdBu","RdGy","RdYlBu","RdYlGn","Spectral","Blues","BuGn","BuPu","GnBu","Greens","Greys","Oranges","OrRd","PuBu","PuBuGn","PuRd","Purples","RdPu","Reds","YlGn","YlGnBu","YlOrBr","YlOrRd"]

def getURL():
    #url = urlinput.value
    url = "/home/max/Downloads/2016033000-ART-passive_grid_pmn_DOM01_ML_0002.nc"
    return url

def graph():
    for d in getattr(xrData,variable).dims:
        # WORKAROUND because Holoview is not working with a kdim with name "height"
        # See issue
        if d == "height":
            freedims.append("hi")
            continue
        if d != "ncells":
            freedims.append(d)

    ranges = {}
    for d in freedims:
        # WORKAROUND because Holoview is not working with a kdim with name "height"
        # See issue
        if d != "hi":
            ranges[d] = (0,len(getattr(getattr(xrData,variable),d)))
        else:
            ranges[d] = (0,len(getattr(getattr(xrData,variable),"height")))
    dm = hv.DynamicMap(triGraph, kdims=freedims).redim.range(**ranges)
    print("DynamicMap:" + str(dm))
    cm = "Magma"
    if slCMap is not None:
        cm = slCMap.value
    return rasterize(dm).opts(cmap=cm,colorbar=True)
    #return datashade(dm)


def triGraph(*args):
    global n, n4, tris, xrData, verts, variable, freedims

    n1 = []
    n2 = []
    n3 = []

    selectors = {}
    idx = 0
    for d in freedims:
        # WORKAROUND because Holoview is not working with a kdim with name "height"
        # See issue
        if d == "hi":
            selectors["height"] = args[idx]
        else:
            selectors[d] = args[idx]
        idx = idx +1

    if n is None:
        xrData = xr.open_dataset(getURL(),decode_cf=False)
        verts = np.column_stack((xrData.clon_bnds.stack(z=('vertices','ncells')),xrData.clat_bnds.stack(z=('vertices','ncells'))))

        #not so performant
        f = 180 / math.pi
        for v in verts:
            v[0] = v[0] * f
            v[1] = v[1] * f

        l = len(xrData.clon_bnds)

        n1 = np.arange(l)
        n2 = n1 + l
        n3 = n2 + l

        n4 = np.column_stack((n1,n2,n3))
        n = np.column_stack((n4,getattr(xrData, variable).isel(selectors)))

        verts = pd.DataFrame(verts,  columns=['Longitude', 'Latitude'])
        tris  = pd.DataFrame(n, columns=['v0', 'v1', 'v2',"var"], dtype = np.float64)
        tris['v0'] = tris["v0"].astype(np.int32)
        tris['v1'] = tris["v1"].astype(np.int32)
        tris['v2'] = tris["v2"].astype(np.int32)
    else:
        tris["var"] = getattr(xrData, variable).isel(selectors)

    print('vertices:', len(verts), 'triangles:', len(tris))

    res = hv.TriMesh((tris,verts), label=(variable)).options(filled=True)
    return res

def loadMetaCallback():
    global slVar, slMesh, xrData
    state = LOADINGMETA

    divLoading = Div(text="loading metadata...")
    curdoc().clear()
    l = layout([
    [widgetbox(divLoading)]
    ])
    curdoc().add_root(l)

    try:
        xrData = xr.open_dataset(getURL(),decode_cf=False)
    except:
        divError = Div(text="Failed to load metadata")
        curdoc().clear()
        l = layout([
        [widgetbox(divError)]
        ])
        curdoc().add_root(l)
        state = ERROR
        return


    state = LOADEDMETA
    variables = ["None"]
    meshOptions = ["calculate", "DOM1 (not implemented)", "DOM2 (not implemented)", "DOM3 (not implemented)"]
    for k,v in xrData.variables.items():
        variables.append(k)

    slVar = bokeh.models.Select(title="Variable", options=variables, value="None")
    slMesh = bokeh.models.Select(title="Mesh", options=meshOptions, value="calculate")

    btShow = bokeh.models.Button(label="show")
    btShow.on_click(loadGraphCallback)

    curdoc().clear()
    l = layout([
    [widgetbox(slVar)],
    [widgetbox(slMesh)],
    [widgetbox(btShow)]
    ])
    curdoc().add_root(l)


def sliderUpdate(attr, old, new):
    height = new
    loadGraphCallback()

def variableUpdate(attr,old,new):
    variable = new
    loadGraphCallback()

def update(attr, old, new):
    loadGraphCallback()

def loadGraphCallback():
    global xrData, height, variable
    global slHeight, slVar, slCMap

    state =LOADING

    if slHeight is not None:
        height = slHeight.value
    if slVar is not None:
        variable = slVar.value
    if slCMap is not None:
        cm = slCMap.value
    else:
        cm = COLORMAPS[0]

    variables = ["None"]
    for k,v in xrData.variables.items():
        variables.append(k)

    slVar = bokeh.models.Select(title="Variable", options=variables, value=variable)
    slHeight = bokeh.models.Slider(start=0, end=len(xrData.height)-1, value=height, step=1, title="Height")

    slCMap = bokeh.models.Select(title="Colormap", options=COLORMAPS, value=cm)
    txTitle = bokeh.models.TextInput(value="TR_stn, height ...", title="Title:")
    txPre = bokeh.models.PreText(text=str(xrData),width=800)
    cbOpts = bokeh.models.CheckboxButtonGroup(
        labels=["Colorbar", "x-Axis", "y-Axis"], active=[0, 1, 1])


    btShow = bokeh.models.Button(label="show")
    btShow.on_click(loadGraphCallback)
    slVar.on_change("value",variableUpdate)
    slCMap.on_change("value",update)

    variable = slVar.value


    divLoading = Div(text="loading graph...")
    curdoc().clear()
    l = layout([
        [widgetbox(divLoading)]
    ])
    curdoc().add_root(l)

    plot = renderer.get_widget(graph(),'widgets')
    print(plot.state)
    curdoc().clear()
    l = layout([
        [widgetbox(txTitle)],
        [widgetbox(slVar)],
        [widgetbox(cbOpts)],
        [widgetbox(slCMap)],
        [plot.state],
        [widgetbox(txPre)]
    ])

    curdoc().add_root(l)
    state = LOADED

def modify_doc(doc):
    doc.title = 'ncview2'
    btLoad = bokeh.models.Button(label="load")
    btLoad.on_click(loadMetaCallback)

    doc.clear()
    l = layout([
    [widgetbox(urlinput)],
    [widgetbox(btLoad)]
    ])
    doc.add_root(l)


modify_doc(curdoc())
