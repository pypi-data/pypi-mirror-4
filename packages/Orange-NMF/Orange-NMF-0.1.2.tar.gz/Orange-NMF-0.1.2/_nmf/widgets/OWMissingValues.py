
"""
<name>Missing Values Indicator</name>
<description>Detection of Missing Values</description>
<icon>icons/MissingIcon.png</icon>
<priority>30</priority>
"""

import numpy as np

#import sys
#sys.path.append("C:\\Python27\\Lib\site-packages\\Orange\\OrangeWidgets")
from OWWidget import *
import OWGUI



class OWMissingValues(OWWidget):
    settingsList = []
    def __init__(self, parent=None, signalManager=None):
        OWWidget.__init__(self, parent, signalManager, 'Missing Values Indicator')
        
        self.inputs = [("Data", ExampleTable, self.data)]
        self.outputs = [("Missing Values Indicator", ExampleTable)]
        self.loadSettings()

        # GUI
        box = OWGUI.widgetBox(self.controlArea, "Info")
        self.infoa = OWGUI.widgetLabel(box, 'No data on input yet, waiting to get something.')
        self.infob = OWGUI.widgetLabel(box, '')

        OWGUI.separator(self.controlArea)
        OWGUI.button(self.controlArea, self, "Commit", callback=self.commit)        
        self.resize(100,50)

    def data(self, dataset):
        if dataset:
            self.dataset = dataset
            self.infoa.setText('%d variables in input data set' % len(dataset[0]))
            self.infob.setText('%d observations in input data set' % len(dataset))
        else:
            self.send("Missing Values Indicator", None)
            self.infoa.setText('No data on input yet, waiting to get something.')
            self.infob.setText('')
                      
        
    def commit(self):
        # find missing value and report them in indicator matrix
        indic=np.ones([len(self.dataset),len(self.dataset[0])]) #last column of data is the IDs
        for i in range(0,len(self.dataset)):
            for j in range(0,len(self.dataset[0])): 
                if self.dataset[i][j].isSpecial():
                    indic[i][j]=0
        self.outputData=indic
        domainX=self.dataset.domain
        self.outputData=Orange.data.Table(domainX, np.array(self.outputData))       
        for i in range(0,len(self.dataset)):        
            self.outputData[i]["ID"]=self.dataset[i]["ID"]
        self.send("Missing Values Indicator", self.outputData)     

            
# Test the widget, run from prompt

if __name__=="__main__":
    appl = QApplication(sys.argv)
    ow = OWMissingValues()
    ow.show()
    dataset = orange.ExampleTable('C:/Users/Fajwel/Dropbox/Orange/testMissingData.txt')
    ow.data(dataset)
    appl.exec_()
