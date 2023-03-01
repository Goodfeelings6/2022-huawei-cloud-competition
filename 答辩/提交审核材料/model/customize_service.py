# !/usr/bin/python
# -*- coding: UTF-8 -*-


from __future__ import absolute_import

from __future__ import division

from __future__ import print_function

import json
from model_service.pytorch_model_service import PTServingBaseService
from baseline_algorithm import base_algorithm


class CrossDomainService(PTServingBaseService):
    def __init__(self, model_name, model_path):
        # 初始化pytorch模型，用于符合华为云平台调用程序的格式要求。实际并未使用该AI模型。
        self.model_name = model_name
        self.model_path = model_path

    def _preprocess(self, data):

        """
        `data` is provided by Upredict service according to the input data. Which is like:
          {
              'lane': {
                'video01.potion.txt': b'xxx'
              }
          }
        For now, predict a single file at a time.
        """
        # 数据预处理，data为json格式，filename为轨迹文件文件名，file_content为二进制格式的轨迹数据
        preprocessed_data = {}
        for file_name, file_content in data["lane"].items():
            car_record = []
            lines = file_content.read().decode()
            lines = lines.split('\n')
            for line in lines:
                if len(line) > 1:
                    car_record.append(json.loads(line))
            preprocessed_data[file_name] = car_record
        # 经过以上处理，preprocessed_data的key为filename，value为List[dict]格式，每一个元素是一帧数据，与轨迹文件txt中一致
        # return作为_inference中的data
        return preprocessed_data

    def _inference(self, data):
        result = base_algorithm(data=data)
        print(result)
        # return作为_postprocess中的data
        return result

    def _postprocess(self, data):

        """
        `data` is the result of your model. Which is like:
          {
            'video01': {'left':10,'straight':10,'right':10,'1':10,'2':10,'3':10}
          }
        """
        # return返回给平台，符合格式要求
        return data
