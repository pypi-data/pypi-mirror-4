
"""
<name>Rank selection for NMF</name>
<description>Compute measures for NMF rank selection</description>
<icon>icons/NMF.png</icon>
<priority>30</priority>
    """


import nimfa
import numpy as np

#import sys
#sys.path.append("C:\\Python27\\Lib\site-packages\\Orange\\OrangeWidgets")
from OWWidget import *
import OWGUI



class OWNMFRankSelection(OWWidget):
    settingsList = ['nbIter','factorizationMethod','rangeRanksUB','rangeRanksLB','initialization','nbRuns']
    def __init__(self, parent=None, signalManager=None):
        OWWidget.__init__(self, parent, signalManager, 'Rank selection for NMF')
        
        self.inputs = [("Data", ExampleTable, self.data),("Initial_W", ExampleTable, self.dataInitW),("Initial_H", ExampleTable, self.dataInitH)]
        self.outputs = [("Measures", ExampleTable)]
        
        self.nbIter=100
        self.factorizationMethod=0
        self.initialization=0
        self.rangeRanksUB=10 # upper bound for range of ranks
        self.rangeRanksLB=2 # lower bound for range of ranks
        self.nbRuns=10 # number of runs to calculate measures
        self.doCoph=1
        self.doSparse=0
        self.doRss=0
        self.loadSettings()
        
        # GUI
        box = OWGUI.widgetBox(self.controlArea, "Info")
        self.infoa = OWGUI.widgetLabel(box, 'No data on input yet, waiting to get something.')
        self.infob = OWGUI.widgetLabel(box, '')
        
        OWGUI.separator(self.controlArea)
        self.paramBox = OWGUI.widgetBox(self.controlArea, "Parameters")
        OWGUI.lineEdit(self.paramBox, self, 'nbIter', label='Number of iterations',labelWidth=150, orientation="horizontal")
        self.methodBox = OWGUI.widgetBox(self.controlArea, "Factorization Method")        
        OWGUI.radioButtonsInBox(self.methodBox, self, 'factorizationMethod',callback=self.setNbIter,
                                btnLabels = ["NMF", "LSNMF", "SNMF", "BMF"],
                                tooltips = ["Standard Nonnegative Matrix Factorization",
                                            "Alternating Nonnegative Least Squares Matrix Factorization Using Projected Gradient (bound constrained optimization) method for each subproblem",
                                            "Sparse Nonnegative Matrix Factorization",
                                            "Binary Matrix Factorization"])
        self.initBox = OWGUI.widgetBox(self.controlArea, "Initialization")        
        OWGUI.radioButtonsInBox(self.initBox, self, 'initialization',
                                btnLabels = ["random_vcol", "NNDSVD", "Fixed"],
                                tooltips = ["Random initialization of factors",
                                            "Nonnegative Double Singular Value Decomposition",
                                            "Fixed (to be done)"])
        self.chooseRankBox = OWGUI.widgetBox(self.controlArea, "Find best rank (calculate selected measures)")
        self.infob = OWGUI.widgetLabel(box, '')
        OWGUI.spin(self.chooseRankBox, self, 'rangeRanksLB', label='Minimum rank',min=1,max=200, step=1,labelWidth=150, orientation="horizontal")
        OWGUI.spin(self.chooseRankBox, self, 'rangeRanksUB', label='Maximum rank',min=1,max=200, step=1,labelWidth=150, orientation="horizontal")   
        OWGUI.spin(self.chooseRankBox, self, 'nbRuns', label='Number of runs',min=1,max=100, step=1,labelWidth=150, orientation="horizontal")
        OWGUI.checkBox(self.chooseRankBox, self, "doCoph", "Cophenetic correlation coefficient", callback=self.setNbRuns)
        OWGUI.checkBox(self.chooseRankBox, self, "doRss", "RSS", callback=self.setNbRuns)        
        OWGUI.checkBox(self.chooseRankBox, self, "doSparse", "Sparseness", callback=self.setNbRuns)
        OWGUI.button(self.controlArea, self, "Go (this process may be lengthy)", callback=self.findBestRank)        
        self.paramBox.setDisabled(1)
        self.methodBox.setDisabled(1)
        self.initBox.setDisabled(1)
        self.chooseRankBox.setDisabled(1)
        
        self.resize(100,50)
    
    def data(self, dataset):
        if dataset:
            self.dataset = dataset
            self.infoa.setText('%d variables in input data set' % len(dataset[0]))
            self.infob.setText('%d observations in input data set' % len(dataset))
            self.paramBox.setDisabled(0)
            self.methodBox.setDisabled(0)
            self.initBox.setDisabled(0)
            self.chooseRankBox.setDisabled(0)
        #self.commit()
        else:
            self.send("W", None)
            self.send("H", None)
            self.send("Measures",None)
            self.infoa.setText('No data on input yet, waiting to get something.')
            self.infob.setText('')   
    
    def dataInitH(self, dataset):
        if not dataset:
            return # avoid any unnecessary computation
        H=dataset.toNumpy()
        H=np.matrix(H[0]) 
        self.initH = H
    
    def dataInitW(self, dataset):
        if not dataset:
            return # avoid any unnecessary computation
        W=dataset.toNumpy()
        W=np.matrix(W[0]) 
        self.initW = W
        
    def setNbIter(self):
        if self.factorizationMethod==0:
            self.nbIter=200
        elif self.factorizationMethod==1:
            self.nbIter=200
        elif self.factorizationMethod==2:
            self.nbIter=200
        else:
            self.nbIter=200 
    
    def setNbRuns(self):
        if self.doCoph:
            self.nbRuns=10
        else:
            self.nbRuns=1
    
    def findBestRank(self):   
        V=self.dataset.toNumpy()
        V=np.matrix(V[0])
        methodLabels = ["nmf", "lsnmf", "snmf", "bmf"]
        initLabels = ["random_vcol", "nndsvd", "fixed"]
        if self.initialization == 2:
            fctr = nimfa.mf(V, seed = initLabels[self.initialization], method = methodLabels[self.factorizationMethod], rank = 4, max_iter = self.nbIter, W=self.initW, H=self.initH)
        else:
            if self.factorizationMethod==1:
                fctr = nimfa.mf(V, seed = initLabels[self.initialization], min_residuals=1e-15, method = methodLabels[self.factorizationMethod], rank = 4, max_iter = self.nbIter, sub_iter = 20, inner_sub_iter = 20)
            else:
                fctr = nimfa.mf(V, seed = initLabels[self.initialization], method = methodLabels[self.factorizationMethod], rank = 4, max_iter = self.nbIter) 
        measures=[]
        if self.doCoph:
            measures.append('cophenetic')
        if self.doRss:
            measures.append('rss')
        if self.doSparse:
            measures.append('sparseness')
        res = fctr.estimate_rank(range=xrange(self.rangeRanksLB,self.rangeRanksUB +1),n_run=self.nbRuns, what=measures)
        if self.doSparse:
            resTable=np.zeros([self.rangeRanksUB-self.rangeRanksLB+1,len(measures)+2])
        else:
            resTable=np.zeros([self.rangeRanksUB-self.rangeRanksLB+1,len(measures)+1]) 
        # fill output table, since sparseness is computed for both W and H, treat it separately (two columns instead of one)    
        for i in range(0, self.rangeRanksUB-self.rangeRanksLB+1):
            resTable[i,0]=self.rangeRanksLB + i
            if self.doCoph:
                resTable[i, 1]= res[resTable[i,0]]['cophenetic']
            if self.doRss:
                resTable[i, self.doCoph + 1]= res[resTable[i,0]]['rss']
            if self.doSparse:
                resTable[i,len(measures)]=res[resTable[i,0]]['sparseness'][0]
                resTable[i,len(measures)+1]=res[resTable[i,0]]['sparseness'][1]
        
        # transform to Orange format        
        domResList=[Orange.feature.Continuous("Rank")]
        if self.doCoph:
            domResList.append(Orange.feature.Continuous("Cophenetic"))
        if self.doRss:
            domResList.append(Orange.feature.Continuous("RSS"))
        if self.doSparse:
            domResList.append(Orange.feature.Continuous("Sparseness W"))
            domResList.append(Orange.feature.Continuous("Sparseness H"))
        self.listAtt=domResList
        domRes=Orange.data.Domain(domResList,0)
        self.measures=Orange.data.Table(domRes,resTable)        
        self.send("Measures", self.measures)



# Test the widget, run from prompt

if __name__=="__main__":
    appl = QApplication(sys.argv)
    ow = OWNMFRankSelection()
    ow.show()
    dataset = orange.ExampleTable('C:/Users/Fajwel/Dropbox/Orange/sampleData.tab')
    ow.data(dataset)
    ow.dataInitH(dataset)
    ow.dataInitW(dataset)
    appl.exec_()

