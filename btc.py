import pandas
import numpy
from scipy.stats import norm


''' load data '''
data = pandas.read_csv('sex.csv')
data_count = len(data)

''' get input '''
to_classify = "Person"
event = {"Height": 6,
         "Weight": 130,
         "Foot size": 8}

''' extract classes '''
categories = data[to_classify].astype('category')
classes = categories.cat.categories

''' parametrisation of numerical data '''
param_columns = ['A']
param_columns.extend(classes.tolist())
mu = pandas.DataFrame(columns=param_columns)
sigma = pandas.DataFrame(columns=param_columns)
for column in data.applymap(numpy.isreal).all().items():
    # select numeric columns
    if column[1] is True:
        row_mu = [column[0]]
        row_sigma = [column[0]]
        for c in classes:
            # select data for the class
            datum = data[data[to_classify] == c][column[0]]
            # compute mean
            m = sum(datum) / len(datum)
            row_mu.append(m)
            # compute variance (unbiased)
            row_sigma.append(sum(numpy.power((datum - m), 2)) / (len(datum) - 1))
        mu.loc[len(mu)] = row_mu
        sigma.loc[len(sigma)] = row_sigma

''' compute hypothesis '''
classes_counts = categories.value_counts()
hypothesis = dict()
for klass in classes:
    # prior probability
    hypothesis[klass] = classes_counts[klass] / data_count
    # posterior probabilities
    for category, value in event.items():
        if mu['A'].isin([category]).any() and sigma['A'].isin([category]).any():
            m = mu[mu['A'] == category][klass].values[0]
            s = sigma[sigma['A'] == category][klass].values[0]
            g = numpy.exp((-numpy.power(event[category] - m, 2))/(2*s)) / numpy.sqrt(2*numpy.pi*s)
            hypothesis[klass] *= g
        else:
            hypothesis[klass] *= len(data[(data[category] == value) & (data[to_classify] == klass)]) / classes_counts[klass]

''' normalisation '''
hypothesis = {k: v / total for total in (sum(hypothesis.values()),) for k, v in hypothesis.items()}
print(hypothesis)

