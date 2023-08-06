import numpy as np

class ConfusionMatrix(object):
    def __init__(self, actual_predicted_pairs, categories):
        self._categories = categories
        self.M = self._build(actual_predicted_pairs)

    def _build(self, actual_predicted_pairs):
        m = np.zeros((len(self._categories), len(self._categories)))
        for actual, predicted in actual_predicted_pairs:
            m[self._categories.index(predicted), self._categories.index(actual)] += 1
        return m

    def n_correct(self):
        return np.sum(np.diagonal(self.M))

    def n_incorrect(self):
        return self.N() - self.n_correct();

    def precision(self):
        return np.diagonal(self.M) / np.sum(self.M, axis=1)

    def precision_total(self):
        return np.sum(np.diagonal(self.M)) / np.sum(self.M)

    def recall(self):
        return np.diagonal(self.M) / np.sum(self.M, axis=0)

    def f_measure(self, beta=1):
        return (1 + beta**2) * \
               (self.precision()*self.recall()) / \
               (beta**2*self.precision()+self.recall())

    def N(self):
        return np.sum(self.M)

    def one_vs_all(self, cat_index):
        return 0

class PrecisionRecallMatrix(object):
    def __init__(self, tp=.0, tn=.0, fp=.0, fn=.0):
        self.tp = tp
        self.tn = tn
        self.fp = fp
        self.fn = fn

    def precision(self):
        """
        Precision is tp / (tp + fp).
        If no predictions were made (tp + fp = 0), a conventional precision score of 1.0 is returned
        """
        if (self.tp + self.fp) > 0:
            return self.tp / (self.tp + self.fp)
        else:
            return 1.0

    def recall(self):
        """
        Recall is tp / (tp + fn)
        """
        return self.tp / (self.tp + self.fn)

    def accuracy(self):
        """
        Accuracy is (tp + tn) / (tp + tn + fp + fn)
        """
        return (self.tp + self.tn) / (self.tp + self.tn + self.fp + self.fn)

    def f_measure(self, beta=1):
        return (1 + beta**2) * \
               (self.precision()*self.recall()) / \
               (beta**2*self.precision()+self.recall())

    def __repr__(self):
        return "{}(tp={}, tn={}, fp={}, fn={})".format(self.__class__.__name__, self.tp, self.tn, self.fp, self.fn)

class PrecisionRecallFormatter(object):
    @classmethod
    def parse_json(cls, input):
        pass

