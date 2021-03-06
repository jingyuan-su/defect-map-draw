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
                    #scan_sampling, sampling_edge, defect_sampling = parser_klf(root, filename, logger)
                    #return scan_sampling, sampling_edge, defect_sampling
                    klarf_reading = parser_klf(root, filename, logger)
                    return klarf_reading,logger
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
        SetupID_str = find_klf_str_keyword_connect_result(klf_str, 'SetupID ', logger)[-3]
        # get tool info
        Tool_ID, Tool_model, Tool_Vendor = klf_tool_parser(klf_str, logger)

        if 'KLA' in Tool_ID:
            recipe_str = find_klf_str_keyword_connect_result(klf_str, 'SetupID', logger)[-3]
        else:
            recipe_str = SetupID_str + '_' + find_klf_str_keyword_connect_result(klf_str, 'StepID', logger)[-1]


        # get wafer no & image list
        Wafer_Tiff_dict = klf_waferid_and_img(klf_str, logger)
        # get notch direction
        Wafer_notch_direction = klf_batch_info_parser(klf_str, 'OrientationMarkLocation', logger)
        # get sampleCenterLocation
        Sample_center_location = klf_batch_info_parser(klf_str, 'SampleCenterLocation', logger)
        Die_pitch = klf_batch_info_parser(klf_str, 'DiePitch', logger)

        # return dataframe
        if 'SampleDieMap' in klf_str:
            key_str = 'SampleDieMap'
            Sample_plan_coordinate, sample_count = klf_sampling_coordinate_parser(klf_str, logger, key_str)
        elif 'SampleTestPlan' in klf_str:
            key_str = 'SampleTestPlan'
            Sample_plan_coordinate, sample_count, sample_edge = klf_sampling_coordinate_parser(klf_str, logger, key_str)
        else:
            Sample_plan_coordinate = None
            sample_count = None

        # return dict{}
        Defect_list_coordinate = klf_defect_coordinate_parser(klf_str, logger, Wafer_Tiff_dict.keys())

        # noinspection PyUnresolvedReferences
        # logger.info('FileTimestamp: %s' % FileTimestamp)
        # logger.info('LotID: %s' % LotID_str)
        # logger.info('Tool_ID: %s' % Tool_ID)
        # logger.info('Tool_model: %s' % Tool_model)
        # logger.info('Tool_Vendor: %s' % Tool_Vendor)
        # logger.info('Setupid: %s' % SetupID_str)
        # logger.info('Recipe: %s' % recipe_str)
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
        wafer_info['Setupid'] = SetupID_str
        wafer_info['Recipe'] = recipe_str
        wafer_info['Notch_direction'] = Wafer_notch_direction
        wafer_info['SampleCenter'] = Sample_center_location
        wafer_info['Diepitch_x'] = float(Die_pitch.strip().split(' ')[0])
        wafer_info['Diepitch_y'] = float(Die_pitch.strip().split(' ')[1])
        wafer_info['Sample_count'] = sample_count
        wafer_info['wafer_tiff'] = Wafer_Tiff_dict
        wafer_info['samplining_coordinate'] = Sample_plan_coordinate
        wafer_info['defect_coordinate'] = Defect_list_coordinate
        wafer_info['sample_edge'] = sample_edge
        
  
        #return wafer_info
        # return Defect_list_coordinate['25']
        # return Sample_plan_coordinate, sample_edge, Defect_list_coordinate['02']
        return wafer_info

    except Exception as e:
        logger.error(str(e))
        return None
    finally:
        pass

async def echo(websocket):
    mytest_path = os.path.join(os.path.expanduser('~'), 'Desktop\\defect-map-draw\\test file')
    # mysampling_coordinate ,mysamping_edge, mydefect_coordinate= detect_new_file(mytest_path)
    myklarf_result,logger = detect_new_file(mytest_path)
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

    # if (mysamping_edge is not None) and (mysampling_coordinate is not None) and (mydefect_coordinate is not None):    
    #     send_data = dict()
    #     sampling_coor_json = mysampling_coordinate.to_json(orient='records')
    #     defect_coor_json = mydefect_coordinate.to_json(orient='records')
    #     send_data['sampling_coor'] = sampling_coor_json
    #     send_data['sampling_edge'] = mysamping_edge
    #     send_data['defect_coor'] = defect_coor_json
        # await websocket.send(json.dumps(send_data))
    if(myklarf_result is not None):
        send_data = dict()
        sampling_coord_json = myklarf_result['samplining_coordinate'].to_json(orient='records')
        die_pitch_x = myklarf_result['Diepitch_x']
        die_pitch_y = myklarf_result['Diepitch_y']
        sample_edge = myklarf_result['sample_edge']

        send_data['sampling_coord'] = sampling_coord_json
        send_data['die_pitch_x'] = die_pitch_x
        send_data['die_pitch_y'] = die_pitch_y
        send_data['sampling_edge'] = sample_edge
        send_data['lotid'] = myklarf_result['lotid']
        send_data['Recipe'] = myklarf_result['Recipe']
        send_data['Tool_ID'] = myklarf_result['Tool_ID']

        for waferid,defect_coord in myklarf_result['defect_coordinate'].items():
            send_data['waferID'] = str(waferid)
            send_data['defect_coord'] = defect_coord.to_json(orient='records')
            # logger.info(waferid)
            # logger.info(defect_coord)
            await websocket.send(json.dumps(send_data))


async def main():
    async with websockets.serve(echo, 'localhost', 8765) as websocket:
        await asyncio.Future()



if __name__ == "__main__":
    #  mytest_path = os.path.join(os.path.expanduser('~'), 'Desktop\\test')
    #  detect_new_file(mytest_path)
    asyncio.run(main())
