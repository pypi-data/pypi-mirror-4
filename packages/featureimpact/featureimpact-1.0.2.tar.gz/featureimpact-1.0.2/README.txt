This package let's you compute the statistical impact of features given
a scikit-learn estimator. The computation is based on the mean variation 
of the difference between quantile and original predictions. The impact
is reliable for regressors and binary classifiers.

Currently, all features must be pure numerical, non-categorical values.
