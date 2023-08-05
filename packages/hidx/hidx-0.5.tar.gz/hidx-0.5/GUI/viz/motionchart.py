# -*- coding: utf-8 -*-

"""
Module implementing MotionChart GUI.
"""
import time
import datetime
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NToolbar
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from matplotlib import rcParams
from matplotlib import cbook
from matplotlib import cm
import matplotlib.colors as colors
import numpy as np
from multiprocessing import Process
from threading import Thread
from PyQt4.QtGui import QWidget, QSizePolicy, QCheckBox
from PyQt4.QtCore import pyqtSignature, SIGNAL, QTimer
from Ui_motionchart import Ui_MotionChart


class MotionChart(QWidget, Ui_MotionChart):
    """
    Class documentation goes here.
    """
    def __init__(self, parent=None, main=None, data={},t_steps=1):
        """

        :param parent: maingui widget
        :param main:
        :param data: dictionary with all the data
        :param t_steps: integer with the number of time steps
        :return:
        """
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.all_data = data
        self.data = {}
        self.t_steps = t_steps
        self.tint = 0 #time interval between time steps in seconds
        self.logscale = [False,False]
        
        self.scatter = Canvas(self, 'scatter')
        self.scatterLayout.addWidget(self.scatter)
        self.bar = Canvas(self, 'bar')
        self.histLayout.addWidget(self.bar)
        self.line = Canvas(self, 'line')
        self.lineLayout.addWidget(self.line)
        self.main = main #main gui
        self.num_ent = len(self.all_data['entity_levels'])
        self.all_data['fall_back_colors'] = np.ones((self.t_steps,self.num_ent)).dot(np.diag(np.arange(self.num_ent)))
        self.check_combos()
        self.timer = QTimer(self)
        self.timer.timeout.connect(lambda:self.timeSlider.setValue(self.current_step+1))
        self.current_step = 0
        self.started = False
        self.fill_entity_group_box(self.all_data['entity_levels'])
    
    def fill_entity_group_box(self,  entities):
        """
        Fill the entity lgroup box with the entity levels so that they can be
        selected
        """
        self.entities_cbs = []
        for e in entities:
            if e is None:
                e = 'NA'
            cb = QCheckBox(self.scrollAreaWidgetContents)
            cb.setText(str(e))
            cb.setCheckState(0)
            self.entityLayout.addWidget(cb)
            self.connect(cb, SIGNAL('stateChanged()'), self.toggle_plot_labels)
            self.entities_cbs.append(cb)
    
    def toggle_plot_labels(self, st):
        legend = [self.all_data['entity_levels']]

    def check_combos(self):
        """
        Check if all combos have been set with some variable
        :return:
        """
        if self.colorCombo.count() == 0:
            self.on_colorCombo_currentIndexChanged('fall_back_colors')

    
    @pyqtSignature("int")
    def on_playSpeed_valueChanged(self, value):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        pass
    
    @pyqtSignature("int")
    def on_timeSlider_valueChanged(self, value):
        """
        Slot documentation goes here.
        """
        self.current_step = value
        print value
        
        self.timeLabel.setText(str(value))
        self.timeSlider.setToolTip(str(value))
        self.scatter.compute_figure(value)
        self.bar.compute_figure(value)
        self.line.compute_figure(value)
        self.update()
        
    @pyqtSignature("")
    def on_playButton_released(self):
        """
        Slot documentation goes here.
        """
        if not self.started:
            self.timer.start(self.tint*1000)
            self.started = True
        else:
            self.timer.stop()
            self.started = False
