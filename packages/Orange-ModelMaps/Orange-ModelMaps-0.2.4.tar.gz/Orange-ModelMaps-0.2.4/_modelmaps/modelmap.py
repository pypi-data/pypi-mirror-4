"""
.. index:: model map

***************
Build Model Map
***************

.. autoclass:: Orange.modelmaps.BuildModelMap
   :members:
   
**************
Help Functions
**************

.. autofunction:: load
.. autofunction:: save
.. autofunction:: get_models_table
.. autofunction:: get_feature_subsets

"""

import bz2, itertools, math, random, os.path, time, uuid, re, sys
import cPickle as pickle

import scipy.stats
import numpy as np

import orngVizRank as vr
import model

from orngScaleData import getVariableValuesSorted

from Orange import data, distance, ensemble, feature, misc, projection
from Orange.classification.knn import kNNLearner
from Orange.classification.tree import SimpleTreeLearner, TreeLearner

MODEL_LIST = ["", "SCATTERPLOT", "RADVIZ", "SPCA", "POLYVIZ", "TREE", "NaiveLearner", "kNNLearner", "SVM", "RF"]

def distance_mi(m1, m2):
    """Return inverted normalized mutual information.

    1 - NMI(m1.instance_predictions, m2.instance_predictions)
    """

    classes1 = np.unique(m1.instance_predictions)
    classes2 = np.unique(m2.instance_predictions)
    m1_classes = [m1.instance_predictions == c for c in classes1]
    m2_classes = [m2.instance_predictions == c for c in classes2]
    m1_p = [np.average(m1_c1) for m1_c1 in m1_classes]
    m2_p = [np.average(m2_c2) for m2_c2 in m2_classes]

    eps = np.finfo(float).eps
    mi = sum(sum(np.average(m1_c1 & m2_c2) * np.log2(max(np.average(m1_c1 & m2_c2) / p1 / p2, eps)) for m2_c2, p2 in zip(m2_classes, m2_p)) for m1_c1, p1 in zip(m1_classes, m1_p))
    h1 = -sum(p * np.log2(p) for p in m1_p)
    h2 = -sum(p * np.log2(p) for p in m2_p)

    return 0 if h1 == 0 and h2 == 0 else 1. - 2 * mi / (h1 + h2)

def distance_class(m1, m2):
    w = np.average(m1.instance_predictions != m2.instance_predictions)
    return 1 if math.isnan(w) else w

def distance_manhattan(m1, m2):
    return np.sum(np.abs(m1.probabilities - m2.probabilities)) / 2. / len(m1.probabilities)

def distance_euclidean(m1, m2):
    return np.sum(np.sqrt(np.sum((m1.probabilities - m2.probabilities)**2, axis=1))) / math.sqrt(2.) / len(m1.probabilities)

def distance_rank(m1, m2):
    return 1 - abs(scipy.stats.spearmanr(m1.probabilities, m2.probabilities, axis=None)[0])

def get_feature_subsets_scatterplot(domain, nsubsets):
    """Return attribute subsets for Scatter Plot."""
    attrs = []
    for i in range(len(domain.features)):
        for j in range(i):
            attrs.append((domain.features[i].name, domain.features[j].name))
    random.shuffle(attrs)

    if nsubsets > len(attrs):
        raise AttributeError("Attribute nsubsets higher than number of possible combinations: %d." % len(attrs))

    return attrs[:nsubsets]

def get_feature_subsets(domain, nsubsets=None, min_features=None, max_features=None):
    """Return random attribute subsets.
    
    :param domain: data set domain to extract features
    :type domain: :obj:`Orange.data.Domain`
    
    :param nsubsets:  number of attribute subsets
    :type nsubsets: int
    
    """

    def binomial(n, k):
        if n > k:
            return math.factorial(n) / (math.factorial(k) * math.factorial(n - k))
        elif n == k:
            return 1
        else:
            return 0

    max_features = len(domain.features) if max_features is None else min(max_features, len(domain.features))
    min_features = 2 if min_features is None else max(min(min_features, max_features), 2)

    attrs = [var.name for var in domain.features]
    nattrs = len(attrs)
    total = sum(binomial(nattrs, i) for i in range(min_features, max_features + 1))

    if nsubsets is not None and nsubsets > total:
        raise AttributeError("Attribute nsubsets higher than number of possible combinations: %d." % total)

    if min_features == max_features:
        combinations = itertools.combinations(attrs, max_features)
    else:
        combinations = (itertools.chain(*(itertools.combinations(attrs, i) for i in range(min_features, max_features + 1))))

    if nsubsets is None:
        return list(combinations)
    else:
        selectors = [1] * nsubsets + [0] * (total - nsubsets)
        random.shuffle(selectors)
        return list(itertools.compress(combinations, selectors))
    #return list(itertools.compress(combinations, xrange(10)))

