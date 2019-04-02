#!/usr/bin/python
#from bokeh.server.server import Server
from bokeh.layouts import layout, widgetbox, row
from bokeh.models import ColumnDataSource, Div
from bokeh.models.widgets import TextInput
from bokeh.io import curdoc
import geoviews as gv
import geoviews.feature as gf

import bokeh as bokeh
import pandas as pd
import xarray as xr
import holoviews as hv
import numpy as np

from cartopy import crs

from holoviews.operation.datashader import datashade, rasterize

import math
import logging

from src.plots.TriMeshPlot import TriMeshPlot
from src.plots.CurvePlot import CurvePlot

renderer = hv.renderer('bokeh').instance(mode='server',size=300)


FORMAT = '%(asctime)-15s %(clientip)s %(user)-8s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('ncview2')
logger.info({i.__name__:i.__version__ for i in [hv, np, pd]})


defaultinput = "http://eos.scc.kit.edu/thredds/dodsC/polstracc0new/2016033000/2016033000-ART-passive_grid_pmn_DOM01_ML_0002.nc"
#defaultinput = "eos.scc.kit.edu"
#defaultinput = "/home/max/Downloads/Test/2016033000/2016033000-ART-passive_grid_pmn_DOM01_ML_0002.nc"

urlinput = TextInput(value=defaultinput, title="netCDF file -OR- OPeNDAP URL:")
slVar = None
slMesh = None
slCMap = None
slAggregateFunction = None
slAggregateDimension = None
cbCoastlineOverlay = None
txTitle = None

aggregates = []

COLORMAPS = ["Blues","Inferno","Magma","Plasma","Viridis","BrBG","PiYG","PRGn","PuOr","RdBu","RdGy","RdYlBu","RdYlGn","Spectral","BuGn","BuPu","GnBu","Greens","Greys","Oranges","OrRd","PuBu","PuBuGn","PuRd","Purples","RdPu","Reds","YlGn","YlGnBu","YlOrBr","YlOrRd"]

tmPlot = None
xrData = None
xrDataMeta = None

class Aggregates():
    def __init__(self, dim, f):
        self.dim = dim
        self.f = f


def getURL():
    """
    Function to capsulate the url input.

    Returns:
        str: The entered data url
    """
    url = urlinput.value
    # Build list if multiple urls are entered
    if ',' in url:
        url = url.split(',')
    return url

def loadData(url):
    """
    Function load OPeNDAP data

    Returns:
        xarray Dataset: Loads the url as xarray Dataset
    """
    # As issue: https://github.com/pydata/xarray/issues/1385 writes, open_mfdata is much slower. Opening the
    # same file and preparing it for the curve graph is taking minutes with open_mfdataset, but seconds with open_dataset
    if '*' in url or isinstance(url,list):
        logger.info("Loading with open_mfdataset")
        xrData = xr.open_mfdataset(url,decode_cf=False,decode_times=False)
    else:
        logger.info("Loading with open_data")
        xrData = xr.open_dataset(url, decode_cf=False, decode_times=False)
    return xrData

def loadDataMeta(url):
    """
    Function load OPeNDAP data

    Returns:
        xarray Dataset: Loads the url as xarray Dataset
    """
    # As issue: https://github.com/pydata/xarray/issues/1385 writes, open_mfdata is much slower. Opening the
    # same file and preparing it for the curve graph is taking minutes with open_mfdataset, but seconds with open_dataset
    if '*' in url or isinstance(url,list):
        logger.info("Loading with open_mfdataset")
        xrData = xr.open_mfdataset(url,decode_cf=False,decode_times=False, chunks={})
    else:
        logger.info("Loading with open_data")
        xrData = xr.open_dataset(url, decode_cf=False, decode_times=False, chunks={})
    return xrData


def preDialog():
    global slVar, slMesh, xrDataMeta

    logger.info("Started preDialog()")

    divLoading = Div(text="Loading metadata...")
    curdoc().clear()
    l = layout([
    [widgetbox(divLoading)]
    ])
    curdoc().add_root(l)

    url = getURL()

    try:
        xrDataMeta = loadDataMeta(url)
        assert xrDataMeta != None
    except:
        logger.error("Failed to load metadata for url " + url)
        divError = Div(text="Failed to load metadata for url " + url)
        curdoc().clear()
        l = layout([
        [widgetbox(divError)]
        ])
        curdoc().add_root(l)
        return


    variables = [x for x in xrDataMeta.variables.keys()]
    # TODO implement DOM02, DOM03
    meshOptions = ["DOM1", "DOM2"]
    #meshOptions = ["reg","calculate", "DOM1", "DOM2"]


    default_dom = "DOM1" if "DOM01" in urlinput.value else "DOM2"
    slVar = bokeh.models.Select(title="Variable", options=variables, value="TR_stn")
    slMesh = bokeh.models.Select(title="Mesh", options=meshOptions, value=default_dom)
    txPre = bokeh.models.PreText(text=str(xrDataMeta),width=800)
    btShow = bokeh.models.Button(label="show")
    btShow.on_click(mainDialog)

    if len(variables) == 0:
        logger.error("No variables found!")
        divError = Div(text="No variables found!")
        curdoc().clear()
        l = layout([
            [widgetbox(divError)]
        ])
        curdoc().add_root(l)
        return

    curdoc().clear()
    l = layout([
    [widgetbox(slVar)],
    [widgetbox(slMesh)],
    [widgetbox(txPre)],
    [widgetbox(btShow)]
    ])
    curdoc().add_root(l)


