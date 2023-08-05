# -*- coding: utf-8 -*-
"""
Module implementing MainWindow.
"""
#-----------------------------------------------------------------------------
# Name:        main.py
# Project:  HiDX
# Purpose:
#
# Author:      Flávio Codeço Coelho<fccoelho@gmail.com>
#
# Created:     2010-05-12
# Copyright:   (c) 2010 by the Author
# Licence:     GPL
#-----------------------------------------------------------------------------

import os
import datetime
from itertools import count
from ConfigParser import SafeConfigParser
from PyQt4.QtCore import pyqtSignature,  QString
from PyQt4.QtGui import (QMainWindow, QFileDialog, QTreeWidgetItem,
                         QTableWidgetItem, QMessageBox, QInputDialog,  QWidget)
from sqlalchemy.ext.sqlsoup import SqlSoup
from sqlalchemy import distinct
import numpy as np
from numpy import array, zeros
from Ui_main import Ui_MainWindow
from dbserver import OpenDb
import dbf
import pandas as pd
from viz import scatmat
from viz.motionchart import MotionChart
from aboutHiDX import AboutDialog

__docformat__ = "restructuredtext en"


class MainWindow(QMainWindow, Ui_MainWindow):
    """
    Class documentation goes here.
    """
    def __init__(self, parent = None):
        """
        Constructor
        """
        QMainWindow.__init__(self, parent)
        self.setupUi(self)
        self.treeWidget.headerItem().setText(0, self.trUtf8("Tables"))
        self.treeWidget.headerItem().setText(1, self.trUtf8("Records"))
        self.treeWidget.setColumnCount(2)
        self.dbs = {}
        self.config = SafeConfigParser()
        self.load_prefs()
        self.currentdb = None
        self.currentdbname = None
        self.currentTable = None
        self.currentVarNames = []
        self.currentVarTypes= {} #variable types in current table
        self.currentTableName = None
        
    def save_prefs(self, opts=[]):
        """
        opts must a list of  triplets ('session','var','value')
        """
        cpath = os.path.join(os.environ['HOME'], '.hidx.conf')
        for o in opts:
            self.config.set(*o)
        with open(cpath, 'wb') as configfile:
            self.config.write(configfile)
            
    def load_prefs(self):
        cpath = os.path.join(os.environ['HOME'], '.hidx.conf')
        if os.path.exists(cpath):
            self.config.read(cpath)
        else:
            self.config.add_section('Connections')
            self.save_prefs([('Connections', 'server', 'mysql'),
                             ('Connections', 'username', ''),
                             ('Connections', 'passwd', ''),
                             ('Connections', 'host', 'localhost'),
                             ('Connections', 'port', '')])
    
    def open_sqlite_db(self, fname):
        '''
        Opens an SQLite database
        '''
        db = SqlSoup('sqlite:///%s' % fname)
        self.currentdb = db
        dbname = os.path.split(fname)[1]
        if dbname in self.dbs: #Avoid name conflict
            for i in count(1, 1):
                if dbname + '_%s' % i not in self.dbs:
                    dbname += '_%s' % i
                    break
        self.currentdbname = dbname
        tables = db.bind.table_names()
        self.dbs[dbname] = (db, tables)
        self.fill_open_db_tree(dbname, tables)
        
    def open_csv(self, fname):
        """
        Opens a CSV file
        :param fname: Name of the csv file to be opened
        :return: None
        """
        #TODO: implement a GUI for specifying details about the loading of csv
        #      such as separators, headers, etc.
        db = pd.read_csv(fname)
