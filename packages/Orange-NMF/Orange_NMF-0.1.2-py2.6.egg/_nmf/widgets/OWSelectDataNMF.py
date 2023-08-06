
"""
<name>Selection for NMF</name>
<description>Selection of variables and observations</description>
<icon>icons/NMFIcon.png</icon>
<priority>30</priority>
"""

#import sys
#sys.path.append("C:\\Python27\\Lib\site-packages\\Orange\\OrangeWidgets")
from OWWidget import *
import OWGUI



class OWSelectDataNMF(OWWidget):
    settingsList = []
    def __init__(self, parent=None, signalManager=None):
        OWWidget.__init__(self, parent, signalManager, 'Selection for NMF')
        # X corresponds to numeric attributes (X will be factorized in X=W*H)
        
        self.inputs = [("X", ExampleTable, self.data),("Xd", ExampleTable, self.dataXd),("Xa", ExampleTable, self.dataXa),("List of variables", ExampleTable, self.dataVar),("List of observations", ExampleTable, self.dataObs)]
        self.outputs = [("Selected data", ExampleTable),("Selected Xd", ExampleTable),("Selected Xa", ExampleTable)]
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
            self.commit()
        else:
            self.send("Selected data", None)
            self.send("Selected Xd", None)
            self.send("Selected Xa", None)
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
    
    def dataVar(self, dataset):
        if not dataset:
            self.varList=None
        else:
            self.varList = dataset

    def dataObs(self, dataset):
        if not dataset:
            self.obsList=None
        else:
            self.obsList = dataset        
        
    def readData(self,dataset): # convert from Orange format to Numpy format, keepy only the matrix to factorize
        V=dataset.toNumpy()
        V=V[0]
        return V                
        
    def selectData(self):
        domainX=self.dataset.domain    
        self.selectedData=self.dataset
        if hasattr(self, 'Xa') and self.Xa:        
            self.selectedXa=self.Xa
        if hasattr(self, 'Xd') and self.Xd:
            self.selectedXd=self.Xd           
        if hasattr(self, 'varList') and self.varList:
            # create new domains for X containing the names of the variables in varList (including meta-attributes)
            newDomainListX=[]
            for i in range(0,len(self.varList)):
                if domainX.__contains__(self.varList[i][0].value) and not(domainX.has_meta(self.varList[i][0].value)): #add attribute which is not meta
                    newDomainListX.append(self.varList[i][0].value)
            # return new orange data tables from the new domains
            newDomainX=Orange.data.Domain(newDomainListX,0,domainX)
            # begin by adding all meta-attributes and then remove those which are not in the list of selected variables (except ID)            
            newDomainX.addmetas(domainX.getmetas())
            metas=domainX.getmetas().values()
            varList2=[] # varList2 is the varList but not in Orange format
            for i in range(0, len(self.varList)):
                varList2.append(self.varList[i][0].value)
            for i in range(0,len(metas)):
                if not(varList2.__contains__(metas[i].name)) and not(metas[i].name=="ID"): # this variable is not selected and is meta attribute which is not "ID"
                    newDomainX.removemeta(metas[i])
            self.selectedData=Orange.data.Table(newDomainX,self.dataset)
            if hasattr(self, 'Xa') and self.Xa:
                 # create list of variables            
                varListAll=[]
                for i in range(0, len(self.Xa)):
                    varListAll.append(self.Xa[i]["Variable"].value)
                # create binary array of indices to select in self.Xa
                indSelectionXa=[]
                for i in range(0, len(varListAll)):
                    # check if varListAll[i] is in varList2
                    j=0
                    check=False
                    while not check and j<len(varList2):
                        if varListAll[i]==varList2[j]:
                            indSelectionXa.append(True)
                            check=True
                        j+=1
                    if not check:
                        indSelectionXa.append(False)
                self.indSelectionXa=indSelectionXa
                self.selectedXa=self.selectedXa.select(indSelectionXa)
                
        if hasattr(self, 'obsList') and self.obsList:
            # create list of IDs            
            IDs=[]
            for i in range(0, len(self.dataset)):
                IDs.append(self.dataset[i]["ID"].value)
            # create list of IDs to select
            IDselection=[]
            for i in range(0, len(self.obsList)):
                IDselection.append(self.obsList[i][0].value)
            # create binary array of indices to select in self.dataset
            indSelection=[]
            for i in range(0, len(IDs)):
                # check if IDs[i] is in IDselection
                j=0
                check=False
                while not check and j<len(IDselection):
                    if IDs[i]==IDselection[j]:
                        indSelection.append(True)
                        check=True
                    j+=1
                if not check:
                    indSelection.append(False)
            self.indSelection=indSelection
            self.selectedData=self.selectedData.select(indSelection)
            if hasattr(self, 'Xa') and self.Xa:
                self.selectedXd=self.selectedXd.select(indSelection)
    
    def commit(self):
        self.selectData()    
        self.send("Selected data", self.selectedData)
        if hasattr(self, 'Xd') and self.Xd:
            self.send("Selected Xd", self.selectedXd)
        if hasattr(self, 'Xa') and self.Xa:
            self.send("Selected Xa", self.selectedXa)

            
# Test the widget, run from prompt

if __name__=="__main__":
    appl = QApplication(sys.argv)
    ow = OWSelectDataNMF()
    ow.show()
    dataset = orange.ExampleTable('C:/Users/Fajwel/Dropbox/Orange/testSelectData.tab')
    selectVar=orange.ExampleTable('C:/Users/Fajwel/Dropbox/Orange/testSelectDataVar.tab')
    selectID=orange.ExampleTable('C:/Users/Fajwel/Dropbox/Orange/testSelectDataID.tab')
    ow.data(dataset)
    ow.dataVar(selectVar)
    ow.dataObs(selectID)
    ow.selectData()
    appl.exec_()
