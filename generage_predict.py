# -*- coding=utf-8 -*-
import Ipynb_importer
import features
import prepare
import os
import numpy as np
from glob import glob
import cross_validation
from features import *
from Config import Config
'''
    方法：只是用Wi-Fi信号出现的次数作为我们的特征，使用线性SVM
    结果：0.7866
'''
def extract_features_version1(path, mail_id):
    '''
    :param path: 测试文件的路径
    :param mail_id: 当前预测的mail的ID
    :return: 训练集合的feature，label 测试集合的feature, 以及当前商场对应的shop 的ID（主要是用来写入csv文件）
    '''
    training_path = os.path.join(Config.data_dir, '训练数据-ccf_first_round_user_shop_behaviorm_' + mail_id + '.csv')
    wifi_dict = features.generate_wifi_dictionary(
        [training_path, path]
    )
    print 'the number of wifi source is ', len(wifi_dict)
    training_features = features.generate_wifi_dict_feature(training_path, wifi_dict)
    print 'max feature number is ', np.max(training_features)
    training_labels, shop_ids = features.generate_label(
        csv_path=training_path,
        mail_shop_path=Config.mail_shop_txt_path,
        shop_mail_path=Config.shop_mail_txt_path
    )
    testing_features = features.generate_wifi_dict_feature(path, wifi_dict)
    training_features = np.array(training_features)
    testing_features = np.array(testing_features)
    training_labels = np.array(training_labels)
    all_features = np.concatenate([training_features, testing_features])
    all_features = features.do_pca(all_features)
    training_features = all_features[:len(training_features)]
    testing_features = all_features[len(training_features):]
    print 'after pca operation, the shape of feature is ', np.shape(all_features)
    return training_features, training_labels, testing_features, shop_ids

'''
    方法：只是用Wi-Fi信号出现的次数作为我们的特征和Wi-Fi信号的强度作为组合特征，使用线性Xgboost分类器
    结果：0.85 n_components 选择的是100
'''
def extract_features_version2(path, mail_id, wifi_strength_txt_path, n_components=100):
    '''
    :param path: 测试文件的路径
    :param mail_id: 当前预测的mail的ID
    :return: 训练集合的feature，label 测试集合的feature, 以及当前商场对应的shop 的ID（主要是用来写入csv文件）
    '''

    def do_pca_one_feature(features, n_components=100):
        features = np.array(features)
        features_pca = do_pca(features, n_components=n_components)
        return features_pca

    training_path = os.path.join(Config.data_dir, '训练数据-ccf_first_round_user_shop_behaviorm_' + mail_id + '.csv')
    wifi_dict = features.generate_wifi_dictionary(
        [training_path, path]
    )
    wifi_strength_dict = prepare.Tools.load_dict(wifi_strength_txt_path)
    training_features_show = features.generate_wifi_dict_feature(training_path, wifi_dict)
    training_features_strength = features.generate_wifi_strength(training_path, wifi_dict, wifi_strength_dict)
    training_labels, shop_ids = features.generate_label(
        csv_path=training_path,
        mail_shop_path=Config.mail_shop_txt_path,
        shop_mail_path=Config.shop_mail_txt_path
    )

    testing_features_show = features.generate_wifi_dict_feature(path, wifi_dict)
    testing_features_strength = features.generate_wifi_strength(path, wifi_dict, wifi_strength_dict)
    all_features_show = np.concatenate([training_features_show, testing_features_show])
    all_features_strength = np.concatenate([training_features_strength, testing_features_strength])
    all_features = np.concatenate(
        [do_pca_one_feature(all_features_show, n_components=n_components),
         do_pca_one_feature(all_features_strength, n_components=n_components)],
        axis=1
    )
    training_labels = np.array(training_labels)
    training_features = all_features[:len(training_labels)]
    testing_features = all_features[len(training_labels):]
    print 'after pca operation, the shape of feature is ', np.shape(all_features)
    return training_features, training_labels, testing_features, shop_ids


