# -*- coding=utf-8 -*-

from prepare import *
'''
    构建Wi-Fi词典
    :params csv_paths 文件的路径数组，根据多个文件构建wifi字典，默认wifi字段总是在csv的最后一列
'''
def generate_wifi_dictionary(csv_paths):
    wifi_list = []
    for csv_path in csv_paths:
        lines = read_csv(csv_path)
        for line in lines[1:]:
            record_obj = record(','.join(line))
            wifi_list.extend([wifi_obj.id for wifi_obj in record_obj.wifis.wifi_arr])
    wifi_list = list(set(wifi_list))
    wifi_dict = dict(zip(wifi_list, range(len(wifi_list))))
    return wifi_dict

'''
    根据Wi-Fi字典构建特征向量
    依据Wi-Fi出现次数作为特征
'''
def generate_wifi_dict_feature(csv_path, wifi_dict):
    lines = read_csv(csv_path)
    features = np.zeros([len(lines)-1, len(wifi_dict)], np.uint8)
    for index, line in enumerate(lines[1:]):
        record_obj = record(','.join(line))
        for wifi_obj in record_obj.wifis.wifi_arr:
            if wifi_obj.id not in wifi_dict.keys():
                # 属于移动Wi-Fi
                continue
            features[index, wifi_dict[wifi_obj.id]] += 1
    return features
'''
    根据Wi-Fi字典构建特征向量
    依据特征向量，依句Wi-Fi出现的强度作为特征
'''
def generate_wifi_strength(csv_path, wifi_dict, wifi_strength_dict):
    print 'will be finish'
    lines = read_csv(csv_path)
    features = np.zeros([len(lines) - 1, len(wifi_dict)], np.float32)
    for index, line in enumerate(lines[1:]):
        record_obj = record(','.join(line))
        for wifi_obj in record_obj.wifis.wifi_arr:
            wifi_id = wifi_obj.id
            if wifi_id not in wifi_dict.keys():
                # 移动Wi-Fi
                continue
            wifi_index = wifi_dict[wifi_id]
            # 这里选取Wi-Fi信号的最大值的时候，可以考虑选择top25 的平均值
            max_wifi_strength = wifi_strength_dict[wifi_id][-1]
            # wifi_strength_arr = np.array(wifi_strength_dict[wifi_id])
            # max_wifi_strength = np.mean(wifi_strength_arr[int(0.75 * len(wifi_strength_arr)):])
            features[index][wifi_index] += (1.0 * wifi_obj.singal) / max_wifi_strength
    return features

'''
    根据csv文件构建label，不同的label是不同的商铺
'''
def generate_label(csv_path, mail_shop_path, shop_mail_path):
    lines = read_csv(csv_path)
    mail_shop_dict = Tools.load_dict(mail_shop_path)
    shop_mail_dict = Tools.load_dict(shop_mail_path)
    labels = []
    mail_id = shop_mail_dict[lines[1][1]]
    shops = mail_shop_dict[mail_id]
    for line in lines[1:]:
        labels.append(
            shops.index(line[1])
        )
    return labels, shops

'''
    计算经纬度特征
    我们知道商场中每个商铺的经纬度，对于商场中的每一条消费记录我们也计算消费者位置和每个商铺的距离作为特征
'''
def generate_longitude_latitude_feature(mail_csv_path, mail_shop_txt, shop_longitude_latitude_txt, is_training, mail_id):
    '''
    :param mail_csv_path: 商场的消费记录
    :param mail_shop_txt: 商场和店铺的关系，因为我们需要知道该商场一共有哪些店铺
    :param shop_longitude_latitude_txt: 店铺的经纬度信息dict存储的路径
    :param is_training: 传进来的商场的消费记录是训练集合的还是测试集合的， 如果是测试集合的直接根据他的mail_id字段就可以获取mail_id, 如果是训练的，则需要将该值传递进来
    :param mail_id: None 代表的是测试机，可以用数据中获取，否则是训练集合
    :return:
    '''
    mail_shop_dict = Tools.load_dict(mail_shop_txt)
    shop_longitude_latitude_dict = Tools.load_dict(shop_longitude_latitude_txt)
    records_obj = records(mail_csv_path, is_training)
    features = []
    for record_obj in records_obj.records:
        feature = []
        if mail_id is None:
            mail_id = record_obj.mail_id
        shop_ids = mail_shop_dict[mail_id]
        for shop_id in shop_ids:
            shop_info = shop_longitude_latitude_dict[shop_id]
            distance = Tools.haversine(shop_info[0], shop_info[1], float(record_obj.longitude), float(record_obj.latitude))
            feature.append(distance)
        features.append(Tools.MaxMinNormalization(feature, np.max(feature), np.min(feature)))
    return features

'''
    使用PCA方法进行降维
'''
def do_pca(features, n_components=100):
    from sklearn import decomposition

    pca = decomposition.PCA(n_components=n_components, copy=True)

    features_pca = pca.fit_transform(features)
    return features_pca