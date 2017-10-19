# -*- coding=utf-8 -*-
import Ipynb_importer
import features
import prepare
import os
import numpy as np
from glob import glob
import cross_validation
def generate_predict(data_dir, re_name, output_path):
    predict_dir = data_dir
    paths = glob(os.path.join(predict_dir, re_name))
    lines_str = []
    for path_index, path in enumerate(paths):
        print path_index, ' ', path
        filename = os.path.basename(path)
        mail_id = filename[filename.rindex('_')+1: filename.find('.csv')]
        training_path = os.path.join(prepare.data_dir, '训练数据-ccf_first_round_user_shop_behaviorm_'+mail_id+'.csv')
        test_lines = prepare.read_csv(path)
        wifi_dict = features.generate_wifi_dictionary(
            [training_path, path]
        )
        print 'the number of wifi source is ', len(wifi_dict)
        training_features = features.generate_wifi_dict_feature(training_path, wifi_dict)
        training_labels, shop_ids = features.generate_label(
            csv_path=training_path,
            mail_shop_path=os.path.join(prepare.data_dir, 'mail_shop.txt'),
            shop_mail_path=os.path.join(prepare.data_dir, 'shop_mail.txt')
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
        prepare.data_dir,
        'AB榜测试集-evaluation_publicm_*.csv',
        './predict.csv'
    )

