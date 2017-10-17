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
    wifi_dict = generate_wifi_dictionary(
        [os.path.join(data_dir, '训练数据-ccf_first_round_user_shop_behaviorm_690.csv')]
    )

    features = generate_wifi_dict_feature(
        os.path.join(data_dir, '训练数据-ccf_first_round_user_shop_behaviorm_690.csv'),
        wifi_dict
    )
    print np.shape(features)
    labels, shops_id = generate_label(
        os.path.join(data_dir, '训练数据-ccf_first_round_user_shop_behaviorm_690.csv'),
        os.path.join(data_dir, 'mail_shop.txt'),
        os.path.join(data_dir, 'shop_mail.txt')
    )
    features = np.array(features)
    labels = np.array(labels)

    features_pca = do_pca(features)

    print np.shape(features_pca)
    print np.shape(labels)


    KCrossValidation.do(features_pca, labels, mySVC.do, 'svm') # 决策树的得分是90.95