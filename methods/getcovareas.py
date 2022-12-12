import hashlib
import os
import requests
import time
import sys
import json
import csv


# 显示某等级地区的小计
def show_level_count(x_list):
    j = 0
    for i in range(len(x_list)):
        j += len(x_list[i]["communitys"])
    print(j)
    return j


def writer_to_csv(risk_txt):
    risk_json = json.loads(risk_txt)

    so_far_time = risk_json["data"]["end_update_time"]

    highlist = risk_json["data"]["highlist"]
    middlelist = risk_json["data"]["middlelist"]
    lowlist = risk_json["data"]["lowlist"]

    encoding = "utf_8_sig"
    f = open("risk_data_" + so_far_time + ".csv", "w", encoding=encoding, newline="")
    csv_writer = csv.writer(f)

    level_dict = {}
    level_dict["高风险"] = highlist
    level_dict["中风险"] = middlelist
    level_dict["低风险"] = lowlist

    for level in level_dict.keys():
        risk_level = level
        for i in range(len(level_dict[level])):
            province = level_dict[level][i]["province"]
            city = level_dict[level][i]["city"]
            county = level_dict[level][i]["county"]
            for j in range(len(level_dict[level][i]["communitys"])):
                csv_writer.writerow(
                    [
                        risk_level,
                        province,
                        city,
                        county,
                        level_dict[level][i]["communitys"][j],
                    ]
                )
    # write_to_csv_file(csv_writer, highlist, "高风险")
    # write_to_csv_file(csv_writer, middlelist, "中风险")
    # write_to_csv_file(csv_writer, lowlist, "低风险")
    f.close()

    print("写入risk_data.csv完成.")


def get_risk_area_data():
    timestamp = str(int(time.time()))
    # timestamp = '1662646358'

    x_wif_timestamp = timestamp
    timestampHeader = timestamp

    x_wif_nonce = "QkjjtiLM2dCratiA"
    x_wif_paasid = "smt-application"

    x_wif_signature_str = (
        timestamp + "fTN2pfuisxTavbTuYVSsNJHetwq5bJvCQkjjtiLM2dCratiA" + timestamp
    )
    x_wif_signature = (
        hashlib.sha256(x_wif_signature_str.encode("utf-8")).hexdigest().upper()
    )

    signatureHeader_str = (
        timestamp + "23y0ufFl5YxIyGrI8hWRUZmKkvtSjLQA" + "123456789abcdefg" + timestamp
    )
    signatureHeader = (
        hashlib.sha256(signatureHeader_str.encode("utf-8")).hexdigest().upper()
    )

    url = "http://bmfw.www.gov.cn/bjww/interface/interfaceJson"

    headerss = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json;charset=utf-8",
        "x-wif-nonce": "QkjjtiLM2dCratiA",
        "x-wif-paasid": "smt-application",
        "x-wif-signature": x_wif_signature,
        "x-wif-timestamp": x_wif_timestamp,
    }

    From_data = (
        '{"key":"3C502C97ABDA40D0A60FBEE50FAAD1DA",\
    "appId":"NcApplication","paasHeader":"zdww",\
    "timestampHeader":"'
        + timestampHeader
        + '",\
    "nonceHeader":"123456789abcdefg","signatureHeader":"'
        + signatureHeader
        + '"}'
    )
    # print(From_data)

    response = requests.post(url=url, data=From_data, headers=headerss)
    if not response.status_code == 200:
        # print(response.status_code)
        return "", response.status_code
    response.encoding = "utf-8"

    # print(response.text)
    return json.loads(response.text.replace("\u2022", "")), response.status_code


# if __name__ == "__main__":
#     risk_data = get_risk_area_data()
#     from pprint import pprint
#     print(risk_data)