def get_models_table():
    """Return an empty data table for model meta data."""

    attrs = []
    attrs.append(feature.String("uuid"))
    varAttrs = feature.Continuous("number of attributes")
    varAttrs.numberOfDecimals = 0
    attrs.append(varAttrs)
    attrs.append(feature.Continuous("CA"))
    attrs.append(feature.String("CA by class"))
    attrs.append(feature.Continuous("P"))
    attrs.append(feature.Continuous("AUC"))
    attrs.append(feature.Continuous("Brier"))
    attrs.append(feature.Continuous("Brier by class"))
    attrs.append(feature.Continuous("cluster CA"))
    attrs.append(feature.String("label"))
    attrs.append(feature.String("attributes"))
    attrs.append(feature.Discrete("type", values=MODEL_LIST[1:]))
    attrs.append(feature.Python("model"))
    csizes = feature.Continuous("cluster size")
    csizes.numberOfDecimals = 0
    attrs.append(csizes)

    return data.Table(data.Domain(attrs, 0))


def load(file_name):
    """Load a model map. Read compressed tuple containing model similarity
    matrix and data table.

    """

    base, ext = os.path.splitext(file_name)
    file_name = base if ext.lower() == ".bz2" else file_name

    smx, table, data = pickle.load(bz2.BZ2File('%s.bz2' % file_name, "r"))
    return smx, table, data

def save(file_name, smx, model_data, original_data):
    """Save model map to disk. Model similarity matrix and data table tuple
    is pickled and compressed as a bz2 archive.

    """

    if original_data is None or smx is None or model_data is None:
        raise AttributeError("Distance matrix, model meta-data table, and original data table must be given.")

    base, ext = os.path.splitext(file_name)
    file_name = base if ext.lower() == ".bz2" else file_name

    pickle.dump((smx, model_data, original_data), bz2.BZ2File('%s.bz2' % file_name, "w"), -1)

class BuildModelMap(object):

    def __init__(self, fname, folds=10, model_limit=500):

        self.model_limit = model_limit
        self.data_d = self._get_data(fname)
        #self.data_c = self._get_data(fname, continuize=True)
        self.data_d = data.filter.IsDefined(domain=self.data_d.domain)(self.data_d)

        self.folds = folds if len(self.data_d) < 2000 else 2

        self.indices = data.sample.SubsetIndicesCV(self.data_d, self.folds, randseed=0)

    def _get_data(self, fname, continuize=False):
        """Return a data Table.
           
        :param fname: data set file name
        :type fname: string
        
        :param continuize:  if true, it tries to load a name-c.tab data table as Orange DomainContinuizer changes attribute names.
        :type continuize: bool
        
        """

        if continuize:
            base, ext = os.path.splitext(fname)
            if base[-2:] == "-c":
                fname = "%s%s" % (base, ext)
            else:
                fname = "%s-c%s" % (base, ext)

            table = data.Table(fname)
            return table
            ##############################################################################
            ## preprocess Data set
