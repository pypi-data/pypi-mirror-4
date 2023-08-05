"""
<name>Model Map</name>
<description>Visualization and analysis of prediction models</description>
<icon>icons/Network.png</icon>
<contact>Miha Stajdohar (miha.stajdohar(@at@)gmail.com)</contact> 
<priority>6520</priority>
"""

import os.path

from Orange import classification, misc, modelmaps, network, utils
from Orange.network.community import CommunityDetection
from OWNxCanvasQt import OWNxCanvas

from orngScaleLinProjData import *
from OWNxExplorer import *
from OWkNNOptimization import OWVizRank
from OWNxHist import *
from OWDistributions import OWDistributionGraph

from PyQt4 import QtCore

dir = utils.environ.widget_install_dir

ICON_PATHS = [("TREE", "Classify/icons/ClassificationTree"),
              ("SCATTERPLOT", "Visualize/icons/ScatterPlot"),
              ("SCATTTERPLOT", "Visualize/icons/ScatterPlot"),
              ("LINEAR_PROJECTION", "Visualize/icons/LinearProjection"),
              ("SPCA", "Visualize/icons/LinearProjection"),
              ("RADVIZ", "Visualize/icons/Radviz"),
              ("POLYVIZ", "Visualize/icons/Polyviz"),
              ("NaiveLearner", "Classify/icons/NaiveBayes"),
              ("BAYES", "Classify/icons/NaiveBayes"),
              ("kNNLearner", "Classify/icons/kNearestNeighbours"),
              ("KNN", "Classify/icons/kNearestNeighbours"),
              ("SVM", "Classify/icons/BasicSVM"),
              ("RF", "Classify/icons/RandomForest")]

ICON_SIZES = ["16", "32", "40", "48", "60"]

MODEL_IMAGES = {"MISSING": os.path.join(dir, "icons/Unknown.png")}

PIXMAP_CACHE = {}

for size in ICON_SIZES:
    for model, path in ICON_PATHS:
        MODEL_IMAGES[model + size] = os.path.join(dir, "%s_%s.png" % (path, size))

class ModelItem(orangeqt.ModelItem):
    def __init__(self, index, x=None, y=None, parent=None):
        orangeqt.ModelItem.__init__(self, index, OWPoint.Ellipse, Qt.blue, 5, parent)
        if x is not None:
            self.set_x(x)
        if y is not None:
            self.set_y(y)

    def paint(self, painter, option, widget):
        orangeqt.ModelItem.paint(self, painter, option, widget)

#        lbl = self.text()
#
#        if lbl == "":
#            return
#
#        metrics = painter.fontMetrics()
#        th = metrics.height()
#
#        pen = painter.pen()
#        pen.setColor(QtCore.Qt.black)
#        painter.setPen(pen)
#
#        for i, l in enumerate(lbl.split(", ")):
#            tw = metrics.width(l)
#            r = QtCore.QRectF(-tw / 2., self.size() / 2. + 5 + i * th, tw, th);
#            painter.drawText(r, QtCore.Qt.AlignCenter, l);

class ModelCurve(NetworkCurve):
    def __init__(self, parent=None, pen=QPen(Qt.black), xData=None, yData=None):
        NetworkCurve.__init__(self, parent, pen=QPen(Qt.black), xData=None, yData=None)

class OWModelMapCanvas(OWNxCanvas):

    def __init__(self, master, parent=None, name="None"):
        OWNxCanvas.__init__(self, master, parent, name)
        self.networkCurve = ModelCurve()
        self.NodeItem = ModelItem

        self.selectionNeighbours = 1
        self.tooltipNeighbours = 1
        self.plotAccuracy = None
        self.vizAttributes = None
        self.radius = 100

    def mouseMoveEvent(self, event):
        OWNxCanvas.mouseMoveEvent(self, event)

        if self.graph is None or self.layout is None:
            return

        if self.plotAccuracy or self.vizAttributes:
            cursor = self.mapToScene(event.pos())
            nearest = self.nearest_point(cursor)

            if nearest is not None:
                toMark = set(self.get_neighbors_upto(nearest.index(), self.tooltipNeighbours))
                toMark = list(toMark)
                self.networkCurve.clear_node_marks()
                self.networkCurve.set_node_marks(dict((i, True) for i in toMark))
                if self.plotAccuracy:
                    self.plotAccuracy(toMark)
                if self.vizAttributes:
                    self.vizAttributes(toMark)
            else:
                nodes = self.networkCurve.nodes().items()
                nodes = [i for i, n in nodes if (n.pos() - cursor).manhattanLength() < self.radius]

                self.networkCurve.clear_node_marks()
                self.networkCurve.set_node_marks(dict((i, True) for i in nodes))

                if self.plotAccuracy:
                    self.plotAccuracy(nodes)
                if self.vizAttributes:
                    self.vizAttributes(nodes)

    def set_tooltip_attributes(self, attributes):
        if self.graph is None or self.items is None or \
           not isinstance(self.items, data.Table):
            return

        attributes = ["Cluster CA", "label", "P", "attributes"]

