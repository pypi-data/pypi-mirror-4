# -*- coding:utf-8 -*-
'''
Created on Apr 21, 2010

Scatterplot matrix

@author: Delphine Pessoa

with modifications by Flávio C. Coelho
'''
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NToolbar
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from matplotlib import rcParams

from PyQt4.QtGui import QSizePolicy, QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QStatusBar, QWidget,  QPixmap,  QIcon

from numpy import arange, array, compress, zeros,  ones,  searchsorted, inf
from pylab import plot, histogram, show
from scipy.stats import linregress
from copy import deepcopy
import sys
import time
import pdb

__docformat__ = "restructuredtext en"

class ScatMat:
    """ 
    Builds a scatterplot matrix from a  
    """
    def __init__(self, pars, title='', parfun=None):
        """
        Builds a scatterplot matrix
        
        :Parameters:
            - `pars`: dictionary of {"parameter name" : array of parameter values}.
            - `parfun`: Function taking as args an axes object and a boolean array 
            representing selected pars and is expected to use the axes to plot something. 
        """
        t0 = time.time()        
        #Create Window
        pw = QWidget(parent=None)
        pw.setWindowTitle(title)
        icon = QIcon()
        icon.addPixmap(QPixmap(":/viz/images/line-plot.png"), QIcon.Normal, QIcon.Off)
        pw.setWindowIcon(icon)
        self.pw = pw
        self.layout  = QVBoxLayout(pw)
        self.msg = None
        self.col_def = 'blue'
        self.col_sel = 'orange'
        self.parsselected = {}#{'p1':(min,max),...}
        self.barsselected= {} #histogram bars selected
        
        #Add Figure
        self.canvas = MeuCanvas( pars=pars,  parent = pw, cdef=self.col_def, csel=self.col_sel)
        self.parfun = parfun
        if parfun:
            self.setup_parfun_axes()
        self.layout.addWidget(self.canvas)
        
        #Bind 'pick' event for clicking on one of the bars
        self.pars = pars
        self.canvas.mpl_connect('pick_event', self.on_p)
        self.hist_sel = None
        self.val_sel = None
        
        #Add Toolbar
        self.tb = NToolbar(self.canvas, parent = pw)
        self.layout.addWidget(self.tb)

        self.showMessage('Scatterplot Matrix')
        
        t1 = time.time()
        print "Ready in ", t1-t0, "seconds."