#            transformer = data.continuization.DomainContinuizer()
#            transformer.multinomialTreatment = data.continuization.DomainContinuizer.NValues
#            transformer.continuousTreatment = data.continuization.DomainContinuizer.NormalizeBySpan
#            transformer.classTreatment = data.continuization.DomainContinuizer.Ignore
#            table = table.translate(transformer(table))
#            return feature.imputation.AverageConstructor(table)(table)
        else:
            return data.Table(fname)

    def data(self):
        return self.data_d

    def build_model(self, learner, data):
        """Build a classification meta-model.
        
        :param learner: classification learner to wrap
        :type learner: :obj:`Orange.classification.Learner`
        
        :param data: data set
        :type data: :obj:`Orange.data.Table`
        
        """

        probabilities = []
        instance_predictions = []
        instance_classes = []
        res = []
        # estimate class probabilities using CV
        for fold in range(self.folds):
            learnset = data.selectref(self.indices, fold, negate=1)
            testset = data.selectref(self.indices, fold, negate=0)
            classifier = learner(learnset)
            tcn = 0
            for i in range(len(data)):
                if (self.indices[i] == fold):
                    ex = data.Instance(testset[tcn])
                    ex.setclass("?")

                    cr = classifier(ex, classifier.GetBoth)
                    if cr[0].isSpecial():
                        raise "Classifier %s returned unknown value" % (classifier.name)

                    probabilities.append(list(cr[1]))
                    instance_predictions.append(cr[0])
                    instance_classes.append(testset[tcn].get_class())
                    tcn += 1

        return model.Model(type(learner).__name__,
                     learner(data),
                     np.array(probabilities),
                     {val: i for i, val in enumerate(self.data_d.domain.class_var.values)},
                     [x.name for x in data.domain.attributes],
                     instance_predictions,
                     instance_classes)

    def build_projection_model(self, attributes, visualizationMethod):
        """Build a projection meta-model."""

        method = "?"
        if visualizationMethod == vr.SCATTERPLOT:
            graph = data.preprocess.scaling.ScaleScatterPlotData()
            method = "SCATTERPLOT"
        elif visualizationMethod == vr.RADVIZ:
            graph = data.preprocess.scaling.ScaleLinProjData()
            graph.normalizeExamples = 1
            method = "RADVIZ"
        elif visualizationMethod in [vr.LINEAR_PROJECTION, vr.KNN_IN_ORIGINAL_SPACE]:
            graph = data.preprocess.scaling.ScaleLinProjData()
            graph.normalizeExamples = 0
            method = "SPCA"
        elif visualizationMethod == vr.POLYVIZ:
            graph = data.preprocess.scaling.ScalePolyvizData()
            graph.normalizeExamples = 1
            method = "POLYVIZ"
        else:
            print "an invalid visualization method was specified. VizRank can not run."
            return

        graph.setData(self.data_d, graph.rawSubsetData)
        attrIndices = [graph.attributeNameIndex[attr] for attr in attributes]
        #domain = data.Domain([feature.Continuous("xVar"), feature.Continuous("yVar"), graph.dataDomain.class_var])
        classListFull = graph.original_data[graph.dataClassIndex]
        table = None

        if visualizationMethod == vr.LINEAR_PROJECTION:
            freeviz = projection.linear.FreeViz(graph)
            projections = freeviz.find_projection(vr.PROJOPT_SPCA, attrIndices, set_anchors=0, percent_data_used=100)
            if projections != None:
                XAnchors, YAnchors, (attrNames, newIndices) = projections
                table = graph.create_projection_as_example_table(newIndices, XAnchors=XAnchors, YAnchors=YAnchors)
            else:
                print 'a null projection found'
        elif visualizationMethod == vr.SCATTERPLOT:
            XAnchors = YAnchors = None
            table = graph.create_projection_as_example_table(attrIndices)
        else:
            XAnchors = graph.create_xanchors(len(attrIndices))
            YAnchors = graph.create_yanchors(len(attrIndices))
            validData = graph.get_valid_list(attrIndices)
            # more than min number of examples
            if np.sum(validData) >= 10:
                classList = np.compress(validData, classListFull)
                selectedData = np.compress(validData, np.take(graph.no_jittering_scaled_data, attrIndices, axis=0), axis=1)
                sum_i = graph._getSum_i(selectedData)
                table = graph.create_projection_as_example_table(attrIndices, validData=validData, classList=classList, sum_i=sum_i, XAnchors=XAnchors, YAnchors=YAnchors)

        if not table: return None

        probabilities = []
        instance_predictions = []
        instance_classes = []
        learner = kNNLearner(k=0, rankWeight=0, distanceConstructor=distance.Euclidean(normalize=0))

        for fold in range(self.folds):
            learnset = table.selectref(self.indices, fold, negate=1)
            testset = table.select(self.indices, fold, negate=0)
            classifier = learner(learnset)

            for ex in testset:
                instance_classes.append(ex.get_class().value)
                ex.setclass("?")
                cl, prob = classifier(ex, classifier.GetBoth)
                probabilities.append(list(prob))
                instance_predictions.append(cl.value)

            if len(table) > 2000:
                break

        return model.Model(method,
                     None, #learner(table),
                     np.array(probabilities),
                     {val: i for i, val in enumerate(self.data_d.domain.class_var.values)},
                     attributes,
                     np.array(instance_predictions),
                     np.array(instance_classes),
                     XAnchors=XAnchors,
                     YAnchors=YAnchors)


    def build_rf_models(self, trees=50, max_depth=2, three_folds=False):
        if three_folds:
            indices = data.sample.SubsetIndicesCV(folds=3, stratified=data.sample.SubsetIndices.Stratified, randseed=42)(self.data_d)
        else:
            indices = data.sample.SubsetIndices2(p0=0.5, stratified=data.sample.SubsetIndices.Stratified, randseed=42)(self.data_d)

        rv = []

        for i in range(3 if three_folds else 1):
            train = self.data_d.select(indices, 0)

            min_instances = 5
            rf_learner = ensemble.forest.RandomForestLearner(trees=trees*2, base_learner=TreeLearner(), name="RF: %d trees; max depth: None; min instances: %d" % (trees, min_instances))
            rf_classifier = rf_learner(train)

            remaining_folds = range(3)
            remaining_folds.remove(i)

            for j in range(2 if three_folds else 1):

                test = self.data_d.select(indices, remaining_folds[j])

                def get_features(cls, domain):
                    #features = re.findall('{ [01] \d+ (\d+)', pickle.dumps(cls))
                    #return [domain[i].name for i in map(int, features)]
                    def tree_attr(node):
                        if not node or node.branch_selector is None:
                            return []

                        size = [node.branch_selector.class_var.name]
                        if node.branch_selector:
                            for branch in node.branches:
                                    size += tree_attr(branch)
                        return size

                    return tree_attr(cls.tree)

                models = []
                for c in rf_classifier.classifiers:
                    probabilities = []
                    instance_predictions = []
                    instance_classes = []
                    for ex in test if three_folds else train:
                        ex = data.Instance(ex)
                        instance_classes.append(ex.get_class().value)
                        ex.setclass("?")
                        cl, prob = c(ex, c.GetBoth)
                        if cl.isSpecial():
                            raise "Classifier %s returned unknown value" % c.name
                        probabilities.append(list(prob))
                        instance_predictions.append(cl.value)

                    models.append(model.Model("RF",
                                        c,
                                        np.array(probabilities),
                                        {val: k for k, val in enumerate(test.domain.class_var.values)},
                                        get_features(c, test.domain),
                                        np.array(instance_predictions),
                                        np.array(instance_classes),
                                        XAnchors=None,
                                        YAnchors=None))

                rv.append((models, rf_classifier, self.data_d.select(indices, remaining_folds[(j + 1) % 2]) if three_folds else test))

        return rv[0] if len(rv) == 1 else rv


    def _print_time(self, time_start, iter, numiter):
        time_elapsed = time.time() - time_start
        time_total = time_elapsed / iter * (numiter * (numiter-1) / 2.)
        time_remainng = int(time_total - time_elapsed)
        print iter, '/', numiter * (numiter - 1) / 2, '| remaining:', time_remainng / 60 / 60, ':', time_remainng / 60 % 60, ':', time_remainng % 60

    def build_model_matrix(self, models, dist=distance_manhattan):
        """Build a distance matrix of models given the distance measure."""

        dim = len(models)
        print "%d models to matrix -- %s" % (dim, dist.__name__)
        smx = misc.SymMatrix(dim)
        counter = 0
        time_start = time.time()
        for i in range(dim):
            for j in range(i):
                smx[i, j] = dist(models[i], models[j])

            counter += i
            if (i+1) % 1000 == 0:
                self._print_time(time_start, counter, dim)

        return smx

    def build_model_data(self, models):
        """Return an :obj:`Orange.data.Table` of model meta-data."""

        table = get_models_table()
        table.extend([model.get_instance(table.domain) for model in models])
        return table
