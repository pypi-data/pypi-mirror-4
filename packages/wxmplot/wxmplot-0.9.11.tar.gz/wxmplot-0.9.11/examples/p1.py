#!/usr/bin/python
#
# simple example of MPlot

import wx
import time
import numpy
import wxmplot
import epics
from epics.wx import DelayedEpicsCallback

class PVPlotter():
    def __init__(self, xpvname, ypvname, n=60):
        self.plotter= wxmplot.PlotFrame()
        self.x = None
        self.y = None
        self.n = n

        self.xpvname = xpvname
        self.xpv = epics.PV(xpvname)
        self.x = self.xpv.get()
        self.ypvname = ypvname
        self.ypv = epics.PV(ypvname)
        self.ypv.add_callback(self.onChange)
        self.y = self.ypv.get()
	print len(self.x) , len(self.y)
        self.plotter.plot(self.x[:n], self.y[:n], title='13-ID RGA 2', xlabel='Z')
        self.plotter.Show()

    @DelayedEpicsCallback
    def onChange(self, pvname=None, value=None, **kw):
        if pvname == self.xpvname:
            self.x = value
        else:
            self.y = value
        if self.x is not None and self.y is not None:
            n = min(60, len(self.x), len(self.y))
            self.plotter.update_line(0, self.x[:n], self.y[:n])
            print '======', time.ctime()
            print ' x   y'
            for x, y in zip(self.x, self.y):
                if y > 1.e-4:
                    print x, y

#
app = wx.PySimpleApp()
p =PVPlotter('FE:13:ID:RGA2:wfx', 'FE:13:ID:RGA2:wfy')
app.MainLoop()


