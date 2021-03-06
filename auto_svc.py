# -*- coding: utf-8 -*-
"""auto_svc

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1ay4h6RYubrd2ct94kp0aYS_eKk7PcPDo
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_regression
from sklearn import svm
import matplotlib.pyplot as plt
import sys

def get_data(url, target):
  df = pd.read_csv(url)
  results = df.dtypes
  cols = df.columns
  for res in range(len(results)):
    # Drop columns if they are not numerical, unless it contains the target variable. Also drop na columns.
    if results[res] not in ['float64', 'int64'] and cols[res] != target or len(df.loc[:,cols[res]]) != len(df.loc[:,cols[res]].dropna()):
      df = df.drop(cols[res], axis=1)
  # store data in dict of string : numpy array for easier use.
  data = {}
  targ = {}
  new_cols = df.columns
  for col in new_cols:
    if col == target:
      targ[col] = np.array(list(df.loc[:,col]))
    else:
      data[col] = np.array(list(df.loc[:,col]))
  return data, targ

def get_train_data(data):
  X = []
  for key in data.keys():
    X.append(data[key])
  new_X = []
  for i in range(len(X[0])):
    entry = []
    for j in range(len(X)):
      entry.append(X[j][i])
    new_X.append(entry)
  return np.array(new_X)

def get_most_imp(url, target):
  data, targ = get_data(url, target)
  X = get_train_data(data)
  y = targ[target]
  regr = RandomForestClassifier(max_depth=2, random_state=0)
  regr.fit(X, y)
  imps = list(regr.feature_importances_)
  two_highest = []
  keys = list(data.keys())
  for i in range(len(imps)):
    if i <= 1:
      two_highest.append([keys[i], imps[i]])
    else:
      if two_highest[0][1] > two_highest[1][1]:
        if imps[i] > two_highest[1][1]:
          two_highest[1] = [keys[i], imps[i]]
      else:
        if imps[i] > two_highest[0][1]:
          two_highest[0] = [keys[i], imps[i]]
  return data, targ, two_highest

def get_svcs(url, target, outfile):
  data, targ, most_imp = get_most_imp(url, target)
  new_data = {}
  for key in data.keys():
    if key == most_imp[0][0] or key == most_imp[1][0]:
      new_data[key] = data[key] / max(data[key])
  X = get_train_data(new_data)
  y = targ[target]

  unique = []
  for i in range(len(y)):
    if y[i] not in unique:
      unique.append(y[i])
    if len(unique) == 3:
      pass
  new_y = []
  for i in range(len(y)):
    if y[i] == unique[0]:
      new_y.append(0)
    elif y[i] == unique[1]:
      new_y.append(1)
    else:
      new_y.append(2)

  y = np.array(new_y)
  h = .02  # step size in the mesh
  if len(X) > 2000:
    X = X[0:2000]
    y = y[0:2000]
  # we create an instance of SVM and fit out data. We do not scale our
  # data since we want to plot the support vectors
  C = 1.0  # SVM regularization parameter
  svc = svm.SVC(kernel='linear', C=C).fit(X, y)
  rbf_svc = svm.SVC(kernel='rbf', gamma=0.7, C=C).fit(X, y)
  poly_svc = svm.SVC(kernel='poly', degree=3, C=C).fit(X, y)
  lin_svc = svm.LinearSVC(C=C).fit(X, y)

  # create a mesh to plot in
  x_min, x_max = X[:, 0].min() - 1, X[:, 0].max() + 1
  y_min, y_max = X[:, 1].min() - 1, X[:, 1].max() + 1
  xx, yy = np.meshgrid(np.arange(x_min, x_max, h),
                     np.arange(y_min, y_max, h))

  # title for the plots
  titles = ['SVC with linear kernel',
          'LinearSVC (linear kernel)',
          'SVC with RBF kernel',
          'SVC with polynomial (degree 3) kernel']

  plt.figure(figsize=(15,15))
  for i, clf in enumerate((svc, lin_svc, rbf_svc, poly_svc)):
    # Plot the decision boundary. For that, we will assign a color to each
    # point in the mesh [x_min, x_max]x[y_min, y_max].
    plt.subplot(2, 2, i + 1)
    plt.subplots_adjust(wspace=0.4, hspace=0.4)

    Z = clf.predict(np.c_[xx.ravel(), yy.ravel()])

    # Put the result into a color plot
    Z = Z.reshape(xx.shape)
    plt.contourf(xx, yy, Z, cmap=plt.cm.coolwarm, alpha=0.8)

    # Plot also the training points
    plt.scatter(X[:, 0], X[:, 1], c=y, cmap=plt.cm.coolwarm)
    plt.xlabel(most_imp[0][0])
    plt.ylabel(most_imp[1][0])
    plt.xlim(xx.min(), xx.max())
    plt.ylim(yy.min(), yy.max())
    plt.xticks(())
    plt.yticks(())
    plt.title(titles[i] + " | Seperability = " + str(round(clf.score(X, y), 2)) + "%")

  plt.savefig("SVC")

if __name__=="__main__":
  url = sys.argv[1]
  print(url)
  targ_col = sys.argv[2]
  get_svcs = get_svcs(url, targ_col, "svc.png")
