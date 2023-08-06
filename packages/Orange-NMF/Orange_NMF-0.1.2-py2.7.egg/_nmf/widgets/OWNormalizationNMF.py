
"""
<name>Normalization for NMF</name>
<description>Normalization for NMF</description>
<icon>icons/NormalizeIcon.png</icon>
<priority>30</priority>
"""

import numpy as np

#import sys
#sys.path.append("C:\\Python27\\Lib\site-packages\\Orange\\OrangeWidgets")
from OWWidget import *
import OWGUI



class OWNormalizationNMF(OWWidget):
    settingsList = ['logTransform','scale','scaleMedian','subMin','normRows']
    def __init__(self, parent=None, signalManager=None):
        OWWidget.__init__(self, parent, signalManager, 'Normalization for NMF')
        
        self.inputs = [("Data", ExampleTable, self.data)]
        self.outputs = [("Processed data", ExampleTable)]
        self.logTransform=0
        self.scale=0
        self.scaleMedian=0
        self.subMin=0
        self.normRows=0
        self.loadSettings()

        # GUI
        box = OWGUI.widgetBox(self.controlArea, "Info")
        self.infoa = OWGUI.widgetLabel(box, 'No data on input yet, waiting to get something.')
        self.infob = OWGUI.widgetLabel(box, '')

        OWGUI.separator(self.controlArea)
        self.logBox = OWGUI.widgetBox(self.controlArea, "Log transformation")
        OWGUI.checkBox(self.logBox, self, "logTransform", "Take the log 2 of the data")
        self.normalizeBox = OWGUI.widgetBox(self.controlArea, "Normalization")
        OWGUI.checkBox(self.normalizeBox, self, "scale", "Scale")
        OWGUI.checkBox(self.normalizeBox, self, "scaleMedian", "Divide by median")
        OWGUI.checkBox(self.normalizeBox, self, "subMin", "Subtract minimum value")
        OWGUI.checkBox(self.normalizeBox, self, "normRows", "Normalize rows (sum to one)")
        OWGUI.button(self.controlArea, self, "Commit", callback=self.commit)        
        
        self.logBox.setDisabled(1)
        self.normalizeBox.setDisabled(1)        
        self.resize(100,50)

    def data(self, dataset):
        if dataset:
            self.dataset = dataset
            self.infoa.setText('%d variables in input data set' % len(dataset[0]))
            self.infob.setText('%d observations in input data set' % len(dataset))
            self.logBox.setDisabled(0)
            self.normalizeBox.setDisabled(0)
            self.commit()
        else:
            self.send("Processed data", None)
            self.infoa.setText('No data on input yet, waiting to get something.')
            self.infob.setText('')
        
        
    def readData(self,dataset): # convert from Orange format to Numpy format, keepy only the matrix to factorize
        V=dataset.toNumpy()
        V=V[0]
        return V                
        
    def commit(self):
        self.processedData=self.readData(self.dataset)
        self.processedData=self.processedData.astype(float)
        if self.logTransform:
            self.processedData=np.log2(self.processedData)
        if self.scale:
            for k in range(0,self.processedData.shape[1]):
                self.processedData[:,k]=self.processedData[:,k]/sum(abs(self.processedData[:,k]))
        if self.scaleMedian:
            for k in range(0,self.processedData.shape[1]):
                self.processedData[:,k]=self.processedData[:,k]/np.median(self.processedData[:,k])
        if self.subMin:
            for k in range(0,self.processedData.shape[1]):
                self.processedData[:,k]=self.processedData[:,k]-np.min(self.processedData[:,k])
        if self.normRows:
            for k in range(0,self.processedData.shape[0]):
                self.processedData[k,:]=self.processedData[k,:]/sum(self.processedData[k,:])
        domainX=self.dataset.domain
        newDomain=[]
        for i in range(0, len(domainX)):
            newDomain.append(Orange.feature.Continuous(domainX[i].name))
        newDomain=Orange.data.Domain(newDomain,0)
        newDomain.addmetas(domainX.getmetas())
        self.processed=Orange.data.Table(newDomain, self.processedData)
        if len(domainX.getmetas()):
            nameMeta=domainX.getmetas().values()[0].name
            for i in range(0,len(self.dataset)):
                self.processed[i][nameMeta]=self.dataset[i][nameMeta]        
        self.send("Processed data", self.processed)     

            
# Test the widget, run from prompt

if __name__=="__main__":
    appl = QApplication(sys.argv)
    ow = OWNormalizationNMF()
    ow.show()
    dataset = orange.ExampleTable('C:/Users/Paul Fogel/Desktop/testNormRows.tab')
    ow.data(dataset)
    appl.exec_()