def variableUpdate(attr,old,new):
    """
    This function is only a wrapper round the main function for building the buildDynamicMap.
    It is called if at property like the cmap is changed and the whole buildDynamicMap needs
    to be rebuild.
    """
    variable = new
    mainDialog()


def cmapUpdate(attr, old, new):
    """
    This function is only a wrapper round the main function for building the buildDynamicMap.
    It is called if at property like the cmap is changed and the whole buildDynamicMap needs
    to be rebuild.
    """
    mainDialog()


def aggDimUpdate(attr, old, new):
    mainDialog()

def aggFnUpdate(attr, old, new):
    mainDialog()

def coastlineUpdate(new):
    logger.info("coastlineUpdate")
    mainDialog()

def mainDialog():
    """
    This function build up and manages the Main-Graph Dialog
    """
    global slVar, slCMap, txTitle, slAggregateFunction, slAggregateDimension, cbCoastlineOverlay
    global tmPlot, xrData, xrDataMeta

    logger.info("Started mainDialog()")

    btApply = bokeh.models.Button(label="apply")
    btApply.on_click(mainDialog)

    slVar.on_change("value", variableUpdate)

    if slCMap is None:
        slCMap = bokeh.models.Select(title="Colormap", options=COLORMAPS, value=COLORMAPS[0])
        slCMap.on_change("value", cmapUpdate)

    if txTitle is None:
        txTitle = bokeh.models.TextInput(value="title", title="Title:")

    txPre = bokeh.models.PreText(text=str(xrDataMeta),width=800)

    # Define aggregates
    # TODO allow other/own aggregateFunctions
    aggregateFunctions = ["None","mean","sum"]
    # TODO load this array from the data

    if "ML" in urlinput.value:
        height = "height"
    elif "PL" in urlinput.value:
        height = "lev"
    else:
        height = "alt"
    aggregateDimensions = ["None", height, "lat"] # removed lat since it takes too long

    # time could only be aggregated if it exist
    if hasattr(xrDataMeta.clon_bnds, "time"):
        aggregateDimensions.append("time")

    if slAggregateFunction is None:
        slAggregateFunction = bokeh.models.Select(title="Aggregate Function", options=aggregateFunctions, value="mean")
        slAggregateFunction.on_change("value", aggFnUpdate)
    if slAggregateDimension is None:
        slAggregateDimension = bokeh.models.Select(title="Aggregate Dimension", options=aggregateDimensions, value="lat")
        slAggregateDimension.on_change("value", aggDimUpdate)
    if cbCoastlineOverlay is None:
        cbCoastlineOverlay = bokeh.models.CheckboxGroup(labels=["Show coastline"], active=[0])
        cbCoastlineOverlay.on_click(coastlineUpdate)

    variable = slVar.value
    title = txTitle.value
    cm = slCMap.value
    aggDim = slAggregateDimension.value
    aggFn = slAggregateFunction.value
    showCoastline = len(cbCoastlineOverlay.active) > 0

    # Showing a Loading Infotext
    divLoading = Div(text="loading buildDynamicMap...")
    curdoc().clear()
    l = layout([
        [widgetbox(divLoading)]
    ])
    curdoc().add_root(l)

    # Choose if a Curve or TriMesh is to be used
    if aggDim == "lat" and aggFn != "None":
        if xrData is None:
            logger.info("Loading unchunked data for curveplot")
            try:
                url = getURL()
                xrData = loadData(url)
                assert xrData != None
            except:
                logger.error("Error for loading unchunked data.")
        logger.info("Build CurvePlot")
        cuPlot = CurvePlot(logger, renderer, xrData)
        plot = cuPlot.getPlotObject(variable=variable,title=title,aggDim=aggDim,aggFn=aggFn)
        logger.info("Returned plot")
    else:
        if tmPlot is None:
            logger.info("Build TriMeshPlot")
            logger.info(xrDataMeta is None)
            tmPlot = TriMeshPlot(logger, renderer, xrDataMeta)

        plot = tmPlot.getPlotObject(variable=variable,title=title,cm=cm,aggDim=aggDim,aggFn=aggFn, showCoastline=showCoastline)


    curdoc().clear()
    lArray = []
    lArray.append([widgetbox(txTitle)])
    lArray.append([widgetbox(slVar)])
    # Hide colormap option if CurvePlot is used
    if aggDim != "lat" or aggFn == "None":
        lArray.append([widgetbox(slCMap)])
        lArray.append([widgetbox(cbCoastlineOverlay)])

    lArray.append([row(slAggregateDimension,slAggregateFunction)])
    lArray.append([widgetbox(btApply)])
    lArray.append([plot.state])
    lArray.append([widgetbox(txPre)])

    l = layout(lArray)

    curdoc().add_root(l)

# This function is showing the landingpage. Here one could enter the url for the datasource.
# Entering the url is the first step in the dialog
def entry(doc):
    doc.title = 'ncview2'
    btLoad = bokeh.models.Button(label="load")
    btLoad.on_click(preDialog)
    tx = "ncview II"
    txPre = bokeh.models.PreText(text=tx,width=800)

    doc.clear()
    l = layout([
    [widgetbox(txPre)],
    [widgetbox(urlinput)],
    [widgetbox(btLoad)]
    ])
    doc.add_root(l)

#server = Server({'/': entry}, num_procs=4)
#server.start()

#if __name__ == '__main__':
#    print('Opening Bokeh application on http://localhost:5006/')
#    server.io_loop.add_callback(server.show, "/")
#    server.io_loop.start()

entry(curdoc())
