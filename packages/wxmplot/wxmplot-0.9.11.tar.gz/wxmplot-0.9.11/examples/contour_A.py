import wx
from numpy import exp, random, arange, outer
from wxmplot import ImageFrame

def gauss2d(x, y, x0, y0, sx, sy):
    return outer(exp(-(((y-y0)/float(sy))**2)/2),
                 exp(-(((x-x0)/float(sx))**2)/2))

if __name__ == '__main__':
    app = wx.PySimpleApp()
    frame = ImageFrame(config_on_frame=True)
    ny, nx = 350, 400
    x = arange(nx)
    y = arange(ny)
    ox =  x / 62.
    oy = -2 + y / 97.0
    dat = 0.2 + (0.03*random.random(size=nx*ny).reshape(ny, nx) +
                 6.0*gauss2d(x, y, 240,  126,  45,  36) +
                12.0*gauss2d(x, y, 130,  230,  67,  43) +
                 3.0*gauss2d(x, y, 175,  198,  83,  97) )

    frame.display(dat, x=ox, y=oy) # , style='contour')
    frame.Show()
    app.MainLoop()