#        db = np.genfromtxt(fname)
        self.currentdb = db
        self.currentdbname = fname
        tables = [fname]
        self.dbs[self.currentdbname] = (db, tables)
        #TODO: make sure that all actions related with reading from databases works for csv as
        self.fill_open_db_tree(self.currentdbname, tables)

    def open_dbf(self,fname):
        """
        Opens a dbf file
        :param fname: Name of the dbf file
        :return:
        """
        db = dbf.Table(fname)
        self.currentdb = db
        self.currentdbname = fname
        tables = [fname]
        self.dbs[self.currentdbname] = (db, tables)
        self.fill_open_db_tree(self.currentdbname, tables)

    def open_mysql(self, user, password, host, database, port=3306):
        """
        Open a connection to a MySQL database

        :param user: User with read permissio to the database
        :param password: Password for the user
        :param host: Host of the MySQL server
        :param database: Database name
        :param port: Port of MySQL server
        :return: None
        """
        db = SqlSoup('mysql://%s:%s@%s:%s/%s' % (user, password, host, port,
                                                 database))
        self.currentdb = db
        self.currentdbname = database
        tables = db.bind.table_names()
        self.dbs[self.currentdbname] = (db, tables)
        self.fill_open_db_tree(self.currentdbname, tables)

    def get_table_items(self, dbname, dbw, tables):
        """
        fetch table items from db or file
        :param dbname: name of db or csv/dbf file
        :param dbw: db widget object
        :param tables: list of table names
        :return: list of tableitem objects
        """
        tableitems = []
        for table in tables:
            if dbname.endswith(".dbf"):
                self.currentdb.open()
                table_size = self.get_table_size(self.currentdb,table,kind="dbf")
                table = os.path.split(table)[-1]
            elif dbname.endswith(".csv"):
                table_size = self.get_table_size(self.currentdb,table,kind="csv")
            else:
                table_size = self.get_table_size(self.currentdb,table,kind="sql")
            t_item = QTreeWidgetItem(dbw, [table])
            t_item.setText(1, str(table_size))
            t_item.setToolTip(0, QString(str(table)))
            tableitems.append(t_item)
        return tableitems

    def fill_open_db_tree(self, dbname, tables):
        """
        Fills the tree widget with details of an opened db
        """
        dbw = QTreeWidgetItem([dbname]) #DB widget
        self.treeWidget.insertTopLevelItem(self.treeWidget.topLevelItemCount(),
                                           dbw)
        tableitems = self.get_table_items(dbname, dbw, tables)
            
        self.statusBar.showMessage(self.trUtf8("Database %s opened" % dbname))
        
    def get_table_size(self, db, table, kind="sql"):
        """
        finds out tablesize
        :param db: db object
        :param table: table to be inspected
        :param kind: type of db: "sql","csv","dbf"
        :return: size (int)
        """
        if kind == "dbf":
            db.open()
            n = 0
            for record in  self.currentdb:
                n  += 1
            table_size = n
            db.close()
        elif kind == "csv":
            table_size = db.shape[0]
        elif kind == "sql":
            sql = 'SELECT COUNT(*) FROM ' + table
            table_size = db.bind.execute(sql).fetchall()[0][0]
            db.flush()
        return table_size

    def read_table_data(self, db, offset, rows, table):
        """

        :param db:
        :param offset:
        :param rows:
        :param table:
        :return: list of lists
        """
        if self.current_db_kind == "sql":
            sql = 'SELECT * FROM %s LIMIT %s OFFSET %s' % (table, rows, offset)
            r = db.bind.execute(sql)
            data = r.fetchall()
            db.flush()
        elif self.current_db_kind == "dbf":
            self.currentdb.open()
            data = [[i for i in record] for record in self.currentdb]
            self.currentdb.close()
        elif self.current_db_kind == "csv":
            data = db.as_matrix().tolist()

        return data

    def fill_data_table(self, table, db, rows=None, offset=None):
        """
        Fill spreadsheet with data loaded from db.
        
        :Parameters:
            -`table`: table name
            -`db`: database object
            -`rows`: number of rows to load
            -`offset`: row number to start loading from.
        """
        if not rows:
            rows = self.rowNumber.value()
        if not offset:
            offset = self.rowStart.value()
        data = self.read_table_data(db, offset, rows, table)
        if len(data) == 0:
            QMessageBox.information(None, self.trUtf8("Empty Table"),
                                    self.trUtf8("Table %s is empty" % table),
                                    QMessageBox.StandardButtons(QMessageBox.Ok))
            return
        self.tableWidget.setRowCount(len(data))
        self.tableWidget.setColumnCount(len(data[0]))
        self.tableWidget.setHorizontalHeaderLabels(self.currentVarNames)
        for i, line in enumerate(data):
            for j, v in enumerate(line):
                it = QTableWidgetItem(str(v))
                tooltip = '%s: type: %s' % (self.currentVarNames[j],
                        self.currentVarTypes[self.currentVarNames[j]])
                it.setToolTip(self.trUtf8(tooltip))
                self.tableWidget.setItem(i, j, it)
                
    def assemble_series(self):
        """
        Assembles series array to link with parameter replicates
        """
        #TODO: generalize this. This is specific to MCMC data
        dates = [d[0] for d in self.currentdb.bind.execute('select time from data').fetchall()]
        reps = self.currentdb.bind.execute('select count(*) from series').fetchall()[0][0]/float(len(dates))
        #aggregate series data
        series = {}
        r = self.currentdb.bind.execute('select * from series')
        cnames = r.keys()
        self.currentdb.flush()
        for c in cnames:
            if c in ['pk', 'time']:continue
            r = self.currentdb.bind.execute('select %s from series'%c)
            series[c] = array(r.fetchall())
            series[c].shape = (reps, len(dates))
            self.currentdb.flush()
        return series
    
    def get_column_data(self):
        """
        Returns whole chunks of data (as a numpy array) and their headers
        (as a list of strings) from the spreadsheet
        """
        #TODO: handle datetime columns
        table = self.tableWidget
        sr = table.selectedRanges()
        try:
            if len(sr) == 1:
                sel = sr[0]
                cols = range(sel.leftColumn(), sel.rightColumn() + 1)
            else: # more than one range (non-contiguous selection)
                cols = []
                for s in sr:
                    cols += range(s.leftColumn(), s.rightColumn() + 1)
        except IndexError:
            #when there's no selection
            QMessageBox.warning(None, self.trUtf8("No Data to Plot"),
                self.trUtf8("Please select at least one column to plot."),
                QMessageBox.StandardButtons(QMessageBox.Ok))
            return None, None

        nms = [str(table.horizontalHeaderItem(c).text()) for c in cols]
        data = zeros((table.rowCount(), len(cols)))
        k = 0
        l = 0
        for i in xrange(0, table.rowCount()):
            for j in cols:
                data[k, l] = float(table.item(i, j).text())
                l += 1
            k += 1
            l = 0
        return data, nms
    
    def get_motion_chart_data(self, entity,  tvars):
        """
        Query database to fetch data and return it formatted for motion chart
        plots
        """
        db_table =  self.currentdb.entity(self.currentTableName)
        rows =self.rowNumber.value()
        offset = self.rowStart.value()
        session = self.currentdb.session()
        #find all levels of entity variable
        entities = session.query(distinct(db_table.c[entity]))[:]#[offset:offset + rows]
        entities = [e[0] for e in entities] # levels of the entity variable
        vars = self.currentVarNames
        vars.remove(entity) #variables names
        sel = [db_table.c[v] for v in vars]
        table = []
        # table is a list of data by level of the variable entity, so that we
        # can generate the multiple time series at the motion chart
        for e in entities:
            q = session.query(*sel).filter(db_table.c[entity] == e)
            for t in tvars:
                q = q.filter(db_table.c[t] != None) #Avoid records without a date/time
            res = q[:]#[offset:offset + rows]
            if res: #Only store if there are results
                table.append(np.array(res))
            else:
