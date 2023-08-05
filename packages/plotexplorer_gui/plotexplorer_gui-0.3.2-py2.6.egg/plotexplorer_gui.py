"""
Copyright (c) 2012, Robert Steed
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

    * Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
"""
Robert Steed (rjsteed@talk21.com)
License: BSD 2-clause
last modified 22.08.2012

This script creates a matplotlib graph along side a chooser for cases where there are many similar plots to 
compare and explore. 

To use this script as a plotting module simply import the class DataExplorer and use as follows

DataExplorer(data,redirect=False) #initialise
app.MainLoop() # run

where data is a dictionary of data with each entry key being some text and each value being a tuple of x and y arrays 
ie. {'text to display in chooser':(x_array,y_array)}. Alternatively, each key can be a tuple in which case the chooser will 
be multiple columned and sortable ie. {('label1','label2',float,int):(x_array,y_array)}. But if you are using tuples for keys 
then all must be the same length!

Options: DataExplorer(data,fits=None,labels=None,styles=None,title="plotexplorer",redirect=False)

labels: A tuple which must contain (xlabel,ylabel,columnhdr). Columnhdr will be a tuple of entries that describes your 
entry fields for the data dictionary's keys and is used to label the columns of the checkbox list.

styles: A dictionary that can override the default style of a plot if you add an entry with the appropriate key.

fits: A dictionary of functions of one variable which must be the xaxis. If there is an entry in this dictionary for a given 
plot's key then this function will be plotted along with the original data.

title: Sets text of window title bar.

