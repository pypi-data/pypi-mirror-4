
"""
<name>rSVD</name>
<description>Robust Singular Value Decomposition</description>
<icon>icons/NMF.png</icon>
<priority>30</priority>
"""


import numpy as np
import scipy.stats

#import sys
#sys.path.append("C:\\Python27\\Lib\site-packages\\Orange\\OrangeWidgets")
#sys.path.append("C:\\Users\\Fajwel\\Dropbox\\Orange\\rSVD")
import rSVD
from OWWidget import *
import OWGUI
import re, os.path
from exceptions import Exception


class OWrSVD(OWWidget):
    settingsList = ['rank','maxIter','nTrial','method','saveOutputs',"recentFiles","selectedFileName"]
    # things for saving:    
    savers = {".txt": orange.saveTxt, ".tab": orange.saveTabDelimited,
              ".names": orange.saveC45, ".test": orange.saveC45, ".data": orange.saveC45,
              ".csv": orange.saveCsv
              }

    # exclude C50 since it has the same extension and we do not need saving to it anyway
    registeredFileTypes = [ft for ft in orange.getRegisteredFileTypes() if len(ft)>3 and ft[3] and not ft[0]=="C50"]

    dlgFormats = 'Tab-delimited files (*.tab)\nHeaderless tab-delimited (*.txt)\nComma separated (*.csv)\nC4.5 files (*.data)\nRetis files (*.rda *.rdo)\n' \
                 + "\n".join("%s (%s)" % (ft[:2]) for ft in registeredFileTypes) \
                 + "\nAll files(*.*)"

    savers.update(dict((lower(ft[1][1:]), ft[3]) for ft in registeredFileTypes))
    re_filterExtension = re.compile(r"\(\*(?P<ext>\.[^ )]+)")
    
    def __init__(self, parent=None, signalManager=None):
        OWWidget.__init__(self, parent, signalManager, 'rSVD')
        
        self.inputs = [("Data", ExampleTable, self.dataX),("Xd", ExampleTable, self.dataXd),("Xa", ExampleTable, self.dataXa)]
        self.outputs = [("U", ExampleTable), ("V", ExampleTable),("D", ExampleTable),("UDV",ExampleTable),("Residuals",ExampleTable),("qqplot",ExampleTable)]
        
        self.rank=5
        self.nTrial=10
        self.maxIter=200
        self.method=0
        self.saveOutputs=1
        
        # things for saving
        self.recentFiles=[]
        self.selectedFileName = "None"
        self.data = None
        self.filename = ""  
        
        self.loadSettings()

        # GUI
        box = OWGUI.widgetBox(self.controlArea, "Info")
        self.infoa = OWGUI.widgetLabel(box, 'No data on input yet, waiting to get something.')
        self.infob = OWGUI.widgetLabel(box, '')

        OWGUI.separator(self.controlArea)
        self.paramBox = OWGUI.widgetBox(self.controlArea, "Parameters")
        OWGUI.spin(self.paramBox, self, 'rank', min=1, max=200, step=1,
                   label='Rank',labelWidth=150)
        OWGUI.lineEdit(self.paramBox, self, 'maxIter', label='Maximum number of iterations',labelWidth=150, orientation="horizontal")
        OWGUI.lineEdit(self.paramBox, self, 'nTrial', label='Number of trials',labelWidth=150, orientation="horizontal")
        self.methodBox = OWGUI.widgetBox(self.controlArea, "Method")        
        OWGUI.radioButtonsInBox(self.methodBox, self, 'method', callback=self.setNbIter,
              btnLabels = ["SVD", "rSVD LTS Global", "rSVD LTS Global Restricted"],
              tooltips = ["Singular Value Decomposition",
                          "Robust Singular Value Decomposition (LTS Global)",
                          "Robust Singular Value Decomposition (LTS Global Restricted)"])
    
        OWGUI.button(self.controlArea, self, "Commit", callback=self.commit)
        self.saveBox = OWGUI.widgetBox(self.controlArea, "Saving options")
        OWGUI.checkBox(self.saveBox, self, "saveOutputs", "Save outputs")
        rfbox = OWGUI.widgetBox(self.saveBox, "Filename", orientation="horizontal", addSpace=True)
        self.filecombo = OWGUI.comboBox(rfbox, self, "filename")
        self.filecombo.setMinimumWidth(200)
        button = OWGUI.button(rfbox, self, '...', callback = self.browseFile, disabled=0)
        button.setIcon(self.style().standardIcon(QStyle.SP_DirOpenIcon))
        button.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        self.resend = OWGUI.button(self.saveBox, self, "Retreive data", callback = self.resendData, default=True)
        
        OWGUI.rubber(self.controlArea)
        self.setFilelist()
        #self.resize(260,100)
        self.filecombo.setCurrentIndex(0)

        if self.selectedFileName != "":
            if os.path.exists(self.selectedFileName):
                self.openFile(self.selectedFileName)
            else:
                self.selectedFileName = ""      
        
        self.infob = OWGUI.widgetLabel(box, '')        
        self.paramBox.setDisabled(1)
        self.methodBox.setDisabled(1)
        self.saveBox.setDisabled(1)
        
        self.resize(100,50)        
        
    def dataX(self, dataset):
        if dataset:
            self.dataset = dataset
            self.infoa.setText('%d variables in input data set' % len(dataset[0]))
            self.infob.setText('%d observations in input data set' % len(dataset))
            self.rank = min(len(self.dataset),len(self.dataset[0]))            
            self.paramBox.setDisabled(0)
            self.methodBox.setDisabled(0)
            self.saveBox.setDisabled(0)
        else:
            self.send("U", None)
            self.send("D", None)
            self.send("UDV",None)
            self.send("V", None)
            self.send("Residuals",None)
            self.send("qqplot",None)
            self.infoa.setText('No data on input yet, waiting to get something.')
            self.infob.setText('')
            

    def dataXd(self, dataset):
        if not dataset:
            self.Xd=None
        else:
            self.Xd = dataset   
    
    def dataXa(self, dataset):
        if not dataset:
            self.Xa=None
        else:
            self.Xa= dataset 
    
    def setNbIter(self):
        if self.method==0:
            self.maxIter=200
        elif self.method==1:
            self.maxIter=200
        else:
            self.maxIter=200

    def runSVD(self):
        # treat missing values as equal to -99999999
        M0=np.ones([len(self.dataset),len(self.dataset[0])])
        for i in range(0,len(self.dataset)):
            for j in range(0,len(self.dataset[0])): 
                if self.dataset[i][j].isSpecial():
                    M0[i][j]=-99999999
                else:
                    M0[i][j]=self.dataset[i][j]