#                print e
                entities.remove(e)

        return entities, vars, table
    
    @pyqtSignature("")
    def on_action_Connect_activated(self):
        """
        Called when a connect to file action is triggered
        """
        fname = str(QFileDialog.getOpenFileName(\
            None,
            self.trUtf8("Connect to Database"),
            QString(),
            self.trUtf8("Database files(*.sqlite *.dbf *.csv)"),
            None))
        if fname.endswith('.sqlite'):
            self.open_sqlite_db(fname)
        elif fname.endswith('.csv'):
            self.open_csv(fname)
        elif fname.endswith('.dbf'):
            self.open_dbf(fname)

    def get_var_types(self, table, kind):
        if kind == "sql":
            sql = 'SELECT * FROM %s LIMIT 1' % table
            q = self.currentdb.bind.execute(sql)
            self.currentVarNames = vnames = q.keys()
            res = q.fetchone()
            if res != None:
            #only if there are rows in the table
                self.currentVarTypes = dict([(n, type(i)) for i, n in zip(res, vnames)])
            self.currentdb.flush()
        elif kind == "csv":
            self.currentVarNames = vnames =  self.currentdb.columns.tolist()
            self.currentVarTypes = dict(zip(vnames,self.currentdb.dtypes.tolist()))
        elif kind == "dbf":
            self.currentdb.open()
            self.currentVarNames = vnames = self.currentdb.field_names
            self.currentVarTypes = dict([(field,self.currentdb.field_info(field)[0]) for field in vnames])
            self.currentdb.close()

    @pyqtSignature("QTreeWidgetItem*, int")
    def on_treeWidget_itemClicked(self, item, column):
        """
        Handles reading of the database table when the a table is selected
        """
        if self.currentdbname.endswith(".dbf"):
            kind = "dbf"
        elif self.currentdbname.endswith(".csv"):
            kind = "csv"
        else:
            kind = "sql"
        self.current_db_kind = kind
        if item == self.currentTable:
            return # no need to reread the table
        itemname = str(item.text(0))
        if item.childCount(): #if it has children it is a database
            message = "Database %s selected." % itemname
            self.statusBar.showMessage(self.trUtf8(message))
            dbname = str(item.text(0))
            db = self.dbs[dbname][0]
            self.currentdb = db
            self.currentdbname = dbname
        else:
            message = "Table %s selected." % itemname
            self.statusBar.showMessage(self.trUtf8(message))
            self.tableWidget.clear()#;self.tableWidget.clearContents()
            dbname = str(item.parent().text(0))
            db = self.dbs[dbname][0]
            self.currentdb = db
            
            self.currentdbname = dbname
            self.currentTable = item
            self.currentTableName = itemname
            self.currentTableSize = self.get_table_size(self.currentdb,itemname,kind=kind)

            
            if self.currentTableSize !=0:
                #don't try to load data from empty tables
                # finding out variable types
                self.get_var_types(itemname,kind)
                self.rowStart.setMaximum(self.currentTableSize-1)
                self.rowNumber.setMaximum(self.currentTableSize-self.rowStart.value())
                self.fill_data_table(itemname, db)
                
    @pyqtSignature("")
    def on_actionScatterplot_Matrix_activated(self):
        """
        Generate scatterplot matrix from variables selected.
        """
        if not self.dbs:
            return
        db = self.currentdb
        data, pnames = self.get_column_data()
        if data == None:
            return
        pars = {}
        for i, p in enumerate(pnames):
