from base import ComboFeature, Feature
from pandas import DataFrame, Series, concat


class ComboMap(ComboFeature):
    """ abstract base for binary operations on features """
    def __init__(self, features, name=None, fillna=0):
        super(ComboMap, self).__init__(features)
        self.fillna = fillna

    def _combine(self, datas, function):
        data = datas[0]
        data = data.astype('float64')
        for d in datas[1:]:
            if isinstance(d, DataFrame):
                if len(d.columns) == 1:
                    d = d[d.columns[0]]
                else:
                    raise NotImplementedError
            cols = ['%s, %s' % (c, d.name) for c in data.columns]
            data = function(data, d.astype('float64'), axis=0)
            data = data.fillna(self.fillna)
            data.columns = cols
        return data

class Add(ComboMap):
    def combine(self, datas):
        return self._combine(datas, DataFrame.add)
class Divide(ComboMap):
    def combine(self, datas):
        return self._combine(datas, DataFrame.div)
class Multiply(ComboMap):
    def combine(self, datas):
        return self._combine(datas, DataFrame.mul)


class Interactions(ComboFeature):
    def combine(self, datas):
        cols = []
        colnames = []
        data = concat(datas, axis=1)
        n = len(data.columns)
        for i in range(n):
            d1 = data[data.columns[i]]
            for j in range(i+1, n):
                d2 = data[data.columns[j]]
                d = d1.mul( d2)
                colnames.append('%s, %s' % (d1.name, d2.name))
                cols.append(d)
        return concat(cols, keys=colnames, axis=1)

class OutlierCount(ComboFeature):
    # TODO: add prep
    def __init__(self, features, stdevs=5):
        super(OutlierCount, self).__init__(features)
        self.stdevs = stdevs
        self._name = self._name + '_%d'%stdevs

    def is_outlier(self, x, mean, std):
        return int(abs((x-mean)/std) > self.stdevs)

    def combine(self, datas):
        count = DataFrame(np.zeros(len(datas[0])), index=datas[0].index)
        eps = 1.0e-8
        col_names = []
        for data in datas:
            for col in data.columns:
                d = data[col]
                m = d.mean()
                s = d.std()
                if s < eps:
                    continue
                d = d.map(lambda x: self.is_outlier(x, m, s))
                col_names.append(col)
                count = count.add(d, axis=0)
        count.columns = [','.join(col_names)]
        return count


from sklearn.decomposition import PCA
class SVDDimensionReduction(ComboFeature):
    def __init__(self, feature, pct_keep=1., n_keep=None):
        super(SVDDimensionReduction, self).__init__(feature)
        self.pct_keep = pct_keep
        self.n_keep = n_keep
        self._name = self._name + '_%s'%(n_keep if n_keep else pct_keep)

    def combine(self, datas):
        data = concat(datas, axis=1)
        nvecs = self.n_keep if self.n_keep else int(self.pct_keep * len(data.columns))
        pca = PCA(n_components=nvecs)
        x = pca.fit_transform(data.values)
        df = DataFrame(x, columns=['Vector%d'%i for i in range(nvecs)],
                index=data.index)
        return df

