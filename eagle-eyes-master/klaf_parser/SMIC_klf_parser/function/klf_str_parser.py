# -*- coding: UTF-8 -*-
"""
The toolkits
Author:
    jingyuan_su@2021-11-06

"""
import pandas as pd
import time


def find_klf_str_keyword_connect_result(klf_str, keyword, logging):
    """
    split keyowrds from klarf'string

    Args:
        klf_str(string):Should be server loader which was klarf file received from tool FAB insided
        keyword(string):keywords in klarf file
        logging(lagging):Logger
    Returns:
        list:parameters from klarfs
    """
    try:
        klf_str_lower = klf_str.lower()
        keyword_startindex = klf_str_lower.find(keyword.lower())
        keyword_endindex = klf_str_lower.find(';\n', keyword_startindex)
        return klf_str[keyword_startindex + len(keyword):keyword_endindex].replace('"', '').split(' ')
    except Exception as e:
        logging.error(str(e))


def recipe_wildcard_decoder(set_recipe_str, klf_recipe_str):
    """
    wildcard hanlding

    Args:
        set_recipe_str(string):parameters's(recipe set) information including wildchard
        klf_recipe_str(string): recipe info
    Returns:
        bool: do judge
    """

    wildcard_idx = set_recipe_str.find("?")
    if wildcard_idx != -1:
        if klf_recipe_str.replace(klf_recipe_str[wildcard_idx], "") == set_recipe_str.replace("?", ""):
            return True
        else:
            return False
    else:
        return False


def extract_lot(LotID_str):
    """
    extrace lotid from lotid-waferid's format

    Args:
        LotID_str(string):lot_id or lot_id-wafer id string
    Returns:
        string:only lotid string
    """

    if '-' in LotID_str:
        ending = '-' + LotID_str.split('-')[-1]
        return LotID_str[:-len(ending)]
    else:
        return LotID_str


def klf_batch_info_parser(klf_str, info_str, logging):
    """
    extrace other common same formatter information

    Args:
        klf_str(string):klarf string
        info_str(string): specify info from klarf's parameters
        logging(Logging):logger

    Returns:
        list:info list
    """

    try:
        info_start = klf_str.find(info_str, 0) + len(info_str)
        info_end = klf_str.find(';\n', info_start)
        info_result = klf_str[info_start:info_end].replace('"', '')
        return info_result

    except Exception as e:
        logging.error(str(e))


def klf_timestamp_parser(klf_str, logging):
    """
    extrace scan timestamp

    Args:
        klf_str(string):klarf string
        logging(Logging):logger

    Returns:
        string:scan time stamp
    """

    try:
        fileTimestampArr = find_klf_str_keyword_connect_result(klf_str, 'FileTimestamp', logging)
        fileTimestampFormat = '%m-%d-%Y%H:%M:%S' if len(fileTimestampArr) > 8 else "%m-%d-%y%H:%M:%S"
        FileTimestamp = time.strftime("%Y-%m-%d %H:%M:%S",
                                      time.strptime(fileTimestampArr[1] + fileTimestampArr[2], fileTimestampFormat))
        return FileTimestamp

    except Exception as e:
        logging.error(str(e))


def klf_tool_parser(klf_str, logging):
    """
    extrace tool information including tool's vendor,toolid,tool model

    Args:
        klf_str(string):klarf string
        logging(Logging):logger

    Returns:
        string:info list
    """

    try:
        klf_row = klf_str.split('\n')
        for row_name in klf_row:
            first_row_name = row_name.split(' ')[0]
            if first_row_name == 'InspectionStationID':
                tool_id = row_name.split('"')[-2]
                tool_model = row_name.split('"')[-4]
                tool_vendor = row_name.split('"')[-6]
                return tool_id, tool_model, tool_vendor

    except Exception as e:
        logging.error(str(e))