#        pw.show()
#        self.canvas.show()
        print "Draw in ", time.time()-t1
    
    def showMessage(self, msg):
        if self.msg:
            self.msg.set_visible(False)
        self.msg = self.canvas.fig.suptitle(msg)
        
    def setup_parfun_axes(self):
        """
        Creates the axes for plotting parameter function
        """
        np = len(self.pars)
        #Calculating position of axis
        if np%2 ==0:#is even
            b, l, h, w = 0.5, .5, .5, .5
        else:
            b = 1-(np//2)/np
            l = (np//2)/np
            h, w = l, 1-l
        self.funax = self.canvas.fig.add_axes((l, b, w, h))
        
    def plot_parfun(self, parsel):
        """
        Plot parameter function
        """
        ydata, xdata = self.parfun(self.funax, parsel)
        
    
    def on_p(self, event):
        """The event received here is of the type matplotlib.backend_bases.PickEvent which carries a lot of information """
        
        t0 = time.time()
        
        ax = event.mouseevent.inaxes #axes in which the event happened
        qax = self.canvas.daxes_hist[ax]
        qp =  qax['parx'] #Current parameter selected   
        msg = "You selected a bar of the parameter %s"%qp
        self.showMessage(msg)
        
        #search the bin values
        val = event.mouseevent.xdata 
        hval = qax['hist'][1]
        
        ix = searchsorted(hval, val, side='left')
        mn = hval[ix-1] if ix !=0 else -inf
        mx = hval[ix]
        
        # Store pars selected
        if qp not in self.parsselected:
            self.parsselected[qp] = [(mn, mx)]
        else:
            if (mn, mx) in self.parsselected[qp]: #remove range
                idx = self.parsselected[qp].index((mn, mx))
                self.parsselected[qp].pop(idx)
                if self.parsselected[qp] == []: #if list is empty
                    self.parsselected.pop(qp) #remove parameter altogether
            else: #parameter has been selected before but not with this particular range
                self.parsselected[qp].append((mn, mx))
        print self.parsselected
        msg += " with values between %f and %f" % (mn, mx)
        self.showMessage(msg)
        
        qh = qax['rect'][ix-1] #bar of histogram selected i-1
        if qh not in self.barsselected:
            self.barsselected[qh]=1
        else:
            qh.set_facecolor(self.col_def)#change color to default
            self.barsselected.pop(qh) #remove from selected set
            
            
        for b in self.barsselected.keys(): #change color of selected bars
            b.set_facecolor(self.col_sel) 
            
        #Values of parameter that that fit in all ranges selected
        self.val_sel = array([True]*len(self.pars[qp]))
        self.val_sel.shape = self.pars[qp].shape
#            pdb.set_trace()
        for p, lims in self.parsselected.items():
            psel = array([False]*len(self.pars[qp]));psel.shape = self.pars[qp].shape
            for lim in lims:#"or" all different ranges  for a given parameter
                psel |= (self.pars[p]>=lim[0]) & (self.pars[p]<=lim[1])
            # "and" to obtain intersection of each parameter's ranges
            self.val_sel &= psel
        # revert all points to unselected if no parameters are selected
        if not self.parsselected:
            self.val_sel = array([False]*len(self.pars[qp]))
        # Update plots    
        print sum(self.val_sel)
        for axi in self.canvas.daxes_plot:
            ax = self.canvas.daxes_plot[axi]
            dx = ax['data_x']
            dy = ax['data_y']
            ax['plot_def'].set_xdata(dx[- self.val_sel])
            ax['plot_def'].set_ydata(dy[- self.val_sel])
            ax['plot_sel'].set_xdata(dx[self.val_sel])
            ax['plot_sel'].set_ydata(dy[self.val_sel])
        
        self.canvas.draw()
        print time.time()-t0, "seconds to redraw figure"
        
        
class MeuCanvas(FigureCanvas,  QWidget):
    """
    Costumized QWidget to use matplotlib figure
    """
    def __init__(self, pars, cdef, csel, parent=None, height=100,  width=100,  dpi=60):
#        QWidget.__init__(self, parent)
        self.fig = Figure(figsize=(width,  height),  dpi = dpi)
        
        self.compute_initial_figure(pars, cdef, csel)
        self.fig.subplots_adjust(top = 0.95, right=.95, left=.05, bottom=.05, wspace=0, hspace=0)

        FigureCanvas.__init__(self,  self.fig)
        self.setParent(parent)
        
        FigureCanvas.setSizePolicy(self, 
                                        QSizePolicy.Expanding, 
                                        QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
    
    def compute_initial_figure(self, pars, cdef, csel):
        """
        Creates initial figures
        
        :parameters:
            - `pars`: dictionary with series for the scatterplots
            - `cdef`: defaul color for the plots
            - `csel`: color for the selected dots
        """
        par = pars.keys()
        p = len(par)
        labels = []
        self.daxes_hist = {}
        self.daxes_plot = {}
        
        l = list()
        rev = l[:]
        rev.reverse()
        n= 1
        for y in arange(0, p):
            for x in arange(0, y+1):
                py = par[y]
                px = par[x]
                npict = (p*y)+1+x
                ax = self.fig.add_subplot(p, p, npict)
                axc='w'#axis background color
                if x ==y:
                    #plot the histograms in the diagonal
                    hists = histogram(pars[px])
                    lcoords = hists[0]
                    if len(hists[0])!= len(hists[1]):
                        lcoords = hists[1][:-1]
                        
                    bars = ax.bar(left=lcoords, height=hists[0], width=(hists[1][1]-hists[1][0]), picker=True, label='')
                    ax.set_title(px)
                    self.daxes_hist[ax] = {'parx':px, 'hist':hists , 'rect':bars}
                else:
                    #scatterplots in lower triangle
                    dx = pars[px]
                    dy = pars[py]
                    res = linregress(dx, dy)
                    if res[3] < 0.05:
                        axc = 'bisque' if res[2]<0 else 'palegreen'
                    ax.set_axis_bgcolor(axc)
                    pl_def, = ax.plot(dx, dy, 'o',markersize=5,  c=cdef, alpha=.8, label='')
                    pl_sel, = ax.plot([], [], 'o',markersize=5,  c=csel, alpha=.8, label='')
                    
                    lry = (dx*res[0])+res[1]
                    lab = r'$R^2=%.2f$'%(res[2]*res[2]) if res[3] < 0.05 else ""
                    ax.plot(dx, lry, 'k',  label=lab)
                    self.daxes_plot[ax] = {'parx':px, 'pary':py, 'data_x':dx, 'data_y':dy, 'plot_def':pl_def, 'plot_sel':pl_sel}
                
                if x == 0:
                    ax.set_ylabel(py)
                else:
                    ax.set_yticks([])
#                if y !=0:
#                    ax.set_xticks([])

                #Remove half of the xticks and yticks                
                xt = ax.get_xticks()
                yt = ax.get_yticks()
                ax.set_xticks(xt[1:-1:2])
                ax.set_yticks(yt[1:-1:2])
                ax.legend()
                
                npict += 1
            n+=1
    
if __name__=="__main__":
    import sys
    import numpy as np
    from PyQt4 import QtGui
    app = QtGui.QApplication(sys.argv)  
    pars = {'a':np.random.normal(5, 1, 1000), 'b':np.random.normal(3, 1, 1000), 'c':np.random.normal(7, 1, 1000)}
    spm = ScatMat(pars,'test' )
    spm.pw.showMaximized()
    sys.exit(app.exec_())
