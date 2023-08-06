#
# Copyright John Reid 2007, 2008, 2009
#

"""
Code to implement ROC point/curve calculation and plotting.
"""


import math, numpy as N
from itertools import chain


class RocCalculator( object ):
    """
    Calculates specificities and sensitivities

    Source: wikipedia - Fawcett (2004)
    """

    def __init__(self, tp=0, fp=0, tn=0, fn=0):
        self.tp = tp
        "Number of true positives."

        self.fp = fp
        "Number of false positives."

        self.tn = tn
        "Number of true negatives."

        self.fn = fn
        "Number of false negatives."


    def __cmp__(self, other):
        "Comparison."
        diff = self.sensitivity() - other.sensitivity()
        if diff < 0.:
            return -1
        elif diff > 0.:
            return 1.
        else:
            diff = other.specificity() - self.specificity()
            if diff < 0.:
                return -1
            elif diff > 0.:
                return 1.
            else:
                return 0


    def distance(self, other):
        "Measure of distance between points."
        return (self.sensitivity()-other.sensitivity()) * (other.specificity()-self.specificity())


    def __call__(self, truth, prediction):
        "Updates this ROC calculator with one truth/prediction pair"
        if prediction:
            if truth: self.tp += 1
            else: self.fp += 1
        else:
            if truth: self.fn += 1
            else: self.tn += 1

    def __add__(self, rhs):
        "Add this RocCalculator to another and return the result."
        result = RocCalculator()
        result.tp = self.tp + rhs.tp
        result.tn = self.tn + rhs.tn
        result.fp = self.fp + rhs.fp
        result.fn = self.fn + rhs.fn
        return result

    def normalise(self, rhs):
        "Normalise this RocCalculator so that tp+tn+fp+fn=1."
        sum = float(self.tp+self.tn+self.fp+self.fn)
        self.tp /= sum
        self.tn /= sum
        self.fp /= sum
        self.fn /= sum

    @staticmethod
    def always_predict_true():
        "A RocCalculator for a predictor that always predicts True"
        result = RocCalculator()
        result.tp = result.fp = 1
        result.tn = result.fn = 0
        return result

    @staticmethod
    def always_predict_false():
        "A RocCalculator for a predictor that always predicts False"
        result = RocCalculator()
        result.tp = result.fp = 0
        result.tn = result.fn = 1
        return result

    def sensitivity(self):
        "TP/(TP+FN)"
        denominator = self.tp + self.fn
        if denominator:
            return float(self.tp)/denominator
        else:
            return 1.0
    hit_rate = recall = sensitivity

    def specificity(self):
        "TN/(TN+FP)"
        denominator = self.tn + self.fp
        if denominator:
            return float(self.tn)/denominator
        else:
            return 1.0

    def false_positive_rate(self):
        "FP/(TN+FP)"
        return 1.0 - self.specificity()

    def positive_predictive_value(self):
        "TP/(TP+FP)"
        denominator = self.tp + self.fp
        if denominator:
            return float(self.tp)/denominator
        else:
            return 1.0
    precision = positive_predictive_value

    def negative_predictive_value(self):
        "TN/(TN+FN)"
        denominator = self.tn + self.fn
        if denominator:
            return float(self.tn)/denominator
        else:
            return 1.0

    def performance_coefficient(self):
        "TP/(TP+FN+FP) see: Pevzner & Sve"
        denominator = self.tp + self.fn + self.fp
        if denominator:
            return float(self.tp)/denominator
        else:
            return 1.0

    def accuracy(self):
        "(TP+TN)/(TP+TN+FP+FN)"
        denominator = self.tp + self.tn + self.fn + self.fp
        if denominator:
            return float(self.tp+self.tn)/denominator
        else:
            return 1.0
    
    def average_performance(self):
        "(sensitivity()+positive_predictive_value())/2"
        return (self.sensitivity() + self.positive_predictive_value()) / 2.

    def correlation_coefficient(self):
        "(TP.TN-FN.FP)/sqrt((TP+FN)(TN+FP)(TP+FP)(TN+FN)) see: Burset & Guigo"
        denominator = math.sqrt((self.tp+self.fn)*(self.tn+self.fn)*(self.tp+self.fp)*(self.tn+self.fp))
        numerator = self.tp*self.tn-self.fn*self.fp
        if denominator:
            return numerator/denominator
        else:
            if 0.0 == numerator:
                return 0.0
            else:
                return 1.0

    def __str__(self):
        return '''TP: %d; FP: %d; TN: %d; FN: %d
sensitivity:               %.3f    TP/(TP+FN)
specificity:               %.3f    TN/(TN+FP)
positive predictive value: %.3f    TP/(TP+FP)
performance coefficient:   %.3f    TP/(TP+FN+FP)
correlation coefficient:   %.3f    (TP.TN-FN.FP)/sqrt((TP+FN)(TN+FP)(TP+FP)(TN+FN))''' % (
self.tp, self.fp, self.tn, self.fn,
                self.sensitivity(),
                self.specificity(),
                self.positive_predictive_value(),
                self.performance_coefficient(),
                self.correlation_coefficient(),
        )