def klf_defect_coordinate_parser(klf_str, logging, waferID_list):
    """
    defect 's coordinate

    Args:
        klf_str(string):klarf string
        logging(Logging):logger
        waferID_list(list): parse from klarf'wafer id list
    Returns:
        dict:each wafer id's defect coordinate
    """

    global coordinator_content_result
    try:
        # checkout columns count,从机台端出来的不同的klarf 列数不一样
        # 将defect坐标放在dataframe里方便后续操作
        col_info_start = klf_str.find('DefectRecordSpec', 0) + len('DefectRecordSpec')
        col_info_end = klf_str.find(';', col_info_start)
        col_info = klf_str[col_info_start:col_info_end].strip().split(' ')[1:]
        mydefect_coor_dic = {}

        # AIT是多个wafer defect坐标在一份klarf里
        if len(waferID_list) == klf_str.count('DefectList'):

            # for i in range(klf_str.count('DefectList')):
            for mywaferid in waferID_list:
                # coordinator content
                coordinator_content_start = klf_str.find('DefectList', 0) + len('DefectList')
                coordinator_content_end = klf_str.find(';', coordinator_content_start)
                coordinator_content = klf_str[coordinator_content_start:coordinator_content_end].strip().split('\n')
                coordinator_content_result = [[x for x in ss.strip().split(' ')] for ss in coordinator_content]
                # myarray = np.array(coordinator_content_result[:-1])
                mydataframe_defect = pd.DataFrame(coordinator_content_result, columns=col_info)
                # mydataframe_defect.set_index('DEFECTID', replace=False)
                mydefect_coor_dic[mywaferid] = mydataframe_defect
                # mydefect_coor_dic['def_xl'] = mydataframe_defect.loc[['x']].max()
        return mydefect_coor_dic

    except Exception as e:
        logging.error(str(e))


def klf_sampling_coordinate_parser(klf_str, logging, key_str):
    """
    scan sample 's coordinate

    Args:
        klf_str(string):klarf string
        logging(Logging):logger
        key_str(string): SampleCenterLocation
    Returns:
        dataframe:scan sample's coordinate.
        string:scan sample's count
    """

    try:
        col_info_start = klf_str.find(key_str, 0) + len(key_str)
        col_info_end = klf_str.find(';', col_info_start)
        coordinator_edge = dict()

        # sampling content
        coordinator_content = klf_str[col_info_start:col_info_end].strip().split('\n')
        sample_count = coordinator_content.pop(0)
        coordinator_content_result = [[x for x in ss.strip().split(' ') if len(x) > 0] for ss in coordinator_content]
        mydataframe_sampling = pd.DataFrame(coordinator_content_result, columns=['x', 'y']).astype(int)
        # mydataframe_sampling.loc[:,'x'] = mydataframe_sampling['x'].str.astype('int32')
        # mydataframe_sampling.loc[:'y'] = mydataframe_sampling['y'].str.astype('int32')
        def_xl = mydataframe_sampling['x'].min()
        def_xr = mydataframe_sampling['x'].max()
        def_yu = mydataframe_sampling['y'].min()
        def_yl = mydataframe_sampling['y'].max()

        coordinator_edge['def_xl'] = def_xl
        coordinator_edge['def_xr'] = def_xr
        coordinator_edge['def_yu'] = def_yu
        coordinator_edge['def_yl'] = def_yl

        return mydataframe_sampling, sample_count, coordinator_edge

    except Exception as e:
        logging.error(str(e))


def klf_waferid_and_img(klf_str, logging):
    """
    wafer id and image name
    including Fir80 OQI klarf auto take image's fuinction
    including AIT multi-wafer info with one whole klarf

    Args:
        klf_str(string):klarf string
        logging(Logging):logger
    Returns:
        dict: wafer id and Tiff name
    """

    try:
        Wafer_index = 0
        Wafer_Tiff_dict = dict()
        while klf_str.find('WaferID ', Wafer_index) > 0:
            Wafer_index_start = klf_str.find('WaferID ', Wafer_index) + len('WaferID ')
            Wafer_index_end = klf_str.find(';\n', Wafer_index_start)
            Wafer_str = klf_str[Wafer_index_start:Wafer_index_end].replace('"', '')
            Wafer_Tiff_dict[Wafer_str] = []
            Wafer_index = Wafer_index_end
            TiffFile_start_index = Wafer_index
            temp_index = klf_str.find('WaferID ', Wafer_index)
            find_tiff_str = klf_str[TiffFile_start_index:temp_index]

            TiffFile_index = 0
            while find_tiff_str.find('TiffFileName ', TiffFile_index) > 0:
                TiffFile_index_start = find_tiff_str.find('TiffFileName ', TiffFile_index) + len('TiffFileName ')
                TiffFile_index_end = find_tiff_str.find(';\n', TiffFile_index_start)
                TiffFile_str = find_tiff_str[TiffFile_index_start:TiffFile_index_end]
                TiffFile_str = TiffFile_str.strip('"')
                if '\\' in TiffFile_str:
                    TiffFile_str = TiffFile_str.split('\\')[-1]
                TiffFile_index = TiffFile_index_end
                Wafer_Tiff_dict[Wafer_str].append(TiffFile_str)

        return Wafer_Tiff_dict
    except Exception as e:
        logging.error(str(e))