#        for t in range(len(self.data['t'])):
#            self.timeSlider.setValue(t)
#            time.sleep(self.tint)
        
    @pyqtSignature("QString")
    def on_yVarCombo_currentIndexChanged(self, p0):
        """
        Slot documentation goes here.
        """
        self.data['y'] = self.all_data[str(p0)]
        self.scatter._set_data_set('y')
        self.bar._set_data_set('y')
        self.line._set_data_set('y')
        self.scatter.rescale_axis('y')
        self.line.rescale_axis('y')
    
    @pyqtSignature("bool")
    def on_yLog_toggled(self, checked):
        """
        Slot documentation goes here.
        """
        if checked:
            self.scatter.ax.set_yscale('log')
            self.line.ax.set_yscale('log')
            self.logscale[1] = True
        else:
            self.scatter.ax.set_yscale('linear')
            self.line.ax.set_yscale('linear')
            self.logscale[1] = False
        self.scatter.draw()
        self.line.draw()
    
    @pyqtSignature("bool")
    def on_xLog_toggled(self, checked):
        """
        Slot documentation goes here.
        """
        if checked:
            self.scatter.ax.set_xscale('log')
            self.logscale[0] = True
        else:
            self.scatter.ax.set_xscale('linear')
            self.logscale[0] = False
        self.scatter.draw()

    
    @pyqtSignature("QString")
    def on_xVarCombo_currentIndexChanged(self, p0):
        """
        Slot documentation goes here.
        """
        self.data['x'] = self.all_data[str(p0)]
        self.scatter._set_data_set('x')
        self.bar._set_data_set('x')
        self.line._set_data_set('x')
        self.scatter.rescale_axis('x')

    @pyqtSignature("QString")
    def on_timeCombo_currentIndexChanged(self, p0):
        """
        Slot documentation goes here.
        """
        t = self.all_data[str(p0)]
        self.data['t'] = t

        self.timeSlider.maximum = max(t.ravel())
        self.timeSlider.minimum = min(t.ravel())
        self.timeSlider.value = min(t.ravel())
    
    @pyqtSignature("QString")
    def on_sizeCombo_currentIndexChanged(self, p0):
        """
        Slot documentation goes here.
        """
        self.data['s'] = self.all_data[str(p0)]
        self.scatter._set_data_set('s')
        self.bar._set_data_set('s')
        self.line._set_data_set('s')
        
    @pyqtSignature("QString")
    def on_colorCombo_currentIndexChanged(self, p0):
        """
        Derive colormap from color variables.
        """
        cs1 = self.all_data[str(p0)]
        cs1 = np.array(cs1)
        shp = cs1.shape
        try:
            cs1 /= cs1.max() # turn variable levels into floats between 0 and 1

        except TypeError: # categorical variable
            cl = set(cs1.ravel().tolist()) #unique category list
            l = len(cl)
            cd = dict(zip(cl, np.arange(l) / float(l))) #category -> float dict
            for i, e in enumerate(cs1.ravel()):
                cs1.ravel()[i] = cd[e]
        self.data['c'] = cs1
#        print "==> Colormap: ",self.data['c']
        self.scatter._set_data_set('c')
        self.bar._set_data_set('c')
        self.line._set_data_set('c')

class Canvas(FigureCanvas):
    """
    Costumized QWidget to use matplotlib figure
    """
    def __init__(self, parent=None, typ='scatter', height=100, width=100,
                 dpi=100):
        self.fig = Figure(figsize=(width,  height), dpi=dpi)
        self.ax = self.fig.gca()#add_subplot(111, autoscale_on=not typ == 'scatter')
        self.ax.hold(False)
        self.typ = typ
        self.gui = parent
        if self.typ == 'scatter':
            self.ax.autoscale(False)
            self.ax.autoscale_view(False, False)
        