def update_roc(roc, truth_prediction_iterable):
    "for each (truth,prediction) in iterable, update the ROC calculator"
    for truth, prediction in truth_prediction_iterable:
        roc(truth, prediction)



def get_new_roc_parameter(rocs, for_specificity=True):
    """
    Takes a sequence of (parameter, roc) tuples and returns a new parameter that should be tested
    next.

    It chooses this parameter by sorting the sequence and taking the mid-point between
    the parameters with the largest absolute difference between their specificities or
    sensitivities (depending on for_specificity parameter).
    """
    rocs.sort()
    statistic = for_specificity and RocCalculator.specificity or RocCalculator.sensitivity
    diffs = [
      (abs(statistic(rocs[i][1])-statistic(rocs[i+1][1])), (rocs[i][0]+rocs[i+1][0])/2)
      for i
      in xrange(len(rocs)-1)
    ]
    return max(diffs)[1]


def plot_roc_points(rocs, **plot_kwds):
    """
    Plots TPR versus FPR for the ROCs in rocs. Adds points at (0,0) and (1,1).

    :param rocs: A sequence of ROCs.
    :param plot_kwds: All extra keyword arguments are passed to the pylab.plot call.
    :returns: The result of pylab.plot call.
    """
    from pylab import plot
    return plot(
     [s for s in chain((0.,), (1. - roc.specificity() for roc in rocs), (1.,))],
     [s for s in chain((0.,), (roc.sensitivity() for roc in rocs), (1.,))],
     **plot_kwds
    )


def plot_precision_versus_recall(rocs, **plot_kwds):
    """
    Plots precision versus recall for the ROCs in rocs. Adds points at (0,1) and (1,0).

    :param rocs: A sequence of ROCs.
    :param plot_kwds: All extra keyword arguments are passed to the pylab.plot call.
    :returns: The result of pylab.plot call.
    """
    from pylab import plot
    points = [(roc.recall(), roc.precision()) for roc in rocs]
    #points.sort()
    return plot(
            [recall for recall, precision in points],
            [precision for recall, precision in points],
            **plot_kwds
    )


def plot_precision_recall(roc_thresholds, recall_plot_kwds={}, precision_plot_kwds={}, plot_fn=None):
    """
    Plots a precision-recall curve for the given ROCs.

    :param roc_thresholds: A sequence of tuples (ROC, threshold).
    :param recall_plot_kwds: Passed to the pylab.plot call for the recall.
    :param precision_plot_kwds: Passed to the pylab.plot call for the precision.
    :param plot_fn: Function used to plot. Use pylab.semilogx for log scale threshold axis.
    :returns: The result of 2 pylab.plot calls as a tuple (recall, precision).
    """
    if None == plot_fn:
        from pylab import plot
        plot_fn = plot
    if 'label' not in recall_plot_kwds:
        recall_plot_kwds['label'] = 'Recall'
    if 'color' not in recall_plot_kwds:
        recall_plot_kwds['color'] = 'blue'
    if 'linestyle' not in recall_plot_kwds:
        recall_plot_kwds['linestyle'] = ':'
    recall_result = plot_fn(
        [t for roc, t in roc_thresholds],
        [roc.recall() for roc, t in roc_thresholds],
        **recall_plot_kwds
    )
    if 'label' not in precision_plot_kwds:
        precision_plot_kwds['label'] = 'Precision'
    if 'color' not in precision_plot_kwds:
        precision_plot_kwds['color'] = 'maroon'
    if 'linestyle' not in precision_plot_kwds:
        precision_plot_kwds['linestyle'] = '--'
    precision_result = plot_fn(
        [t for roc, t in roc_thresholds],
        [roc.precision() for roc, t in roc_thresholds],
        **precision_plot_kwds
    )
    return recall_result, precision_result


def area_under_curve(rocs, include_0_0=True, include_1_1=True):
    """
    :param rocs: The ROC points.
    :param include_0_0: True to include extra point for origin of ROC curve.
    :param include_1_1: True to include extra point at (1,1) in ROC curve.

    :returns: The area under the ROC curve given by the ROC points.
    """
    x_axis = []
    y_axis = []
    if include_0_0:
        x_axis.append(0.)
        y_axis.append(0.)
    x_axis.extend(1. - roc.specificity() for roc in rocs)
    y_axis.extend(roc.sensitivity() for roc in rocs)
    if include_1_1:
        x_axis.append(1.)
        y_axis.append(1.)
    last_x, last_y = None, None
    area = 0.
    for x, y in zip(x_axis, y_axis):
        if last_x != None: # if not first point
            area += (x-last_x) * (y+last_y) / 2
        last_x, last_y = x, y
    return area


