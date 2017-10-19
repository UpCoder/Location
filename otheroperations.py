# -*- coding=utf-8 -*-
import os
import shutil
def rename():
    path = '/home/give/PycharmProjects/Location/data'
    save_path = '/home/give/PycharmProjects/Location/data/data'
    names = os.listdir(path)
    paths = [os.path.join(path, name) for name in names]
    for cur_path in paths:
        base_name = os.path.basename(cur_path)
        if base_name.find('publicm') != -1:
            mail_id = base_name[base_name.rindex('_') + 1: base_name.find('.csv')]
            target_path = os.path.join(save_path, 'AB榜测试集-evaluation_publicm_' + mail_id + '.csv')
            shutil.copy(
                cur_path,
                target_path
            )
        if base_name.find('user_shop_behaviorm') != -1:
            mail_id = base_name[base_name.rindex('_') + 1: base_name.find('.csv')]
            target_path = os.path.join(save_path, '训练数据-ccf_first_round_user_shop_behaviorm_' + mail_id + '.csv')
            shutil.copy(
                cur_path,
                target_path
            )
def check_repeat():
    from prepare import read_csv
    lines = read_csv('/home/give/PycharmProjects/Location/predict.csv')
    my_dict = {}
    for index, line in enumerate(lines[1:]):
        if index % 1000 == 0:
            print int(index / 1000)
        my_dict[line[0]] = index
    values = list(my_dict.values())
    values.sort()
    for index, value in enumerate(values):
        if index != value:
            print 'Error'
if __name__ == '__main__':
    check_repeat()