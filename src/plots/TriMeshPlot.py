#!/usr/bin/python


import geoviews as gv
import geoviews.feature as gf

import bokeh as bokeh
import pandas as pd
import xarray as xr
import holoviews as hv
import numpy as np

from cartopy import crs

from holoviews.operation.datashader import rasterize

import math

import grpc                     
import nc_pb2
import nc_pb2_grpc

from .Plot import Plot

import time


MAX_MESSAGE_LENGTH = 16000000
current_milli_time = lambda: int(round(time.time() * 1000))

class TriMeshPlot(Plot):
    def __init__(self, url, heightDim, dom, logger, renderer, xrMetaData):
        """
        Overwrites Plot.__init__
        """
        self.url = url
        self.heightDim = heightDim
        self.dom = dom
        self.logger = logger
        self.renderer = renderer
        self.xrMetaData = xrMetaData
        self.dataUpdate = True

        self.useFixColoring = False
        self.fixColoringMin = None
        self.fixColoringMax = None

        self.cSymmetric= False
        self.cLogZ = False

        self.cLevels = 0

        channel = grpc.insecure_channel(
            '0.0.0.0:50051',
            options=[
                ('grpc.max_send_message_length', MAX_MESSAGE_LENGTH),
                ('grpc.max_receive_message_length', MAX_MESSAGE_LENGTH),
            ]
        )
        self.stub = nc_pb2_grpc.NCServiceStub(channel)

        self.loadMesh(xrMetaData)


    def getPlotObject(self, variable, title, cm="Magma", aggDim="None", aggFn="None", showCoastline=True, useFixColoring=False, fixColoringMin=None, fixColoringMax=None, cSymmetric=False, cLogZ=False, cLevels=0, dataUpdate=True):
        """
        Function that builds up a plot object for Bokeh to display
        Returns:
            : a plot object
        """
        self.variable = variable
        self.aggDim = aggDim
        self.aggFn = aggFn
        self.showCoastline = showCoastline
        self.useFixColoring = useFixColoring
        self.fixColoringMin = fixColoringMin
        self.fixColoringMax = fixColoringMax

        self.cSymmetric = cSymmetric
        self.cLogZ = cLogZ

        self.cLevels = cLevels

        self.dataUpdate = dataUpdate

        if cm != "None":
            self.cm = cm

        self.title = title

        # Builds up the free and non-free dimensions array
        self.buildDims()

        return self.buildDynamicMaps()

    def buildDynamicMaps(self):
        """
        Function to capsulate the free dimensions together with the actual
        Trimeshgraph.

        Returns:
            : a rasterizes plot of the DynamicMap with the TriMesh graph in it.
        """
        ranges = self.getRanges()
        coastln = gf.coastline.opts(projection=crs.PlateCarree(),line_width=2)
        rasterizedgraphopts = {"cmap":self.cm,"colorbar":True}
        # TODO do not hardcode the sizes
        totalgraphopts = {"height":self.HEIGHT, "width":self.WIDTH}


        if len(self.freeDims) > 0:
            self.logger.info("Show with DynamicMap")
            dm = hv.DynamicMap(self.buildTrimesh, kdims=self.freeDims).redim.range(**ranges)
        else:
            # This is needed as DynamicMap is not working with an empty kdims array.
            self.logger.info("Show without DynamicMap")
            dm = self.buildTrimesh()

        self.logger.info("Checking for coloring mode...")
        try:
            if self.useFixColoring is True and self.fixColoringMin is not None and self.fixColoringMax is not None:
                self.logger.info("Use fixed coloring with %f to %f" % (self.fixColoringMin, self.fixColoringMax))
                preGraph = rasterize(dm).opts(**rasterizedgraphopts).opts(symmetric=self.cSymmetric,logz=self.cLogZ,color_levels=self.cLevels,clim=(self.fixColoringMin, self.fixColoringMax))
            elif self.useFixColoring is True:
                # Calculate min and max values:
                maxValue = getattr(self.xrMetaData, self.variable).max(dim=getattr(self.xrMetaData,self.variable).dims)
                minValue = getattr(self.xrMetaData, self.variable).min(dim=getattr(self.xrMetaData,self.variable).dims)
                self.logger.info("Use fixed coloring with calculated min (%f) and max(%f)" % ( minValue, maxValue))
                preGraph = rasterize(dm).opts(**rasterizedgraphopts).opts(symmetric=self.cSymmetric,logz=self.cLogZ,color_levels=self.cLevels,clim=(float(minValue), float(maxValue)))
            else:
                self.logger.info("Use no fixed coloring")
                preGraph = rasterize(dm).opts(**rasterizedgraphopts).opts(symmetric=self.cSymmetric,logz=self.cLogZ,color_levels=self.cLevels)
        except Exception as e:
            print(e)

        if self.showCoastline == True:
            graph = preGraph * coastln
        else:
            graph = preGraph
        graph = graph.opts(**totalgraphopts)


        if len(self.freeDims) > 0:
            return self.renderer.get_widget(graph.opts(**totalgraphopts),'widgets')
        else:
            return self.renderer.get_plot(graph.opts(**totalgraphopts))



    def buildTrimesh(self, *args):
        """
        Function that builds up the TriMesh-Graph
        Args:
            Take multiple arguments. A value for every free dimension.
        Returns:
            The TriMesh-Graph object
        """
        if self.dataUpdate == True:
            selectors = self.buildSelectors(args)
            self.logger.info("Selectors: " + str(selectors))

            if self.aggDim == "None" or self.aggFn == "None":
                self.logger.info("No aggregation")
                self.tris["var"] = self.stub.GetTris(nc_pb2.TrisRequest(filename=self.url, variable=self.variable, alt=selectors[self.heightDim], time=selectors['time'], dom=self.dom)).data
            else:
                if self.aggFn == "mean":
                    self.logger.info("mean aggregation with %s" % self.aggDim)
                    self.tris["var"] = self.stub.GetTrisAgg(nc_pb2.TrisAggRequest(filename=self.url, variable=self.variable, aggregateFunction=0, dom=self.dom)).data
                elif self.aggFn == "sum":
                    self.logger.info("sum aggregation %s" % self.aggDim)
                    self.tris["var"] = self.stub.GetTrisAgg(nc_pb2.TrisAggRequest(filename=self.url, variable=self.variable, aggregateFunction=1, time=selectors['time'], dom=self.dom)).data
                else:
                    self.logger.error("Unknown Error! AggFn not None, mean, sum")

            # Apply unit
            factor = 1
            self.tris["var"] = self.tris["var"] * factor

        res = hv.TriMesh((self.tris,self.verts), label=(self.title) )
        return res

    def loadMesh(self, xrMetaData):
        """
        Function to build up a mesh

        Returns:
            array of triangles and vertices: Builds the mesh from the loaded xrMetaData
        """
        start = current_milli_time()
        response = self.stub.GetMesh(nc_pb2.MeshRequest(filename=self.url, dom=self.dom))
        end = current_milli_time()
        self.logger.info("response took %f" % ((end - start) / 1000))
        verts = np.column_stack((response.lons, response.lats))
        # If only one file is loaded has no attribute time, so we have to check this
        if hasattr(xrMetaData.clon_bnds, "time"):
            # isel time to 0, as by globbing the clon_bnds array could have multiple times
            l = len(xrMetaData.clon_bnds.isel(time=0))
        else:
            l = len(xrMetaData.clon_bnds.isel())
        n1 = []
        n2 = []
        n3 = []

        n1 = np.arange(l)
        n2 = n1 + l
        n3 = n2 + l

        # Use n1 as dummy. It will get overwritten later.
        n = np.column_stack((n1, n2, n3, n1))

        verts = pd.DataFrame(verts, columns=['Longitude', 'Latitude'])
        tris = pd.DataFrame(n, columns=['v0', 'v1', 'v2', "var"], dtype=np.float64)

        # As those values are use as indecies in the verts array, they must be int, but the forth column
        # needs to be float, as it contains the data
        tris['v0'] = tris["v0"].astype(np.int32)
        tris['v1'] = tris["v1"].astype(np.int32)
        tris['v2'] = tris["v2"].astype(np.int32)

        self.tris = tris
        self.verts = verts