def plot_random_classifier(**kwargs):
    """Draw a random classifier on a ROC plot. Black dashed line by default."""
    from pylab import plot
    if 'color' not in kwargs:
        kwargs['color'] = 'black'
    if 'linestyle' not in kwargs:
        kwargs['linestyle'] = ':'
    plot(
    [0,1],
    [0,1],
    **kwargs
)


def label_plot():
    """Label the x and y axes of a ROC plot."""
    import pylab as P
    P.xlabel('1 - specificity: 1-TN/(TN+FP)')
    P.ylabel('sensitivity: TP/(TP+FN)')


def label_precision_versus_recall():
    """Label the x and y axes of a precision versus recall plot."""
    import pylab as P
    P.xlabel('Recall: TP/(TP+FN)')
    P.ylabel('Precision: TP/(TP+FP)')
    P.xlim(0, 1)
    P.ylim(0, 1)


def label_precision_recall():
    """Label the x and y axes of a precision-recall plot."""
    import pylab as P
    P.xlabel('threshold')
    P.ylabel('precision/recall')


def count_threshold_classifications(thresholds, value):
    """
    Take a list of thresholds (in sorted order) and count how many would be classified positive and negative at the given value.

    :returns: (num_positive, num_negative).
    """
    from bisect import bisect_right
    idx = bisect_right(thresholds, value)
    return len(thresholds) - idx, idx


def roc_for_threshold(positive_thresholds, negative_thresholds, value):
    """
    Take lists of positive and negative thresholds (in sorted order)
    and calculate a ROC point for the given value.
    """
    tp, fn = count_threshold_classifications(positive_thresholds, value)
    fp, tn = count_threshold_classifications(negative_thresholds, value)
    return RocCalculator(tp, fp, tn, fn)


def make_roc_from_threshold_fn(positive_thresholds, negative_thresholds):
    ":returns: A function that calculates a ROC point given a threshold."
    def local_roc_for_threshold(value):
        return roc_for_threshold(positive_thresholds, negative_thresholds, value)
    return local_roc_for_threshold


def rocs_from_thresholds(positive_thresholds, negative_thresholds, num_points=32):
    """
    Takes 2 sorted lists: one list is of the thresholds required to classify the positive examples as positive
    and the other list is of the thresholds required to classify the negative examples as positive.

    :returns: A list of ROC points.
    """
    min_threshold = min(positive_thresholds[0], negative_thresholds[0])
    max_threshold = max(positive_thresholds[-1], negative_thresholds[-1])
    rocs = map(
                make_roc_from_threshold_fn(positive_thresholds, negative_thresholds),
                N.linspace(min_threshold, max_threshold, num_points)[::-1]
        )
    return rocs


def pick_roc_thresholds(roc_for_threshold_fn, min_threshold, max_threshold, num_points=32):
    """
    Tries to pick thresholds to give a smooth ROC curve.

    :returns: A list of (roc point, threshold) tuples.
    """
    def add_threshold(threshold):
        "Calculate the ROC point and add to list."
        rocs.append((roc_for_threshold_fn(threshold), threshold))
        rocs.sort()

    def compare_2_points(x1, x2):
        "Compare 2 ROC points to see how far apart they are."
        rp1, t1 = x1
        rp2, t2 = x2
        return (rp1.distance(rp2), (t1+t2)/2.)

    rocs = []
    add_threshold(min_threshold)
    add_threshold(max_threshold)

    while(len(rocs) < num_points):
        # find best new threshold
        biggest_distance, new_threshold = max(map(compare_2_points, rocs[:-1], rocs[1:]))
        add_threshold(new_threshold)

    return rocs


def create_rocs_from_thresholds(positive_thresholds, negative_thresholds, num_points=32):
    """
    Takes 2 sorted lists: one list is of the thresholds required to classify the positive examples as positive
    and the other list is of the thresholds required to classify the negative examples as positive.

    :returns: A list of tuples (ROC point, threshold).
    """
    return pick_roc_thresholds(
                make_roc_from_threshold_fn(positive_thresholds, negative_thresholds),
            min_threshold=min(positive_thresholds[0], negative_thresholds[0]),
            max_threshold=max(positive_thresholds[-1], negative_thresholds[-1]),
            num_points=num_points
        )


def picked_rocs_from_thresholds(positive_thresholds, negative_thresholds, num_points=32):
    """
    Takes 2 sorted lists: one list is of the thresholds required to classify the positive examples as positive
    and the other list is of the thresholds required to classify the negative examples as positive.

    :returns: A list of ROC points.
    """
    return [roc for roc, t in create_rocs_from_thresholds(positive_thresholds, negative_thresholds, num_points=num_points)]