'''
    方法：只是用Wi-Fi信号出现的次数作为我们的特征和Wi-Fi信号的强度作为组合特征，使用线性Xgboost分类器
         相比于特征3，我们只选用商场的Wi-Fi作为我们的特征，而不使用移动Wi-Fi
    结果：？ n_components 选择的是100
'''
def extract_features_version3(path, mail_id, n_components=100):
    '''
    :param path: 测试文件的路径
    :param mail_id: 当前预测的mail的ID
    :return: 训练集合的feature，label 测试集合的feature, 以及当前商场对应的shop 的ID（主要是用来写入csv文件）
    '''

    def do_pca_one_feature(features, n_components=100):
        features = np.array(features)
        features_pca = do_pca(features, n_components=n_components)
        return features_pca

    training_path = os.path.join(Config.data_dir, '训练数据-ccf_first_round_user_shop_behavior' + mail_id + '.csv')
    notmobilewifi_everymail = Tools.load_dict(
        Config.mail_notMobileWifi_txt_path
    )
    cur_mail_notmobilewifi = notmobilewifi_everymail[mail_id]
    wifi_dict = dict(zip(cur_mail_notmobilewifi, range(len(cur_mail_notmobilewifi))))
    training_features_show = features.generate_wifi_dict_feature(training_path, wifi_dict)
    wifi_strength_dict = prepare.Tools.load_dict(Config.wifi_strength_txt_path)
    training_features_strength = features.generate_wifi_strength(training_path, wifi_dict, wifi_strength_dict)
    training_labels, shop_ids = features.generate_label(
        csv_path=training_path,
        mail_shop_path=Config.mail_shop_txt_path,
        shop_mail_path=Config.shop_mail_txt_path
    )

    testing_features_show = features.generate_wifi_dict_feature(path, wifi_dict)
    testing_features_strength = features.generate_wifi_strength(path, wifi_dict, wifi_strength_dict)
    all_features_show = np.concatenate([training_features_show, testing_features_show])
    all_features_strength = np.concatenate([training_features_strength, testing_features_strength])
    all_features = np.concatenate(
        [do_pca_one_feature(all_features_show, n_components=n_components),
         do_pca_one_feature(all_features_strength, n_components=n_components)],
        axis=1
    )
    training_labels = np.array(training_labels)
    training_features = all_features[:len(training_labels)]
    testing_features = all_features[len(training_labels):]
    print 'after pca operation, the shape of feature is ', np.shape(all_features)
    return training_features, training_labels, testing_features, shop_ids

'''
    方法：用经纬度信息作为特征，假设一个商场有x个商铺，那么每一条记录都会有一个特征，代表的是消费地点与每个商铺的距离
    结果：？
'''
def extract_features_version4(path, mail_id):
    '''

    :param path: 测试文件的路径
    :param mail_id: 当前预测的mail的ID
    :param shop_mail_txt_path: shop_mail的dict关系
    :param is_training 代表path是训练的还是测试的
    :return: 训练集合的feature，label 测试集合的feature, 以及当前商场对应的shop 的ID（主要是用来写入csv文件）
    '''
    training_path = os.path.join(Config.data_dir, '训练数据-ccf_first_round_user_shop_behaviorm_' + mail_id + '.csv')
    training_features_distance = features.generate_longitude_latitude_feature(
        training_path,
        mail_shop_txt=Config.mail_shop_txt_path,
        is_training=True,
        mail_id='m_' + mail_id,
        shop_longitude_latitude_txt=Config.shop_longitude_latitude_txt_path
    )
    testing_features_distance = features.generate_longitude_latitude_feature(
        path,
        mail_shop_txt=Config.mail_shop_txt_path,
        is_training=False,
        mail_id=None,
        shop_longitude_latitude_txt=Config.shop_longitude_latitude_txt_path
    )
    training_labels, shop_ids = features.generate_label(
        csv_path=training_path,
        mail_shop_path=os.path.join(Config.data_dir, 'mail_shop.txt'),
        shop_mail_path=os.path.join(Config.data_dir, 'shop_mail.txt')
    )

    return training_features_distance, training_labels, testing_features_distance, shop_ids

def generate_predict(data_dir, re_name, output_path):
    predict_dir = data_dir
    paths = glob(os.path.join(predict_dir, re_name))
    lines_str = []
    for path_index, path in enumerate(paths):
        print path_index, ' ', path
        filename = os.path.basename(path)
        mail_id = 'm_' + filename[filename.rindex('_')+1: filename.find('.csv')]
        test_lines = prepare.read_csv(path)
        training_features, training_labels, testing_features, shop_ids = extract_features_version3(
            path,
            mail_id,
        )
        predict_res, acc = cross_validation.RunTest.do(
            training_features,
            training_labels,
            testing_features,
            cross_validation.myLinearSVC.do,
            'svm'
        )
        print predict_res
        for index, line in enumerate(test_lines[1:]):
            line_str = line[0] + ' ' + shop_ids[predict_res[index]]
            lines_str.append(line_str)
    write_lines = [line.split(' ') for line in lines_str]
    write_lines.insert(0, ['row_id', 'shop_id'])
    prepare.Tools.write_csv_file(output_path, write_lines)

if __name__ == '__main__':
    generate_predict(
        Config.data_dir,
        'AB榜测试集-evaluation_publicm_*.csv',
        './predict_version2.csv'
    )