#        M0=self.dataset.toNumpy()
#        M0=np.array(M0[0])
        StdGlobLoc=self.method + 1 
        model= rSVD.rSVD()
        nTrial=self.nTrial
        MaxIter=self.maxIter
        LTScov=0.95
        ncUser=self.rank
        StepIter=1
        MaxNonImpr=5
        tolerance=10**(-6)
        model.doRSVD(M0,nTrial,MaxIter,StdGlobLoc,LTScov,ncUser,StepIter,MaxNonImpr,tolerance)
        U=model.U
        D=model.D
        V=model.V
        UDV=np.dot(np.dot(U,np.diag(D)),V.T)       
        residuals=M0-UDV
        residuals[M0==-99999999]=-99999999 #missing values
        self.residualsNP=residuals
        domainX=self.dataset.domain
     # Transform to Orange format   
        self.V=Orange.data.Table(V)        
        # concatenate with Xa if available
        if hasattr(self, 'Xa') and self.Xa:
            self.V=Orange.data.Table([self.V,self.Xa])
        else:
            self.V.domain.add_meta(Orange.feature.Descriptor.new_meta_id(), Orange.feature.String("Variable"))
            # Get the names of the variables as meta attribute
            for i in range(0,len(domainX)):
                self.V[i]["Variable"]=domainX[i].name
        
        newDomain=domainX
        domW=[]
        for i in range(0, self.rank):
            domW.append(Orange.feature.Continuous("Component %i" %(i+1)))
        domW=Orange.data.Domain(domW,0)
        domW.addmetas(domainX.getmetas())
        self.U = Orange.data.Table(domW,U)
        self.UDV = Orange.data.Table(newDomain,UDV)
        self.D=np.array([np.arange(1,len(D)+1),D])
        self.D=self.D.transpose()
        domD=Orange.data.Domain([Orange.feature.Continuous("Number"),Orange.feature.Continuous("Scaling factor")],0)
        self.D=Orange.data.Table(domD,self.D)
        self.residuals= Orange.data.Table(newDomain,np.array(residuals))
        # add initial missing values
        for i in range(0, len(self.residuals)):
            for j in range(0, len(self.residuals[0])):
                if self.residualsNP[i,j]==-99999999:
                    self.residuals[i][j]='?'
            
                           
        if hasattr(self, 'Xd') and self.Xd:
            self.U =  Orange.data.Table([self.U,self.Xd]) 
            self.UDV = Orange.data.Table([self.UDV,self.Xd])
            self.residuals = Orange.data.Table([self.residuals,self.Xd])
        else:
            for i in range(0,len(self.dataset)):
                self.U[i]["ID"]=self.dataset[i]["ID"]
                self.UDV[i]["ID"]=self.dataset[i]["ID"]
                self.residuals[i]["ID"]=self.dataset[i]["ID"]
                
            
    def calculateQQPlotValues(self):
        nbValues=self.residualsNP.shape[0]*self.residualsNP.shape[1]
        # put all residuals in one vector        
        residualsVector=np.reshape(self.residualsNP, nbValues)
        residualsVector=residualsVector[residualsVector!=-99999999] # exclude missing values
        # sort residuals
        residualsVector.sort()
        normalQuantilesVector=scipy.stats.norm.ppf(np.linspace(1./nbValues,1-1./nbValues,nbValues),loc=residualsVector.mean(),scale=residualsVector.std())
        self.qqplot=np.array([normalQuantilesVector,residualsVector])
        self.qqplot=self.qqplot.transpose()
        domQQPlot=Orange.data.Domain([Orange.feature.Continuous("normal quantiles"),Orange.feature.Continuous("residuals quantiles")],0)
        self.qqplot=Orange.data.Table(domQQPlot,self.qqplot)
        
    
    def browseFile(self):
        if self.recentFiles:
            startfile = self.recentFiles[0]
        else:
            startfile = os.path.expanduser("~/")

