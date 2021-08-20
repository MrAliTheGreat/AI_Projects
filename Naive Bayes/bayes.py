from __future__ import unicode_literals

import pandas as pd
from hazm import *



trainDataframe = pd.read_csv("./books_dataset/books_train.csv")

print(trainDataframe.to_string())