#        lbl  = "%s\n" % self.graph.items()[vertex.index]["label"].value
#        lbl += "CA: %.4g\n" % self.graph.items()[vertex.index]["CA"].value
#        #lbl += "AUC: %.4g\n" % self.graph.items()[vertex.index]["AUC"].value
#        #lbl += "CA best: %s\n" % clusterCA 
#        lbl += "Attributes: %d\n" % len(self.graph.items()[vertex.index]["attributes"].value.split(", "))
#        lbl += ", ".join(sorted(self.graph.items()[vertex.index]["attributes"].value.split(", ")))

        tooltip_attributes = [self.items.domain[att] for att in \
                                 attributes if att in self.items.domain]
        self.networkCurve.set_node_tooltips(dict((node, ', '.join(str( \
                   self.items[node][att]) for att in tooltip_attributes)) \
                                                        for node in self.graph))

    def loadIcons(self):
        items = self.items
        maxsize = str(max(map(int, ICON_SIZES)))
        minsize = min(map(int, ICON_SIZES))
        for v in self.networkCurve.nodes().itervalues():
            size = str(minsize) if v.size() <= minsize else maxsize

            for i in range(len(ICON_SIZES) - 1):
                if int(ICON_SIZES[i]) < v.size() <= int(ICON_SIZES[i + 1]):
                    size = ICON_SIZES[i]
            imageKey = items[v.index()]['type'].value + size
            if imageKey not in MODEL_IMAGES:
                imageKey = "MISSING"

            fn = MODEL_IMAGES[imageKey]
            if not fn in PIXMAP_CACHE:
                PIXMAP_CACHE[fn] = QPixmap(fn)
            v.set_image(PIXMAP_CACHE[fn])

    def set_representatives(self, node_keys):
        nodes = self.networkCurve.nodes()
        map(ModelItem.set_representative, [nodes[i] for i in node_keys])


class ModelClusterView(network.NxView):
    """A network view expanding and contracting nodes that represent model 
    communities. 
    
    """

    def __init__(self, community_detection):
        network.NxView.__init__(self)

        self._community_detection = community_detection
        self._representatives = None
        self._expanded_nodes = set()
        self._representatives_graph = None

    def __del__(self):
        if self._nx_explorer is not None:
            QObject.disconnect(self._nx_explorer.networkCanvas, SIGNAL('point_rightclicked(Point*)'), self.hierarchical_expand)

    def set_nx_explorer(self, _nx_explorer):
        network.NxView.set_nx_explorer(self, _nx_explorer)

        if self._nx_explorer is not None:
            QObject.connect(self._nx_explorer.networkCanvas, SIGNAL('point_rightclicked(Point*)'), self.hierarchical_expand)

    def update_network(self):
        if self._nx_explorer is not None and self._network is not None:
            subnet = self._network
            self._nx_explorer.change_graph(subnet)

    def init_network(self, graph):
        self._network = graph

        if graph is None or self._community_detection is None:
            return None

        return self.hierarchical_subgraph()

    def set_representatives(self):
        if self._nx_explorer is None or self._representatives is None:
            return

        self._nx_explorer.networkCanvas.set_representatives(key for key, val in self._representatives.iteritems() if len(val) > 1)

    def hierarchical_subgraph(self):
        if self._network is None:
            return

        labels = self._community_detection(self._network)
        clusters = {}
        for key, val in labels.iteritems():
            clusters[val] = clusters.get(val, []) + [key]

        items = self._network.items()
        self._representatives = {max(val, key=lambda x, items=items: items[x]["P"].value): val for val in clusters.itervalues()}
        #for key, val in clusters.items():
        #    representatives.append(max(val, key=lambda x, items=items: items[x]["CA"].value))
        # find neighbors for all representatives
        subgraph = network.nx.Graph.subgraph(self._network, self._representatives.iterkeys())

        # add meta-edges between representatives        
        #repr_neighbors = {key: set(itertools.chain.from_iterable(self._network.adj[n].keys() for n in cluster)) for key, cluster in self._representatives.iteritems()}
        #repr_keys = repr_neighbors.keys()
        #edges = list(itertools.chain.from_iterable([(repr_keys[i], repr_keys[j]) for j in range(i) if repr_keys[i] in repr_neighbors[repr_keys[j]]] for i in range(len(repr_keys))))
        #subgraph.add_edges_from(edges)
        #self._representatives_graph = subgraph

        return subgraph

    def hierarchical_expand(self, node):

        if not node.is_representative():
            return

        nodes = set(self._representatives[node.index()])
        nodes.remove(node.index())
        graph_nodes = set(self._nx_explorer.graph.nodes_iter())
        if len(nodes & graph_nodes) > 0: # contract nodes
            nodes = graph_nodes - nodes
            self._expanded_nodes.remove(node)
        else: # expand nodes
            nodes = graph_nodes | nodes
            self._expanded_nodes.add(node)

        self.select_expanded()
        qApp.processEvents()

        subgraph = network.nx.Graph.subgraph(self._network, nodes)
        self._nx_explorer.change_graph(subgraph)
        self.set_representatives()

    def select_expanded(self):
        self._nx_explorer.networkCanvas.unmark_all_points()
        map(lambda n: ModelItem.set_marked(n, True), self._expanded_nodes)