#        filename, selectedFilter = QFileDialog.getSaveFileNameAndFilter(self, 'Save Orange Data File', startfile,
#                        self.dlgFormats, self.dlgFormats.splitlines()[0])
#        filename = str(filename)
#       The preceding lines should work as per API, but do not; it's probably a PyQt bug as per March 2010.
#       The following is a workaround.
#       (As a consequence, filter selection is not taken into account when appending a default extension.)
        filename, selectedFilter = QFileDialog.getSaveFileName(self, 'Save Orange Data File', startfile,
                         self.dlgFormats), self.dlgFormats.splitlines()[0]
        filename = unicode(filename)
        if not filename or not os.path.split(filename)[1]:
            return

        ext = lower(os.path.splitext(filename)[1])
        if not ext in self.savers:
            filt_ext = self.re_filterExtension.search(str(selectedFilter)).group("ext")
            if filt_ext == ".*":
                filt_ext = ".tab"
            filename += filt_ext

        self.addFileToList(filename)
        if hasattr(self, 'WW') and self.WW:      
            self.saveFile()

    def saveFile(self, *index):
        self.error()
        #if self.data is not None:
        combotext = unicode(self.filecombo.currentText())
        if combotext == "(none)":
            QMessageBox.information( None, "Error saving data", "Unable to save data. Select first a file name by clicking the '...' button.", QMessageBox.Ok + QMessageBox.Default)
            return
        filename = self.recentFiles[self.filecombo.currentIndex()]
        fileExt = lower(os.path.splitext(filename)[1])
        filenameWithoutExt=lower(os.path.splitext(filename)[0])
        UfileName=filenameWithoutExt + "_U" + ".tab"
        DfileName=filenameWithoutExt + "_D" + ".tab"
        VfileName=filenameWithoutExt + "_V" + ".tab"
        ResidualsfileName=filenameWithoutExt + "_Residuals" + ".tab"
        UDVfileName=filenameWithoutExt + "_UDV" + ".tab"
        QQplotfileName=filenameWithoutExt + "_QQplot" + ".tab"
        
        if fileExt == "":
            fileExt = ".tab"
        try:
            self.savers[fileExt](UfileName, self.U)
            self.savers[fileExt](DfileName, self.D)
            self.savers[fileExt](VfileName, self.V)
            self.savers[fileExt](ResidualsfileName, self.residuals)
            self.savers[fileExt](UDVfileName, self.UDV)
            self.savers[fileExt](QQplotfileName, self.qqplot)
        except Exception, (errValue):
            self.error(str(errValue))
            return
        self.error()

    def addFileToList(self,fn):
        if fn in self.recentFiles:
            self.recentFiles.remove(fn)
        self.recentFiles.insert(0,fn)
        self.setFilelist()

    def setFilelist(self):
        "Set the GUI filelist"
        self.filecombo.clear()

        if self.recentFiles:
            self.filecombo.addItems([os.path.split(file)[1] for file in self.recentFiles])
        else:
            self.filecombo.addItem("(none)")
              
    def resendData(self):
        combotext = unicode(self.filecombo.currentText())
        if combotext == "(none)":
            QMessageBox.information( None, "Error saving data", "Unable to send data. Select first a file name by clicking the '...' button.", QMessageBox.Ok + QMessageBox.Default)
            return
        filename=self.recentFiles[self.filecombo.currentIndex()]
        filenameWithoutExt=lower(os.path.splitext(filename)[0])
        self.runSVD()
        self.send("U", Orange.data.Table(filenameWithoutExt + "_U"))
        self.send("D", Orange.data.Table(filenameWithoutExt + "_D"))
        self.send("V", Orange.data.Table(filenameWithoutExt + "_V"))
        self.send("UDV", Orange.data.Table(filenameWithoutExt + "_UDV"))
        self.send("Residuals", Orange.data.Table(filenameWithoutExt + "_Residuals"))
        self.send("qqplot", Orange.data.Table(filenameWithoutExt + "_QQplot"))

    def commit(self):
        self.runSVD()
        self.send("U", self.U)
        self.send("D", self.D)
        self.send("V",self.V)
        self.send("UDV",self.UDV)
        self.send("Residuals",self.residuals)
        self.calculateQQPlotValues()
        self.send("qqplot",self.qqplot)
        if self.saveOutputs:
            self.saveFile()
        
        
        
            
# Test the widget, run from prompt

if __name__=="__main__":
    appl = QApplication(sys.argv)
    ow = OWrSVD()
    ow.show()
    dataset = orange.ExampleTable('C:/Users/Fajwel/Dropbox/Orange/data.tab')
    ow.dataX(dataset)
    appl.exec_()



