# -*- coding=utf-8 -*-
from features import *
from sklearn.svm import SVC, LinearSVC
from sklearn.metrics import accuracy_score

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
        param['nthread'] = 4
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
    val_file_name = '训练数据-ccf_first_round_user_shop_behaviorm_615.csv'
    wifi_dict = generate_wifi_dictionary(
        [os.path.join(data_dir, val_file_name)]
    )
    from prepare import Tools
    wifi_strength_dict = Tools.load_dict(os.path.join(data_dir, 'wifi_strength.txt'))
    features_wifi_show = generate_wifi_dict_feature(
        os.path.join(data_dir, val_file_name),
        wifi_dict
    )
    features_wifi_strength = generate_wifi_strength(
        os.path.join(data_dir, val_file_name),
        wifi_dict,
        wifi_strength_dict
    )
    labels, shops_id = generate_label(
        os.path.join(data_dir, val_file_name),
        os.path.join(data_dir, 'mail_shop.txt'),
        os.path.join(data_dir, 'shop_mail.txt')
    )
    labels = np.array(labels)

    features = np.concatenate(
        [do_pca_one_feature(features_wifi_show), do_pca_one_feature(features_wifi_strength)],
        axis=1)
    print np.shape(features)
    print np.shape(labels)


    KCrossValidation.do(features, labels, myXgboost.do, 'svm')