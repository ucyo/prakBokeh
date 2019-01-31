#!/usr/bin/python
from bokeh.layouts import layout, widgetbox
from bokeh.models import ColumnDataSource, Div
from bokeh.models.widgets import TextInput
from bokeh.io import curdoc

import bokeh as bokeh
import pandas as pd
import xarray as xr
import holoviews as hv
import numpy as np


from holoviews.operation.datashader import datashade

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

COLORMAPS = ["Inferno","Magma","Plasma","Viridis"]

def getURL():
    #url = urlinput.value
    url = "/home/max/Downloads/2016033000-ART-passive_grid_pmn_DOM01_ML_0002.nc"
    return url

def graph(v,h):
    global n, n4, tris, xrData, verts
    n1 = []
    n2 = []
    n3 = []

    if n is None:
        xrData = xr.open_dataset(getURL(),decode_cf=False)
        verts = np.column_stack((xrData.clon_bnds.stack(z=('vertices','ncells')),xrData.clat_bnds.stack(z=('vertices','ncells'))))

        l = len(xrData.clon_bnds)

        n1 = np.arange(l)
        n2 = n1 + l
        n3 = n2 + l

        n4 = np.column_stack((n1,n2,n3))
        n = np.column_stack((n4,getattr(xrData,v).isel(height=h,time=0)))

        verts = pd.DataFrame(verts,  columns=['x', 'y'])
        tris  = pd.DataFrame(n, columns=['v0', 'v1', 'v2',"var"], dtype = np.float64)
        tris['v0'] = tris["v0"].astype(np.int32)
        tris['v1'] = tris["v1"].astype(np.int32)
        tris['v2'] = tris["v2"].astype(np.int32)
    else:
        tris["var"] = getattr(xrData, v).isel(height=h, time=0)

    print('vertices:', len(verts), 'triangles:', len(tris))

    res = datashade(hv.TriMesh((tris,verts), label=(v+" on height %d"%h)).options(filled=True))
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
    meshOptions = ["calculate", "DOM1", "DOM2", "DOM3"]
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

def loadGraphCallback():
    global xrData, height
    global slHeight, slVar

    state =LOADING

    if slHeight is not None:
        height = slHeight.value
    if slVar is not None:
        variable = slVar.value

    variables = ["None"]
    for k,v in xrData.variables.items():
        variables.append(k)

    slVar = bokeh.models.Select(title="Variable", options=variables, value=variable)
    slHeight = bokeh.models.Slider(start=0, end=len(xrData.height)-1, value=height, step=1, title="Height")


    btShow = bokeh.models.Button(label="show")
    btShow.on_click(loadGraphCallback)
    #slHeight.on_change("value",sliderUpdate)
    slVar.on_change("value",variableUpdate)

    variable = slVar.value


    divLoading = Div(text="loading graph...")
    curdoc().clear()
    l = layout([
        [widgetbox(divLoading)]
    ])
    curdoc().add_root(l)

    height = slHeight.value
    plot = renderer.get_plot(graph(variable,int(height)))
    print(plot.state)
    curdoc().clear()
    l = layout([
        [widgetbox(slVar)],
        [widgetbox(slHeight)],
        [widgetbox(btShow)],
        [plot.state]
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



#urlinput = TextInput(value="default", title="netCFD/OpenDAP Source URL:")
#btLoad = bokeh.models.Button(label="load")
#btLoad.on_click(loadCallback)


#shaded = graph("")
#doc = hv.renderer('bokeh').server_doc(shaded)
#doc.title = 'HoloViews Bokeh App'

modify_doc(curdoc())
