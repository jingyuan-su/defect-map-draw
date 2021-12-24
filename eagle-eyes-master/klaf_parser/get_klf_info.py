# -*- coding: UTF-8 -*-
"""
The main klarf handling
Author:
    jingyuan_su@2021-10-28

"""
import os
import logging
from SMIC_klf_parser.function.klf_str_parser import *
import json
import asyncio
import websockets

# noinspection PyTypeChecker
def detect_new_file(src_path):
    """
    While true to detect new klarf file in always.
    filter out klarf files from server's loader base on file's postfix

    Args:
        src_path(string):Should be server loader which was klarf file received from tool FAB insided
    Returns:
        logger:loader's path,klarf file,logger
    """
    # %（acstime)s 时间
    # %（filename)s 日志文件名
    # %（funcName)s 调用日志的函数名
    # %（levelname)s 日志的级别
    # %（module)s 调用日志的模块名
    # %（message)s 日志信息
    # %（name)s logger的name，不写的话默认是root

    logger = logging.getLogger("jingyuan")
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s-%(levelname)s-%(funcName)s-%(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    try:
        for root, dirs, files in os.walk(src_path):
            for filename in files:
                file_ext = os.path.splitext(filename)[-1]
                if file_ext.lower() not in ['.jpg', '.jpeg', '.tiff', '.png', '.tif']:
                    dir_name = os.path.split(os.path.split(root)[0])[-1]
                    logger.info("found klarf: " + filename)
                    logger.info('...in ' + dir_name)
                    scan_sampling, sampling_edge, defect_sampling = parser_klf(root, filename, logger)
                    return scan_sampling, sampling_edge, defect_sampling
    except Exception as e:
        logger.error(str(e))
        return None


def parser_klf(src_path, filename, logger):
    """
    Resolving info from klarf files through logger

    Args:
        src_path(string):Should be server loader which was klarf file received from tool FAB insided.
        filename(string): klarf file name.
        logger(string):output
    Returns:
       logger:all of klarf's information should output with logger,including defect coordinate
    """
    wafer_info = {}
    try:
        with open(os.path.join(src_path, filename), 'r') as klf_file:
            klf_str = klf_file.read()

        FileTimestamp = klf_timestamp_parser(klf_str, logger)
        LotID_str = find_klf_str_keyword_connect_result(klf_str, 'LotID', logger)[-1]

        if 'DeviceID' in klf_str:
            DeviceID_str = find_klf_str_keyword_connect_result(klf_str, 'DeviceID', logger)[-1]
        else:
            DeviceID_str = None

        SetupID_str = find_klf_str_keyword_connect_result(klf_str, 'SetupID ', logger)[-3]
        # get tool info
        Tool_ID, Tool_model, Tool_Vendor = klf_tool_parser(klf_str, logger)
        # get wafer no & image list
        Wafer_Tiff_dict = klf_waferid_and_img(klf_str, logger)
        # get notch direction
        Wafer_notch_direction = klf_batch_info_parser(klf_str, 'OrientationMarkLocation', logger)
        # get sampleCenterLocation
        Sample_center_location = klf_batch_info_parser(klf_str, 'SampleCenterLocation', logger)
        Die_pitch = klf_batch_info_parser(klf_str, 'DiePitch', logger)

        if 'SampleDieMap' in klf_str:
            key_str = 'SampleDieMap'
            Sample_plan_coordinate, sample_count = klf_sampling_coordinate_parser(klf_str, logger, key_str)
        elif 'SampleTestPlan' in klf_str:
            key_str = 'SampleTestPlan'
            Sample_plan_coordinate, sample_count, sample_edge = klf_sampling_coordinate_parser(klf_str, logger, key_str)
        else:
            Sample_plan_coordinate = None
            sample_count = None

        Defect_list_coordinate = klf_defect_coordinate_parser(klf_str, logger, Wafer_Tiff_dict.keys())

        # noinspection PyUnresolvedReferences
        # logger.info('FileTimestamp: %s' % FileTimestamp)
        # logger.info('LotID: %s' % LotID_str)
        # logger.info('Tool_ID: %s' % Tool_ID)
        # logger.info('Tool_model: %s' % Tool_model)
        # logger.info('Tool_Vendor: %s' % Tool_Vendor)
        # logger.info('DeviceID: %s' % DeviceID_str)
        # logger.info('Setupid: %s' % SetupID_str)
        # logger.info('Notch direction: %s' % Wafer_notch_direction)
        # logger.info('SampleCenterLocation: %s' % Sample_center_location)
        # logger.info('DiePitch: %s' % Die_pitch)
        # logger.info('scan sampling die count: %s' % sample_count)
        # logger.info('SamplinTestPlan: %s' % Sample_plan_coordinate)
        # logger.info('Wafer_Tiff: %s' % Wafer_Tiff_dict)
        # logger.info('defect coordinate: %s' % Defect_list_coordinate)

        wafer_info['lotid'] = LotID_str
        wafer_info['Tool_ID'] = Tool_ID
        wafer_info['Tool_model'] = Tool_model
        wafer_info['Tool_vendor'] = Tool_Vendor
        wafer_info['DeviceID'] = DeviceID_str
        wafer_info['Setupid'] = SetupID_str
        wafer_info['Notch_direction'] = Wafer_notch_direction
        wafer_info['SampleCenter'] = Sample_center_location
        wafer_info['Diepitch'] = Die_pitch
        wafer_info['Sample_count'] = sample_count
        wafer_info['wafer_tiff'] = Wafer_Tiff_dict
        wafer_info['samplining_coordinate'] = Sample_plan_coordinate
        wafer_info['defect_coordinate'] = Defect_list_coordinate

        #return wafer_info
        # return Defect_list_coordinate['25']
        return Sample_plan_coordinate, sample_edge, Defect_list_coordinate

    except Exception as e:
        logger.error(str(e))
        return None
    finally:
        pass

async def echo(websocket):
    mytest_path = os.path.join(os.path.expanduser('~'), 'Desktop\\code and test file\\test')
    mysampling_coordinate ,mysamping_edge, defect_coordinate= detect_new_file(mytest_path)
    # print (myresult.to_json(orient = 'index'))
    # dataframe to other format 
    # df = pd.DataFrame([['a', 'b'], ['c', 'd']],
    #   index=['row 1', 'row 2'],
    #   columns=['col 1', 'col 2'])
    # ###########
    # split
    # ###########
    # df.to_json(orient='split')
    # >'{"columns":["col 1","col 2"],
    #  "index":["row 1","row 2"],
    #  "data":[["a","b"],["c","d"]]}'
    # ###########
    # index
    # ###########
    # df.to_json(orient='index')
    # >'{"row 1":{"col 1":"a","col 2":"b"},"row 2":{"col 1":"c","col 2":"d"}}'
    # ###########
    # records
    # ###########
    # df.to_json(orient='records')
    # >'[{"col 1":"a","col 2":"b"},{"col 1":"c","col 2":"d"}]'
    # ###########
    # table
    # ###########
    # df.to_json(orient='table')
    # >'{"schema": {"fields": [{"name": "index", "type": "string"},
    #   {"name": "col 1", "type": "string"},    
    #   {"name": "col 2", "type": "string"}],
    #  "primaryKey": "index",
    #  "pandas_version": "0.20.0"},
    #  "data": [{"index": "row 1", "col 1": "a", "col 2": "b"},
    #  {"index": "row 2", "col 1": "c", "col 2": "d"}]}'

    if (mysamping_edge is not None) and (mysampling_coordinate is not None) and (defect_coordinate is not None):    
        send_data = dict()
        sampling_coor_json = mysampling_coordinate.to_json(orient='records')
        defect_coordinate = 
        send_data['sampling_coor'] = sampling_coor_json
        send_data['sampling_edge'] = mysamping_edge
        
        await websocket.send(json.dumps(send_data))
        # await websocket.send(json.dumps(mysamping_edge))

async def main():
    async with websockets.serve(echo, 'localhost', 8766) as websocket:
        await asyncio.Future()



if __name__ == "__main__":
    #  mytest_path = os.path.join(os.path.expanduser('~'), 'Desktop\\test')
    #  detect_new_file(mytest_path)
    asyncio.run(main())
