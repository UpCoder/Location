# -*- coding=utf-8 -*-
from prepare import *
from Config import Config
def split_testdataset_byusershown(train_csv_path, val_csv_path, save_csv_paths):
    '''
        将val数据将所有记录分成user之前出现过和没有出现过
        :param train_csv_path 训练的记录
        :param val_csv_path 测试的记录
        :param save_csv_paths 保存的新文件的路径，第一个是出现过的，第二个是没有出现过的
    '''
    train_users = Statics.statics_user_shown(train_csv_path, True)
    val_lines = read_csv(val_csv_path)
    shown_lines = []
    not_shown_lines = []
    shown_lines.append(val_lines[0])
    not_shown_lines.append(val_lines[0])
    for val_line in val_lines[1:]:
        user_id = val_line[1]
        if user_id in train_users:
            shown_lines.append(val_line)
        else:
            not_shown_lines.append(val_line)
    print 'the number of shown user line is %d' % len(shown_lines)
    print 'the number of not shown user line is %d' % len(not_shown_lines)
    print save_csv_paths[0]
    print save_csv_paths[1]
    Tools.write_csv_file(save_csv_paths[0], shown_lines)
    Tools.write_csv_file(save_csv_paths[1], not_shown_lines)

if __name__ == '__main__':
    split_testdataset_byusershown(
        Config.train_user_data_path,
        Config.val_user_data_path,
        [
            os.path.join(Config.data_dir, 'AB榜测试集-evaluation_public_shown.csv'),
            os.path.join(Config.data_dir, 'AB榜测试集-evaluation_public_not_shown.csv')
        ]
    )