# -*- coding=utf-8 -*-
from features import *
from sklearn.svm import SVC, LinearSVC
from sklearn.metrics import accuracy_score
from Config import Config

class mySVC:
    @staticmethod
    def do(train_data, train_label, test_data, test_label=None):
        clf = SVC()
        clf.fit(train_data, train_label)
        predicts = clf.predict(test_data)
        acc = None
        if test_label is not None:
            acc = accuracy_score(test_label, predicts)
            print acc
        return predicts, acc

class myLinearSVC:
    @staticmethod
    def do(train_data, train_label, test_data, test_label=None):
        svm = LinearSVC()
        svm.fit(train_data, train_label)
        predicts = svm.predict(test_data)
        acc = None
        if test_label is not None:
            acc = accuracy_score(test_label, predicts)
            print acc
        return predicts, acc

class myXgboost:
    @staticmethod
    def do(training_data, train_label, test_data, test_label=None):
        import xgboost as xgb
        param = {}
        # use softmax multi-class classification
        param['objective'] = 'multi:softmax'
        # scale weight of positive examples
        param['eta'] = 0.1
        param['max_depth'] = 6
        param['silent'] = 1
        param['nthread'] = 8
        param['num_class'] = np.max(train_label) + 1
        plst = param.items()
        dTrain = xgb.DMatrix(training_data, label=train_label)
        num_round = 20
        bst = xgb.train(plst, dTrain, num_round)
        dTest = xgb.DMatrix(test_data)
        yPred = bst.predict(dTest)
        acc = None
        if test_label is not None:
            acc = accuracy_score(test_label, yPred)
            print acc
        return yPred, acc

# coding=gbk
# k折交叉验证
from sklearn.model_selection import KFold

k_nums = 10
class KCrossValidation:

    @staticmethod
    def do(data, label, method, method_name):
        average_score = 0.0
        kf = KFold(n_splits=k_nums, shuffle=True)
        for train_index, test_index in kf.split(data, label):
            train_data, test_data = data[train_index], data[test_index]
            train_label, test_label = label[train_index], label[test_index]
            predicted_res, score = method(train_data, train_label, test_data, test_label)
            average_score += score
        average_score /= k_nums
        print 'function name is ', method_name, 'average score is ', average_score

class RunTest:
    @staticmethod
    def do(train_feature, train_label, test_feature, method, method_name):
        predict_res, acc = method(train_feature, train_label, test_feature, None)
        return predict_res, acc

if __name__ == '__main__':
    def do_pca_one_feature(features, n_components=100):
        features = np.array(features)
        features_pca = do_pca(features, n_components=n_components)
        return features_pca
    mail_id = 'm_615'
    training_file_name = '训练数据-ccf_first_round_user_shop_behavior'+ mail_id +'.csv'
    val_file_name = 'AB榜测试集-evaluation_public' + mail_id +'.csv'

    '''
        测试版本2特征的效果
    '''
    from generage_predict import extract_features_version3
    train_features_wifi, train_labels_wifi, _, _ = extract_features_version3(
        path=os.path.join(Config.data_dir, val_file_name),
        mail_id=mail_id,
        n_components=100
    )

    '''
        测试版本3特征的效果
    '''
    # from generage_predict import extract_features_version3
    #
    # train_features_distance, train_labels_distance, _, _ = extract_features_version3(
    #     path=os.path.join(Config.data_dir, val_file_name),
    #     mail_id=mail_id
    # )
    # train_features_distance = np.array(train_features_distance)
    # train_labels_distance = np.array(train_labels_distance)
    # print np.shape(train_labels_wifi), np.shape(train_labels_distance)
    # if not (train_labels_wifi == train_labels_distance).all():
    #     print 'Error, label is not equal'
    #  train_features = np.concatenate([train_features_wifi, train_features_distance], axis=1)
    train_features = train_features_wifi
    print np.shape(train_features)
    KCrossValidation.do(train_features, train_labels_wifi, myXgboost.do, 'svm')