---
Pressing x when using the plot should make the xaxis logarythmic.
"""

import wx
from wx.lib.mixins.listctrl import ColumnSorterMixin,CheckListCtrlMixin

import numpy as N
#import matplotlib
#matplotlib.use('WxAgg')
from matplotlib import use as pluse
pluse('WxAgg')
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wxagg import NavigationToolbar2WxAgg
from matplotlib.figure import Figure
#import pylab as pl

class plotchooser(wx.ListCtrl,CheckListCtrlMixin,ColumnSorterMixin): #customised ListCtrl class
    """the listctrl stores entries with multiple columns. The ColumnSorterMixin allows the entries to be sorted with respect to different columns
    and the checklistctrlMixin adds a check box to each entry. The class will tell you an entries index but since these change with each reordering
    we need to store some data with each entry in order to work out which plot it refers to"""
    def __init__(self,parent,colnum):
        wx.ListCtrl.__init__(self,parent,-1,style=wx.LC_REPORT) #initialises ListCtrl
        CheckListCtrlMixin.__init__(self) #initialises mixin check box class
        ColumnSorterMixin.__init__(self,colnum) #initialises mixin column sorter class with initial number of columns =colnum
        #
        self.itemDataMap={} #needed by ColumnSorterMixin for sorting the columns. A dictionary with a tuple of values for each column indexed using the data stored in each keys entry
    
    def GetListCtrl(self): #needed for sorting the columns
        return self
    
    def GetSecondarySortValues(self, col, key1, key2): #improving the column sorting
        """Returns a tuple of 2 values to use for secondary sort values when the
           items in the selected column match equal.  The default just returns the
           item data values."""
        item1=self.itemDataMap[key1] # tuple1 of the independent variables
        item2=self.itemDataMap[key2] # tuple2 of the independent variables
        #col is the column chosen to sort the entries.
        items=zip(item1,item2)
        for i1,i2 in items[col+1:]+items[:col]: #list all columns on right of col and looping round (stopping one before col)
            if i1!=i2:
                return (i1,i2)
        #failsafe
        return (key1, key2)
    
    def OnCheckItem(self, index, flag): #runs whenever a checkbox is clicked
        key=self.GetItemData(index)
        address=self.itemDataMap[key]
        self.GetParent().GetParent().GetParent().plotshow(address,flag) #runs the plotshow function in DataExplorer
    
    def refreshColumns(self,columnhdr): #updates the number and name of columns to reflect columnhdr
        self.DeleteAllColumns()  #easier than anything else. -but what happens to the entries?
        for hdr in columnhdr:
            self.InsertColumn(1e6,hdr,width=80)
    
    def refreshEntries(self,plotset): #changes the listctrl's entries to those of plotset.
        self.DeleteAllItems() #delete current entries (but not column headers I hope)
        for address in plotset:
            index = self.InsertStringItem(1e6,'blaah') # a foo entry just to create the unique index.  Because InsertStringItem doesn't work for multiple columned sorters (?)
            for i,ad in enumerate(address):
                self.SetStringItem(index,i,str(ad)) #enter text for each column 
            self.SetItemData(index,index) #stores the original index with the entry in order to retrieve its 'address' for extracting the plot from the data.
            self.itemDataMap[index]=address #dictionary for looking up address tuple from initial index.
            #clear checkboxes??


class DataExplorerGUI(wx.Frame):
    def __init__(self,data,fits,labels,styles,parent,id,title):
        """a gui for exploring data stored in dictionary 'data'. 
        data = a dictionary of x,y arrays to plot where the keys are tuples (of equal length)"""
        ## initialise parent class
        wx.Frame.__init__(self,parent,id,title,size=(380,230))
        ## Q1. Are data keys strings or tuples
        strkeys=sum([1 for i in data if type(i) in (type(''),type(0),type(float()))]) #count number of string keys (or int or float)
        tplkeys=sum([1 for i in data if type(i) in (type(()),type([]))]) #count number of tuple or list keys
        assert min(strkeys,tplkeys)==0 #check that there isn't a mixture of key types
        if strkeys==len(data): #just another check that all keys are strings in this case.
            tmp={}
            for key,value in data.items():
                tmp[key,]=value #turn strings keys into single length tuples
            data=tmp 
            del(tmp)
            self.cols=cols=1
        elif tplkeys==len(data):
            self.cols=cols=len(data.keys()[0])
            assert len([False for i in data.keys() if len(i)!=cols])==0 #check that all keys have the same number of columns
        #
        self.data=data #data dictionary. Keys are either strings or tuples.
        #
        if fits!=None: self.fits=fits #often will = None
        else: self.fits={}
        ##Q2. Are there any labels given
        if labels!=None:
            assert len(labels)==3 #check that there are 3 items in labels
            if type(labels[2])not in (type(()),type([])):
                assert cols==1
            else:
                assert len(labels[2])==cols # check that the columnhdrs entry is the same length as the data dictionary key tuples.
        else:
            labels=['','',['A','B','C','D','E','F','G'][:cols]]
        #
        if styles!=None: self.styles=styles #often will = None
        else: self.styles={}        
        #
        self.Plots1={}
        self.FPlots1={} # Fit plots
        self.showlegend=False
        self.stop_refresh_hack=False
        
        #### Set up panels
        splitter=wx.SplitterWindow(self,-1)
        leftpanel=wx.Panel(splitter,-1)
        rightpanel=wx.Panel(splitter,-1)
        
        #### Set up Objects
        self.plotchooser = plotchooser(rightpanel,cols) #setup Plotchooser widget
        self.plotchooser.refreshColumns(labels[2]) #update column headers
        self.plotchooser.refreshEntries(data.keys()) #update entries and clear checkboxes
        #
        self.selectall=wx.Button(rightpanel,-1,"Select All")
        self.Bind(wx.EVT_BUTTON, self.plotall,self.selectall)
        #
        self.fig=Figure()
        self.canvas=FigureCanvas(leftpanel,-1,self.fig)
        self.ax1=self.fig.add_subplot(111) #plot
        self.ax1.set_xlabel(labels[0])
        self.ax1.set_ylabel(labels[1])
        self.fig.subplots_adjust(left=0.1, bottom=0.07, right=0.95, top=0.95)
        self.toolbar=NavigationToolbar2WxAgg(self.canvas)
        self.bsavedata=wx.Button(leftpanel,-1,"Save Data")
        self.Bind(wx.EVT_BUTTON, self.savedata,self.bsavedata)
        self.legendch=wx.CheckBox(leftpanel,-1,"Show Legend")
        self.Bind(wx.EVT_CHECKBOX, self.evt_legendch,self.legendch)
        self.cursorPos=wx.StaticText(leftpanel,-1,"x=0.000000 \ny=0.000000  ",style=wx.ALIGN_LEFT)
        self.canvas.mpl_connect('motion_notify_event', self.UpdateStatusBar)
        #
        self.canvas.mpl_connect('key_press_event', self.press)
        #### Do layout
        vbox1=wx.BoxSizer(wx.VERTICAL)
        vbox1.Add(self.canvas,15,wx.EXPAND)
        hbox2=wx.BoxSizer(wx.HORIZONTAL)
        hbox2.Add(self.toolbar,1,wx.LEFT|wx.EXPAND)
        hbox2.Add(self.bsavedata,0,wx.ALL,border=6)        
        hbox2.Add(self.legendch,0,wx.ALL,border=6)
        hbox2.Add(self.cursorPos,0,wx.ALIGN_RIGHT|wx.LEFT|wx.RIGHT,border=6)
        vbox1.Add(hbox2,1,wx.EXPAND)
        leftpanel.SetSizer(vbox1)
        vbox2=wx.BoxSizer(wx.VERTICAL)
        vbox2.Add(self.plotchooser,2,wx.EXPAND)
        vbox2.Add(self.selectall,0,wx.ALL,border=6)
        rightpanel.SetSizer(vbox2)
        splitter.SplitVertically(leftpanel,rightpanel,-150)
        splitter.SetMinimumPaneSize(50)
        splitter.SetSashGravity(0.5)
        topsizer = wx.BoxSizer(wx.HORIZONTAL)
        topsizer.Add(splitter, 1, wx.EXPAND)
        self.SetSizer(topsizer)
        topsizer.Fit(self)
        
        #### final initialisation
        self.toolbar.update()
        #self.Centre()
        self.Show(True)
            
    def plotshow(self,address,show,refresh_canvas=True): #function gets run every time a checkbox is ticked or unticked in the plotchooser widget.
        label=' '.join([str(j) for j in address]) #create label from address for use in legend
        #
        ax,Plots,FPlots =self.ax1,self.Plots1,self.FPlots1
        if show:
            fitfunc=self.fits.get(address,None) #get/check whether there is a fitting function
            x,y=self.data[address] #get raw data points
            if type(fitfunc)!=type(None): style='x' #change style of data plot depending on presence of fit.
            else: 
                style=self.styles.get(address,'-') #'x-'
            line,=ax.plot(x,y,style,label=label) #plot data
            Plots[address]=line #add plot reference to a dictionary
            # Plotting Fits
            if type(fitfunc)!=type(None):
                xlen=x[-1]-x[0] 
                x2=N.linspace(x[0]-0.25*xlen,x[-1]+0.25*xlen,50) #create array of x axis points (50% bigger than spread in data points)
                y2=fitfunc(x2) # evaluate fitting curve
                cr=line.get_color() #get colour of data plot
                line2,=ax.plot(x2,y2,'-'+cr,label="_nolegend_") # plot data - colour??
                FPlots[address]=line2 #add plot reference to a dictionary                
        else: #removing plots
            line=Plots[address] # get plot reference
            ax.lines.remove(line) #delete line
            del(Plots[address]) #delete plot reference from dictionary
            #
            if FPlots.has_key(address): #remove fitting plot too
                line=FPlots[address]
                ax.lines.remove(line)
                del(FPlots[address])
        
        ### refreshing plots
        #autoscaling?? ax.relim - resets bounds to current data. Or use ax.setautoscaleon=False
        if self.ax1.lines!=[] and self.showlegend:
            self.ax1.legend()#ax2.legend(title=self.dobj.columnhdr())
        else:
            #for ax in ax1,ax2: ax.legend_=None                
            self.ax1.legend_=None
        if self.stop_refresh_hack!=True: self.canvas.draw() # redraw canvas
        
    def evt_legendch(self,event):
        ch=event.IsChecked()
        self.showlegend=ch
        if ch and self.ax1.lines!=[]:
            self.ax1.legend()#ax2.legend(title=self.dobj.columnhdr())
        else:               
            self.ax1.legend_=None
        self.canvas.draw() #
        
    def plotall(self,event):
        pch=self.plotchooser
        self.stop_refresh_hack=True
        for index in range(pch.ItemCount):
            flag=True
            pch.CheckItem(index, flag)#check all items in plotchooser
            #if index%10==0: print index
        self.stop_refresh_hack=False
        self.canvas.draw()
        
    def savedata(self,event):           
        #saving visible data
        wildcard = "csv file (*.csv)|*.csv|" \
            "All files (*.*)|*.*"
        delimiter=','
        
        dlg = wx.FileDialog( self, message="Save file as ...", #defaultDir=self.currentDirectory, 
                defaultFile="", wildcard=wildcard, style=wx.SAVE)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            #which curves are visible?
            Plotted =self.Plots1.keys()
            #create a csv file of the visible data
            data =self.data
            visdata=sum([list(data[address]) for address in Plotted],[])
            lengths=[len(array) for array in visdata]
            maxlen=max(lengths)
            visdata=[N.resize(array,(maxlen,)) for array in visdata] #making all arrays the same length
            for array,length in zip(visdata,lengths): array[length:]=0.0 #N.resize() repeats the array rather than zero filling which I don't want.
            visdata=N.column_stack(visdata)
            #columnheaders 
            #the data addresses are tuples, each entry will go on a separate line 
            colhdr = [[str(Plotted[i][j]) for i in range(len(Plotted))] for j in range(len(Plotted[0]))]
            colhdr = [delimiter.join(sum([[i,i] for i in line],[]))+'\n' for line in colhdr]
            #saving data
            fobj=file(path,'w')
            fobj.writelines(colhdr)
            N.savetxt(fobj,visdata,delimiter=delimiter,fmt='%.4g')
            fobj.close()
            
        dlg.Destroy()
        
    def press(self,event):
        if event.key=='x':
            cur=self.ax1.get_xscale()
            if cur=='linear':
                self.ax1.set_xscale('log')
            elif cur=='log':
                self.ax1.set_xscale('linear')
            self.ax1.relim()
            self.ax1.autoscale_view()
            self.canvas.draw()
    
    def UpdateStatusBar(self, event):
        if event.inaxes:
            x, y = event.xdata, event.ydata
            self.cursorPos.SetLabel("x= %.6g\ny= %.6g" %(x,y))

        
class DataExplorer(wx.App):
    def __init__(self,datadict,fits=None,labels=None,styles=None,title="plotexplorer",*pargs,**kwargs):
        self.data=datadict
        self.fits=fits
        self.labels=labels
        self.styles=styles
        self.title=title
        wx.App.__init__(self,*pargs,**kwargs)
    def OnInit(self):
        self.frame = DataExplorerGUI(self.data,self.fits,self.labels,self.styles,None,-1,self.title)
        self.frame.Show(True)
        return True

if __name__=='__main__':
    data1={'This':(N.arange(10),N.arange(10)**2), 'Is':(N.arange(3,15,1),50*N.sin(N.arange(3,15,1)))}
    data2={('This','Is'):(N.arange(10),N.arange(10)**2),('Another','test'):(N.arange(3,15,1),50*N.sin(N.arange(3,15,1)))}
    labels1=('work','fun',('mango',))
    labels2=('work','fun',('freq','mango'))
    app=DataExplorer(data1,fits=None,labels=labels1,redirect=False)
    app.MainLoop()