#        self._set_data_set()

        #self.fig.subplots_adjust(top=0.95, right=0.95, left=0.05, bottom=0.05,
        #                         wspace=0, hspace=0)
        FigureCanvas.__init__(self,  self.fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def _set_data_set(self, var='all'):
        if var == 'all':
            self.x = self.gui.data['x'].astype(float)
            self.y = self.gui.data['y'].astype(float)
            self.siz = self.gui.data['s'].astype(float)
            self.col = self.gui.data['c'].astype(float)
            self.siz  = self.siz/ float(self.siz.max()) * 500. +100 #normalize size of marker
            self.xlims = (self.x.min(), self.x.max())
            self.ylims =  (self.y.min(), self.y.max())
        elif var == 'x':
            self.x = self.gui.data['x'].astype(float)
            self.xlims = (self.x.min(), self.x.max())
#            print 'x: ',  self.x.shape
        elif var == 'y':
            self.y = self.gui.data['y'].astype(float)
            self.ylims =  (self.y.min(), self.y.max())
#            print 'y: ',  self.y.shape
        elif var == 's':
            self.siz = self.gui.data['s'].astype(float)
            self.siz  = self.siz/ float(self.siz.max()) * 400. #normalize size of marker
#            print 'size: ',  self.siz.shape
        elif var == 'c':
            self.col = self.gui.data['c'].astype(float)

    def update_scale(self):
        """
        Resets the log scales if necessary
        :return:
        """
        if self.gui.logscale[0]:
            self.ax.set_xscale('log')
        if self.gui.logscale[1]:
            self.ax.set_yscale('log')

    def scatter_plot(self, x, y, s, c):
        """generates the scatter plot"""
        c = [i[0] for i in c.T]
#        xshape = x.shape
#        print "x,y,c: ", x.shape, y.shape, len(c)
        sc = self.ax.scatter(x, y, s, c, marker='o', alpha=0.6, edgecolors='none')
        self.ax.set_xlim(self.xlims)
        self.ax.set_ylim(self.ylims)
#        if sum(self.gui.logscale) > 0:
#            self.update_scale()
        self.ax.hold(True)
#        annots = dict([((X, Y),(L, S)) for X, Y, L, S in zip(x, y, self.gui.all_data['entity_levels'], s)])
#        self.colorbar(self.ax)
#        DataCursor(sc, annots=annots)
#        print x, y
#        print x.shape, y.shape

    def scatter_trail(self, x, y, c):
        """
        Generates  trail of semi-tranaparent dots for the movement of the scatter bubbles
        :param x: x series
        :param y: y series
        :param c: color
        :return:
        """
        c = [i[0] for i in c.T]
        self.ax.plot(x,y,'b:', lw=2, alpha=0.2, aa=True)
        if sum(self.gui.logscale) > 0:
            self.update_scale()
        self.ax.grid(True)
        self.ax.hold(False)

    def bar_plot(self, h, c):

        c = [i[0] for i in c.T]
        cols = cm.prism(c)
        pos = range(self.gui.num_ent)
        self.ax.bar(left=pos, height=h, color=cols, edgecolor=cols)
        self.ax.set_xticks(pos)
        self.ax.set_xticklabels(self.gui.all_data['entity_levels'], rotation="vertical", size='xx-small')

    def line_plot(self, t, y):
        self.ax.plot(t, y)
        self.ax.set_xlabel('time')
    
    def rescale_axis(self,  axis = 'x'):
        
        if axis == 'x':
            lims = [float(lim) for lim in self.xlims] # Important because Numpy.isfinite chokes on Decimal types
            self.ax.set_xlim(*lims)
        if axis == 'y':
            lims = [float(lim) for lim in self.ylims] # Important because Numpy.isfinite chokes on Decimal types
            self.ax.set_ylim(*lims)
        self.draw()
            
    def compute_figure(self, t):
        """Creates figures at time t"""
        self.ax.cla()

        if self.typ == 'scatter':
#            Pr = Process(target=self.scatter_plot,args=(self.x[t, :], self.y[t, :], self.siz[ t, :], self.col))

#            xshape = self.x.shape
#            yshape = self.y.shape
#            xsentshaoe = self.x[t, :].shape
            self.scatter_plot(self.x[t, :], self.y[t, :], self.siz[ t, :], self.col)
            self.scatter_trail(self.x[:t+1, :], self.y[:t+1, :],self.col)
        elif self.typ == 'bar':
            self.bar_plot(self.siz[t, :], self.col)
        elif self.typ == 'line':
#            Tr = Thread(target=self.line_plot,args=(self.gui.data['t'][:t+1], self.y[:t+1, :]))
#            Tr.start()
            self.line_plot(self.gui.data['t'][:t+1], self.y[:t+1, :])
        self.draw()

def line_plot(ax,t,y):
    ax.plot(t, y)
    ax.set_xlabel('time')

class DataCursor(object):
    """A simple data cursor widget that displays the x,y location of a
    matplotlib artist when it is selected."""
    def __init__(self, artists, tolerance=5, offsets=(-20, 20), 
                 template='%s: %0.1f',annots=None,  display_all=False):
        """
        Create the data cursor and connect it to the relevant figure.
        :parameters:
        :param artists: is the matplotlib artist or sequence of artists that will be selected. 
        :param tolerance: is the radius (in points) that the mouse click must be within to select the artist.
        :param offsets: is a tuple of (x,y) offsets in points from the selected point to the displayed annotation box
        :param template: is the format string to be used. Note: For compatibility with older versions of python, this uses the old-style (%)  formatting specification.
        :param annots: Annottation dictionary per point (x,y)
        :param display_all: controls whether more than one annotation box will be shown if there are multiple axes.  Only one will be shown per-axis, regardless. 
        """
        self.template = template
        self.offsets = offsets
        self.annots = annots
        self.display_all = display_all
        if not cbook.iterable(artists):
            artists = [artists]
        self.artists = artists
        self.axes = tuple(set(art.axes for art in self.artists))
        self.figures = tuple(set(ax.figure for ax in self.axes))

        self.annotations = {}
        for ax in self.axes:
            self.annotations[ax] = self.annotate(ax)

        for artist in self.artists:
            artist.set_picker(tolerance)
        for fig in self.figures:
            fig.canvas.mpl_connect('pick_event', self)

    def annotate(self, ax):
        """Draws and hides the annotation box for the given axis "ax"."""
        annotation = ax.annotate(self.template, xy=(0, 0), ha='right',
                xytext=self.offsets, textcoords='offset points', va='bottom',
                bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5),
                arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0')
                )
        annotation.set_visible(False)
        return annotation

    def __call__(self, event):
        """Intended to be called through "mpl_connect"."""
        # Rather than trying to interpolate, just display the clicked coords
        # This will only be called if it's within "tolerance", anyway.
        x, y = event.mouseevent.xdata, event.mouseevent.ydata
        annotation = self.annotations[event.artist.axes]
        if x is not None:
            if not self.display_all:
                # Hide any other annotation boxes...
                for ann in self.annotations.values():
                    ann.set_visible(False)
            # Update the annotation in the current axis..
            annotation.xy = x, y
            annotation.set_text(self.template % self.annots[(x, y)])
            annotation.set_visible(True)
            event.canvas.draw()

if __name__=="__main__":
    import sys
    from PyQt4 import QtGui
    app = QtGui.QApplication(sys.argv)
    t = np.arange(1, 101)
    x = np.random.random((len(t), 3))
    y = np.random.random((len(t), 3))
    s = np.array([np.sin(t) / t + 1, np.cos(t) / t + 1, np.sin(t) + 1]).T
    print s.shape
    MC = MotionChart(None, None, {'t': t,'x': x, 'y': y, 's': s,
                                  'c': ['r', 'g', 'b'], 'entity_levels': []})
    MC.colorCombo.addItems(['c'])
    MC.sizeCombo.addItems(['s', 'y', 'x'])
    MC.yVarCombo.addItems(['y', 'x', 's'])
    MC.xVarCombo.addItems(['x', 'y', 's'])
    MC.timeCombo.addItems(['t'])
    MC.show()
    sys.exit(app.exec_())
