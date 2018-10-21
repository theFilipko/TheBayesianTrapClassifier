import pandas

''' load data '''
data = pandas.read_csv('golf.csv')
data_count = len(data)

''' get input '''
to_classify = "Play"
event = {"Outlook": "sunny",
         "Temperature": "cool",
         "Humidity": "high"}

''' extract classes '''
categories = data[to_classify].astype('category')
classes = categories.cat.categories

''' compute hypthesis '''
classes_counts = categories.value_counts()
hypothesis = dict()
for klass in classes:
    # prior probability
    hypothesis[klass] = classes_counts[klass] / data_count
    # posterior probabilities
    for category, value in event.items():
        hypothesis[klass] *= len(data[(data[category] == value) & (data[to_classify] == klass)]) / classes_counts[klass]

''' normalisation '''
hypothesis = {k: v / total for total in (sum(hypothesis.values()),) for k, v in hypothesis.items()}
print(hypothesis)