class OWModelMap(OWNxExplorer, OWNxHist):

    settingsList = ["autoSendSelection", "spinExplicit", "spinPercentage",
        "maxLinkSize", "minVertexSize", "maxVertexSize", "networkCanvas.animate_plot",
        "networkCanvas.animate_points", "networkCanvas.antialias_plot",
        "networkCanvas.antialias_points", "networkCanvas.antialias_lines",
        "networkCanvas.auto_adjust_performance", "invertSize", "optMethod",
        "lastVertexSizeColumn", "lastColorColumn", "networkCanvas.show_indices", "networkCanvas.show_weights",
        "lastNameComponentAttribute", "lastLabelColumns", "lastTooltipColumns",
        "showWeights", "showEdgeLabels", "colorSettings",
        "selectedSchemaIndex", "edgeColorSettings", "selectedEdgeSchemaIndex",
        "showMissingValues", "fontSize", "mdsTorgerson", "mdsAvgLinkage",
        "mdsSteps", "mdsRefresh", "mdsStressDelta", "organism", "showTextMiningInfo",
        "toolbarSelection", "minComponentEdgeWidth", "maxComponentEdgeWidth",
        "mdsFromCurrentPos", "labelsOnMarkedOnly", "tabIndex",
        "networkCanvas.trim_label_words", "opt_from_curr", "networkCanvas.explore_distances",
        "networkCanvas.show_component_distances", "fontWeight", "networkCanvas.state",
        "networkCanvas.selection_behavior", "kNN", "spinLowerThreshold",
        "spinUpperThreshold"]

    def __init__(self, parent=None, signalManager=None, name="Model Map"):
        OWNxExplorer.__init__(self, parent, signalManager, name,
                               NetworkCanvas=OWModelMapCanvas)

        OWNxHist.__init__(self, parent)

        self.inputs = [("Community Detection", CommunityDetection, self.set_community),
                       ("Distances", misc.SymMatrix, self.set_matrix, Default),
                       ("Model Subset", data.Table, self.set_models_subset)]

        self.outputs = [("Model", modelmaps.Model),
                        ("Classifier", classification.Classifier),
                        ("Selected Models", data.Table)]

        self.vertexSize = 32
        self.autoSendSelection = False
        self.minVertexSize = 16
        self.maxVertexSize = 16
        self.vizAccurancy = False
        self.vizAttributes = False
        self.radius = 100
        self.attrIntersection = []
        self.attrIntersectionList = []
        self.attrDifference = []
        self.attrDifferenceList = []
        self.kNN = 1

        self.colorSettings = self.edgeColorSettings

        self.loadSettings()

        self.matrixTab = OWGUI.widgetBox(self.tabs, addToLayout=0, margin=4)
        self.modelTab = OWGUI.widgetBox(self.tabs, addToLayout=0, margin=4)
        self.tabs.insertTab(0, self.matrixTab, "Matrix")
        self.tabs.insertTab(1, self.modelTab, "Model Info")
        self.tabs.setCurrentIndex(self.tabIndex)

        self.networkCanvas.appendToSelection = 0
        self.networkCanvas.minVertexSize = self.minVertexSize
        self.networkCanvas.maxVertexSize = self.maxVertexSize
        self.networkCanvas.invertEdgeSize = 1

        # MARTIX CONTROLS
        self.addHistogramControls(self.matrixTab)
        boxHistogram = OWGUI.widgetBox(self.matrixTab, box="Distance histogram")
        self.histogram = OWHist(self, boxHistogram)
        boxHistogram.layout().addWidget(self.histogram)

        # VISUALIZATION CONTROLS
        vizPredAcc = OWGUI.widgetBox(self.modelTab, "Prediction Accuracy", orientation="vertical")
        OWGUI.checkBox(vizPredAcc, self, "vizAccurancy", "Visualize prediction accurancy", callback=self.visualize_info)
        OWGUI.spin(vizPredAcc, self, "radius", 10, 1000, 1, label="Radius: ", callback=self.visualize_info)
        self.predGraph = OWDistributionGraph(self, vizPredAcc)
        self.predGraph.setMaximumSize(QSize(300, 300))
        self.predGraph.setYRlabels(None)
        self.predGraph.setAxisScale(QwtPlot.xBottom, 0.0, 1.0, 0.1)
        self.predGraph.numberOfBars = 2
        self.predGraph.barSize = 200 / (self.predGraph.numberOfBars + 1)
        vizPredAcc.layout().addWidget(self.predGraph)

        vizPredAcc = OWGUI.widgetBox(self.modelTab, "Attribute lists", orientation="vertical")
        OWGUI.checkBox(vizPredAcc, self, "vizAttributes", "Display attribute lists", callback=self.visualize_info)

        self.attrGraph = OWDistributionGraph(self, vizPredAcc)
        self.attrGraph.setMaximumSize(QSize(300, 300))
        self.attrGraph.setYRlabels(None)
        self.attrGraph.setAxisScale(QwtPlot.xBottom, 0.0, 1.0, 0.1)
        self.attrGraph.numberOfBars = 2
        self.attrGraph.barSize = 200 / (self.attrGraph.numberOfBars + 1)
        vizPredAcc.layout().addWidget(self.attrGraph)


        #self.attrIntersectionBox = OWGUI.listBox(vizPredAcc, self, "attrIntersection", "attrIntersectionList", "Attribute intersection", selectionMode=QListWidget.NoSelection)
        #self.attrDifferenceBox = OWGUI.listBox(vizPredAcc, self, "attrDifference", "attrDifferenceList", "Attribute difference", selectionMode=QListWidget.NoSelection)

        self.attBox.hide()
        self.visualize_info()

        QObject.connect(self.networkCanvas, SIGNAL('selection_changed()'), self.node_selection_changed)

        self.matrixTab.layout().addStretch(1)
        self.modelTab.layout().addStretch(1)

    def set_community(self, community_detection):
        if community_detection is None:
            self.set_network_view(None)
        else:
            mc_view = ModelClusterView(community_detection)
            self.set_network_view(mc_view)
            mc_view.set_representatives()

    def plotAccuracy(self, vertices=None):
        self.predGraph.tips.removeAll()
        self.predGraph.clear()
        #self.predGraph.setAxisScale(QwtPlot.yRight, 0.0, 1.0, 0.2)
        self.predGraph.setAxisScale(QwtPlot.xBottom, 0.0, 1.0, 0.2)

        if not vertices:
            self.predGraph.replot()
            return

        self.predGraph.setAxisScale(QwtPlot.yLeft, -0.5, len(self.matrix.originalData.domain.classVar.values) - 0.5, 1)

        scores = [[float(ca) for ca in ex["CA by class"].value.split(", ")] for ex in self.graph.items().getitems(vertices)]
        scores = [sum(score) / len(score) for score in zip(*scores)]

        currentBarsHeight = [0] * len(scores)
        for cn, score in enumerate(scores):
            subBarHeight = score
            ckey = PolygonCurve(pen=QPen(self.predGraph.discPalette[cn]), brush=QBrush(self.predGraph.discPalette[cn]))
            ckey.attach(self.predGraph)
            ckey.setRenderHint(QwtPlotItem.RenderAntialiased, self.predGraph.useAntialiasing)

            tmpx = cn - (self.predGraph.barSize / 2.0) / 100.0
            tmpx2 = cn + (self.predGraph.barSize / 2.0) / 100.0
            ckey.setData([currentBarsHeight[cn], currentBarsHeight[cn] + subBarHeight, currentBarsHeight[cn] + subBarHeight, currentBarsHeight[cn]], [tmpx, tmpx, tmpx2, tmpx2])
            currentBarsHeight[cn] += subBarHeight

            self.predGraph.addMarker("%.4f" % score, 0, cn, Qt.AlignRight | Qt.AlignBottom)


        self.predGraph.replot()

    def display_attribute_info(self, vertices=None):
        self.attrIntersectionList = []
        self.attrDifferenceList = []

        if vertices is None or len(vertices) == 0:
            return

        attrList = [self.graph.items()[v]["attributes"].value.split(", ") for v in vertices]

        #attrIntersection = set(attrList[0])
        #attrUnion = set()
        #for attrs in attrList:
        #    attrIntersection = attrIntersection.intersection(attrs)
        #    attrUnion = attrUnion.union(attrs)

        #self.attrIntersectionList = attrIntersection
        #self.attrDifferenceList = attrUnion.difference(attrIntersection)



        self.attrGraph.tips.removeAll()
        self.attrGraph.clear()
        #self.predGraph.setAxisScale(QwtPlot.yRight, 0.0, 1.0, 0.2)
        self.attrGraph.setAxisScale(QwtPlot.xBottom, 0.0, 1.0, 0.2)

        if not vertices:
            self.attrGraph.replot()
            return

        labels = [attr.name for attr in self.matrix.originalData.domain.attributes]
        attrList = [{label:len([a for a in attrs if a == label]) for label in labels} for attrs in attrList]


        self.attrGraph.setAxisScale(QwtPlot.yLeft, -0.5, len(labels) - 0.5, 1)

        scores = [sum([attributes[label] for attributes in attrList]) for label in labels]
        #scores = [sum(score) / len(score) for score in zip(*scores)]

        self.attrGraph.setAxisScale(QwtPlot.xBottom, 0.0, max(scores), 1)

        currentBarsHeight = [0] * len(scores)
        for cn, score in enumerate(scores):
            subBarHeight = score
            ckey = PolygonCurve(pen=QPen(self.attrGraph.discPalette[cn]), brush=QBrush(self.attrGraph.discPalette[cn]))
            ckey.attach(self.attrGraph)
            ckey.setRenderHint(QwtPlotItem.RenderAntialiased, self.attrGraph.useAntialiasing)

            tmpx = cn - (self.attrGraph.barSize / 2.0) / 100.0
            tmpx2 = cn + (self.attrGraph.barSize / 2.0) / 100.0
            ckey.setData([currentBarsHeight[cn], currentBarsHeight[cn] + subBarHeight, currentBarsHeight[cn] + subBarHeight, currentBarsHeight[cn]], [tmpx, tmpx, tmpx2, tmpx2])
            currentBarsHeight[cn] += subBarHeight

            self.attrGraph.addMarker("%d" % score, 0, cn, Qt.AlignRight | Qt.AlignBottom)


        self.attrGraph.replot()

    def visualize_info(self):
        self.networkCanvas.radius = self.radius

        if self.vizAccurancy:
            self.networkCanvas.plotAccuracy = self.plotAccuracy
        else:
            self.networkCanvas.plotAccuracy = None
            self.plotAccuracy(None)

        if self.vizAttributes:
            self.networkCanvas.vizAttributes = self.display_attribute_info
        else:
            self.networkCanvas.vizAttributes = None
            self.display_attribute_info(None)

    def set_models_subset(self, subsetData):
        self.info()

        if "uuid" not in subsetData.domain:
            self.info("Invalid subset data. Data domain must contain 'uuid' attribute.")
            return

        uuids = set([ex["uuid"].value for ex in subsetData])
        for v in self.vertices:
            v.highlight = 1 if v.uuid in uuids else 0

    def set_matrix(self, matrix):
        self.warning()

        if matrix is None:
            OWNxHist.setMatrix(self, None)
            return

        if not hasattr(matrix, "items") or not hasattr(matrix, "original_data"):
            self.warning("Data matrix does not have required data for items and original_data.")
            return

        requiredAttrs = set(["CA", "AUC", "attributes", "uuid"])
        attrs = [attr.name for attr in matrix.items.domain]
        if len(requiredAttrs.intersection(attrs)) != len(requiredAttrs):
            self.warning("Items Orange.data.Table does not contain required attributes: %s." % ", ".join(requiredAttrs))
            return

        for ex in matrix.items:
            ex["attributes"] = ", ".join(sorted(ex["attributes"].value.split(", ")))

        OWNxHist.setMatrix(self, matrix)

    def set_node_sizes(self):
        OWNxExplorer.set_node_sizes(self)
        self.networkCanvas.loadIcons()
        self.networkCanvas.replot()

    def set_node_styles(self):
        #for v in self.networkCanvas.networkCurve.nodes().itervalues():
        #    #auc = self.graph.items()[v.index()]
        #    v.style = 1 #auc
        pass

    def node_selection_changed(self):
        self.warning()

        graph = self.graph_base

        if graph is None or graph.items() is None or self.graph_matrix is None:
            self.send("Model", None)
            self.send("Selected Models", None)
            return

        if graph.number_of_nodes() != self.graph_matrix.dim:
            self.warning('Network items and matrix results not of equal length.')
            self.send("Model", None)
            self.send("Selected Models", None)
            return

        selection = self.networkCanvas.selected_nodes()

        if len(selection) == 1:
            model = graph.items()[selection[0]]['model'].value
            self.send('Model', model)
            self.send('Selected Models', graph.items().getitems(selection))
        elif len(selection) > 1:
            self.send('Model', None)
            self.send('Selected Models', graph.items().getitems(selection))
        else:
            self.send('Model', None)
            self.send('Selected Models', None)

        if self._network_view:
            self._network_view.select_expanded()

    def sendSignals(self):
        if self.graph is None or self.graph_matrix is None:
            self.set_graph_none()
            return

        self.set_graph(self.graph, ModelCurve)

        if self._network_view:
            self._network_view.set_representatives()

        self.set_items_distance_matrix(self.graph_matrix)
        #self.hierarchical_view()
        # TODO clickedAttLstBox -> setLabelText(["attributes"]

        for node in self.networkCanvas.networkCurve.nodes().itervalues():
            node.uuid = self.graph_base.items()[node.index()]["uuid"].value

        self.set_node_sizes()
        self.set_node_styles()
        self.set_node_colors()

        #self.networkCanvas.set_node_labels(["attributes"])

        labels = self.matrix.originalData.domain.classVar.values.native()
        self.predGraph.numberOfBars = len(labels)
        self.predGraph.barSize = 200 / (self.predGraph.numberOfBars + 1)
        self.predGraph.setYLlabels(labels)
        self.predGraph.setAxisScale(QwtPlot.xBottom, 0.0, 1.0, 0.2)
        self.predGraph.setAxisScale(QwtPlot.yLeft, -0.5, len(labels) - 0.5, 1)

        self.predGraph.enableYRaxis(0)
        self.predGraph.setYRaxisTitle("")
        self.predGraph.setXaxisTitle("CA")
        self.predGraph.setShowXaxisTitle(True)
        self.predGraph.replot()

        labels = [attr.name for attr in self.matrix.originalData.domain.attributes]
        self.attrGraph.numberOfBars = len(labels)
        self.attrGraph.barSize = 200 / (self.attrGraph.numberOfBars + 1)
        self.attrGraph.setYLlabels(labels)
        self.attrGraph.setAxisScale(QwtPlot.xBottom, 0.0, 1.0, 0.2)
        self.attrGraph.setAxisScale(QwtPlot.yLeft, -0.5, len(labels) - 0.5, 1)

        self.attrGraph.enableYRaxis(0)
        self.attrGraph.setYRaxisTitle("")
        self.attrGraph.setXaxisTitle("models")
        self.attrGraph.setShowXaxisTitle(True)
        self.attrGraph.replot()

        self.visualize_info()

if __name__ == "__main__":
    import OWModelFile
    import pickle
    modelName = 'zoo-168'
    root = 'c:\\Users\\miha\\Projects\\res\\metamining\\'

    appl = QApplication(sys.argv)
    ow = OWModelMap()
    ow.show()
    mroot = '%snew\\' % root
    matrix, labels, data = OWModelFile.readMatrix('%s%s.npy' % (mroot, modelName))
    if os.path.exists('%s%s.tab' % (mroot, modelName)):
        matrix.items = data.Table('%s%s.tab' % (mroot, modelName))
    else:
        print 'ExampleTable %s not found!\n' % ('%s%s.tab' % (mroot, modelName))
    if os.path.exists('%s%s.res' % (mroot, modelName)):
        matrix.results = pickle.load(open('%s%s.res' % \
                                               (mroot, modelName), 'rb'))
    else:
        print 'Results pickle %s not found!\n' % \
              ('%s%s.res' % (mroot, modelName))

    matrix.originalData = data.Table('%stab\\zoo.tab' % root)
    ow.set_matrix(matrix)
    appl.exec_()