def resize_negative_examples(positive_thresholds, negative_thresholds, num_negative=50):
    """
    Reduce the positive and negative thresholds such that there are just 50 (or num_negative) negative examples.
    The positive thresholds are trimmed accordingly.
    """
    if num_negative > len(negative_thresholds):
        raise RuntimeError('Not enough negative examples (%d). Requested %d' % (len(negative_thresholds), num_negative))
    import bisect
    negative_thresholds = negative_thresholds[-num_negative:]
    threshold = negative_thresholds[0]
    positive_cutoff = bisect.bisect(positive_thresholds, threshold)
    positive_thresholds = positive_thresholds[positive_cutoff:]
    return positive_thresholds, negative_thresholds


def auc50_wrong(positive_thresholds, negative_thresholds, num_negative=50, num_points=32):
    """
    Calculate the AUC50 as in Gribskov & Robinson 'Use of ROC analysis to evaluate sequence pattern matching'
    """
    if num_negative > len(negative_thresholds):
        raise RuntimeError('Not enough negative examples (%d). Requested %d' % (len(negative_thresholds), num_negative))
    threshold = negative_thresholds[-num_negative]
    roc_thresholds = pick_roc_thresholds(
        make_roc_from_threshold_fn(positive_thresholds, negative_thresholds),
        min_threshold=threshold,
        max_threshold=max(positive_thresholds[-1], negative_thresholds[-1]),
        num_points=num_points
    )
    auc50 = area_under_curve([roc for roc, t in roc_thresholds], include_1_1=False)
    return auc50, roc_thresholds


def auc50(positive_thresholds, negative_thresholds, num_negative=50, num_points=32):
    """
    Calculate the AUC50 as in Gribskov & Robinson 'Use of ROC analysis to evaluate sequence pattern matching'
    """
    if num_negative > len(negative_thresholds):
        raise RuntimeError('Not enough negative examples (%d). Requested %d' % (len(negative_thresholds), num_negative))
    roc_thresholds = pick_roc_thresholds(
        make_roc_from_threshold_fn(positive_thresholds, negative_thresholds[-num_negative:]),
        min_threshold=min(positive_thresholds[0], negative_thresholds[0]),
        max_threshold=max(positive_thresholds[-1], negative_thresholds[-1]),
        num_points=num_points
    )
    auc50 = area_under_curve([roc for roc, t in roc_thresholds])
    return auc50, roc_thresholds


if '__main__' == __name__:
    import numpy.random as R, pylab as P

    num_examples = 1000
    R.seed(2)
    positive_thresholds = R.normal(size=num_examples, loc=.4, scale=2.)
    positive_thresholds.sort()
    negative_thresholds = R.normal(size=num_examples, loc=-.4, scale=1.)
    negative_thresholds.sort()

    P.close('all')

    roc_thresholds = create_rocs_from_thresholds(positive_thresholds, negative_thresholds, num_points=32)
    rocs = [roc for roc, t in roc_thresholds]
    auc = area_under_curve(rocs)

    P.figure()
    plot_roc_points(rocs, label='classifier : AUC=%.3f' % auc, color='blue', marker='s')
    plot_random_classifier(label='Random')
    label_plot()
    P.legend(loc='lower right')
    P.savefig('output/ROC.eps')
    P.savefig('output/ROC.png')
    P.show()
    P.close()

#       P.figure()
#       plot_precision_versus_recall(rocs, label='classifier : AUC=%.3f' % auc, color='blue', marker='s')
#       label_precision_versus_recall()
#       P.legend(loc='lower left')
#       P.savefig('output/Precision-versus-Recall.eps')
#       P.savefig('output/Precision-versus-Recall.png')
#       P.show()

#       P.figure()
#       plot_precision_recall(roc_thresholds)
#       label_precision_recall()
#       P.legend(loc='lower center')
#       P.savefig('output/Precision-Recall.eps')
#       P.savefig('output/Precision-Recall.png')
#       P.show()

    positive_thresholds, negative_thresholds = resize_negative_examples(positive_thresholds, negative_thresholds)
    roc_thresholds = create_rocs_from_thresholds(positive_thresholds, negative_thresholds, num_points=32)
    rocs = [roc for roc, t in roc_thresholds]
    auc = area_under_curve(rocs)
    P.figure()
    plot_roc_points(rocs, label='classifier : AUC=%.3f' % auc, color='blue', marker='s')
    plot_random_classifier(label='Random')
    label_plot()
    P.legend(loc='lower right')
    P.savefig('output/ROC50.eps')
    P.savefig('output/ROC50.png')
    P.show()
    P.close()