#            if p in ['pk', 'time']:continue
            pars[p] = data[:, i]
            
        self.spm = scatmat.ScatMat(pars, self.currentdbname)
#        print "==>", self.spm.pw.isVisible()

        self.spm.pw.showMaximized()

#        print "==>", self.spm.pw.isVisible()
    
    @pyqtSignature("int")
    def on_rowStart_valueChanged(self, p0):
        """
        Fills data table with the number of rows specified.
        """
        if not self.currentTable:
            return #no table selected
        rows = self.rowNumber.value()
        off = self.rowStart.value()
        if self.currentTableSize != 0:
            self.fill_data_table(self.currentTableName, self.currentdb, rows,
                                 off)

    @pyqtSignature("int")
    def on_rowNumber_valueChanged(self, p0):
        """
        Fills data table with the number of rows specified.
        """
        if not self.currentTable:
            return #no table selected
        rows = self.rowNumber.value()
        off = self.rowStart.value()
        if self.currentTableSize != 0:
            self.fill_data_table(self.currentTableName, self.currentdb, rows,
                                 off)
    
    @pyqtSignature("")
    def on_actionConnect_to_Server_activated(self):
        """
        Open. Db server connection dialog
        """
        opdb = OpenDb(self)
        opdb.show()
    
    @pyqtSignature("")
    def on_actionMotion_Chart_activated(self):
        """
        Check data prerequisites and call motion chart
        """
        if not self.dbs:
            return

        tvars = [] #time variables
        for i in self.currentVarNames:
            if self.currentVarTypes[i] in (datetime.date, datetime.datetime):
                tvars.append(i)

        factors = [] #categorical variables
        for i in self.currentVarNames:
            if self.currentVarTypes[i] in (str, unicode ):
                factors.append(i)

        tcont = [] #numerical variables
        for i in self.currentVarNames:
            if self.currentVarTypes[i] in (int, float, long):
                tcont.append(i)

        it  = QInputDialog.getItem(\
            None,
            self.trUtf8("Entity Name"),
            self.trUtf8("Select variable with entity names"),
            factors,
            0, False)
        if not it:
            return
        if tvars ==[]:
            tv = str(QInputDialog.getItem(\
            None,
            self.trUtf8("Time variable"),
            self.trUtf8("Select variable with time values"),
            tcont,
            0, False)[0])
            tvars.append(tv)
        it = str(it[0])
        entities, vars,  data = self.get_motion_chart_data(it,  tvars)
        datadict = {}
        #concatenate series of each entity level by variable
        for i, n in enumerate(vars):
            datadict[n] = np.array([d[:, i] for d in data]).T

#        print datadict['geocode'].shape, datadict['geocode'][1]
#        print len(datadict)
        datadict['entity'] = it
        datadict['entity_levels'] = entities
        if it in factors:
            factors.remove(it)

        if tvars and len(tcont) >= 2:
            self.MC = MotionChart(data=datadict, t_steps=datadict[tvars[0]].shape[0])
            self.MC.colorCombo.addItems(factors)
            self.MC.sizeCombo.addItems(tcont)
            self.MC.yVarCombo.addItems(tcont)
            self.MC.xVarCombo.addItems(tcont)
            self.MC.timeCombo.addItems(tvars)
            self.MC.show()
        else:
            print self.currentVarNames, self.currentVarTypes
            print tvars, factors, tcont
    
    @pyqtSignature("")
    def on_actionE_xit_activated(self):
        """
        Exit the application.
        """
        try:
            self.MC.close()
        except AttributeError:
            pass
        self.close()
        
    @pyqtSignature("")
    def on_actionAbout_HiDX_activated(self):
        """
        Shows the about dialog
        """
        ad = AboutDialog(self)
        ad.show()
    
    @pyqtSignature("")
    def on_actionReload_activated(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        raise NotImplementedError
    
    @pyqtSignature("")
    def on_actionHelp_activated(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        raise NotImplementedError
