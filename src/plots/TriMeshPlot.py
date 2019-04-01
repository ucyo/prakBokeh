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

from .Plot import Plot

class TriMeshPlot(Plot):
    def __init__(self, logger, renderer, xrData):
        """
        Overwrites Plot.__init__
        """
        self.logger = logger
        self.renderer = renderer
        self.xrData = xrData

        self.loadMesh(xrData)

    def getPlotObject(self, variable, title, cm="Magma", aggDim="None", aggFn="None", showCoastline=True):
        """
        Function that builds up a plot object for Bokeh to display
        Returns:
            : a plot object
        """
        self.variable = variable
        self.aggDim = aggDim
        self.aggFn = aggFn
        self.showCoastline = showCoastline

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
        totalgraphopts = {"height":150, "width":300}


        if len(self.freeDims) > 0:
            self.logger.info("Show with DynamicMap")
            dm = hv.DynamicMap(self.buildTrimesh, kdims=self.freeDims).redim.range(**ranges)
            if self.showCoastline == True:
                return self.renderer.get_widget((rasterize(dm).opts(**rasterizedgraphopts) * coastln).opts(**totalgraphopts),'widgets')
            else:
                return self.renderer.get_widget((rasterize(dm).opts(**rasterizedgraphopts)).opts(**totalgraphopts), 'widgets')
        else:
            self.logger.info("Show without DynamicMap")
            dm = self.buildTrimesh()
            if self.showCoastline == True:
                return self.renderer.get_plot((rasterize(dm).opts(**rasterizedgraphopts) * coastln).opts(**totalgraphopts))
            else:
                return self.renderer.get_plot((rasterize(dm).opts(**rasterizedgraphopts)).opts(**totalgraphopts))


    def buildTrimesh(self, *args):
        """
        Function that builds up the TriMesh-Graph
        Args:
            Take multiple arguments. A value for every free dimension.
        Returns:
            The TriMesh-Graph object
        """

        selectors = self.buildSelectors(args)
        self.logger.info("Selectors: " + str(selectors))

        if self.aggDim == "None" or self.aggFn == "None":
            self.logger.info("No aggregation")
            self.tris["var"] = getattr(self.xrData, self.variable).isel(selectors)
        else:
            if self.aggFn == "mean":
                self.logger.info("mean aggregation with %s" % self.aggDim)
                self.tris["var"] = getattr(self.xrData, self.variable).mean(dim=self.aggDim).isel(selectors)
            elif self.aggFn == "sum":
                self.logger.info("sum aggregation %s" % self.aggDim)
                self.tris["var"] = getattr(self.xrData, self.variable).sum(dim=self.aggDim).isel(selectors)
            else:
                self.logger.error("Unknown Error! AggFn not None, mean, sum")


        # Apply unit
        factor = 1
        self.tris["var"] = self.tris["var"] * factor

        res = hv.TriMesh((self.tris,self.verts), label=(self.title))
        return res

    def loadMesh(self, xrData):
        """
        Function to build up a mesh

        Returns:
            array of triangles and vertices: Builds the mesh from the loaded xrData
        """
        try:
            # If only one file is loaded has no attribute time, so we have to check this
            if hasattr(xrData.clon_bnds, "time"):
                # isel time to 0, as by globbing the clon_bnds array could have multiple times
                verts = np.column_stack((xrData.clon_bnds.isel(time=0).stack(z=('vertices', 'ncells')),
                                         xrData.clat_bnds.isel(time=0).stack(z=('vertices', 'ncells'))))
            else:
                verts = np.column_stack((xrData.clon_bnds.isel().stack(z=('vertices', 'ncells')),
                                         xrData.clat_bnds.isel().stack(z=('vertices', 'ncells'))))
        except:
            self.logger.error("Failed to build loadMesh():verts!")

        # Calc degrees from radians
        f = 180 / math.pi
        for v in verts:
            v[0] = v[0] * f
            v[1] = v[1] * f

        # If only one file is loaded has no attribute time, so we have to check this
        if hasattr(xrData.clon_bnds, "time"):
            # isel time to 0, as by globbing the clon_bnds array could have multiple times
            l = len(xrData.clon_bnds.isel(time=0))
        else:
            l = len(xrData.clon_bnds.isel())
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
