import datetime
from time import time
import os
from notify import send
import urllib3
import requests
from datetime import datetime
from calendar import monthrange
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

#京东签到
def signBeanAct():
    pt_key = os.getenv("PT_KEY", "")
    pt_pin = os.getenv("PT_PIN", "")
    if not all([pt_pin, pt_key]):
        send("京东签到", f'请添加变量PT_KEY及PT_PIN')
    meta = {
        "method": "POST",
        "url": "https://api.m.jd.com/client.action",
        "params": {
            "functionId": "signBeanAct",
            # "body": '{"fp":"-1","shshshfp":"-1","shshshfpa":"-1","referUrl":"-1","userAgent":"-1","jda":"-1","rnVersion":"3.9"}',
            "appid": "ld",
            "client": "apple",
            # "clientVersion": "10.0.4",
            # "networkType": "wifi",
            # "osVersion": "14.8.1",
            # "uuid": "",
            # "openudid": "",
        },
        "cookies": {
            "pt_key": pt_key,
            "pt_pin": pt_pin
        }
    }
    res = req(**meta)

    if res.status_code == 200:
        try:
            res = res.json()
            if res.get("errorMessage"):
                raise Exception("")
            else:
                if res["data"]["status"] == '1':
                    send("京东签到", f"用户{pt_pin}签到成功")
                else:
                    send("京东签到", f"用户{pt_pin}已签到")
        except Exception as e:
            send("京东签到", f"用户{pt_pin} 京豆签到程序异常 {res}")

        # 京东快递
        meta.update(
            {
                "url": "https://lop-proxy.jd.com/jiFenApi/signInQuery",
                "params": {},
                "json": [{"userNo": "$cooMrdGatewayUid$"}],
                "headers": {
                    "AppParams": '{"appid":158,"ticket_type":"m"}',
                    "uuid": "%.f" % (time() * 10 ** 13),
                    "LOP-DN": "jingcai.jd.com"
                }
            }
        )
        res2 = req(**meta)
        res2 = res2.json()
        try:
            if res2['errorMsg'] == 'SUCCESS':
                send("京东快递签到", f"用户{pt_pin}签到成功")
            else:
                send("京东快递签到", f"用户{pt_pin} 签到异常 {res2}")
        except:
            send("京东快递签到", f"用户{pt_pin} 签到异常 {res2}")
    else:
        send("京东签到", f'pt_key: {pt_key}; pt_pin: {pt_pin} 已失效，请重新获取PT_KEY和PT_PIN')

#南航签到
def csairSign(**kwargs):
    result = []

    token = os.getenv("CSAIR_TOKEN", "")
    if not token:
        send("南航签到",f'错误,请输入sign_user_token')
        return
    # 签到
    createTime = int(time() * 1000)
    meta = {
        "method": "POST",
        "url": "https://wxapi.csair.com/marketing-tools/activity/join",
        "params": {
            "type": "APPTYPE",
            "chanel": "ss",
            "lang": "zh"
        },
        "json": {
            "activityType": "sign",
            "channel": "app",
            "entrance": None
        },
        "headers": {"Content-Type": "application/json"},
        "cookies": {
            "sign_user_token": token,
            "TOKEN": token,
            "cs1246643sso": token,
        }
    }
    res = req(**meta)
    if res.status_code == 200:
        try:
            info = res.json()
            if info.get("respCode") == "S00011":
                result.append(f'南航用户：{token} 请检查token是否有效')
            if info.get("respCode") == "S2001":
                result.append(f'南航用户：{token} 今天已签到！')
            else:
                result.append(f'{token} {info.get("respMsg", "")}')
            # 奖励列表
            meta.update({
                "url": "https://wxapi.csair.com/marketing-tools/award/awardList",
                "json": {"activityType": "sign", "awardStatus": "waitReceive", "pageNum": 1, "pageSize": 100},
            })
            res = req(**meta)
            if res.status_code == 200:
                for d in res.json()["data"]["list"]:
                    meta.update({
                        "url": "https://wxapi.csair.com/marketing-tools/award/getAward",
                        "json": {"activityType": "sign", "signUserRewardId": d["id"]},
                    })
                    res = req(**meta)
                    if res.status_code == 200:
                        print(res.json()["data"]["result"])
        except Exception as e:
            print(f'南航签到程序异常 {e}')
    # 签到日历
    month_start = datetime(datetime.now().year, datetime.now().month, 1).strftime("%Y%m%d")
    month_end = datetime(datetime.now().year, datetime.now().month,
                         monthrange(datetime.now().year, datetime.now().month)[1]).strftime("%Y%m%d")
    meta = {
        "url": "https://wxapi.csair.com/marketing-tools/sign/getSignCalendar",
        "params": {
            "type": "APPTYPE",
            "chanel": "ss",
            "lang": "zh",
            "startQueryDate": month_start,
            "endQueryDate": month_end
        },
        "cookies": {"sign_user_token": token}
    }
    res = req(**meta)
    if res:
        try:
            info = res.json()
            if info.get("respCode") == "0000":
                result.append(f'南航用户：{token} 当月 {info["data"]["dateList"]} 已签到')
            else:
                result.append(f'{token} {info.get("respMsg", "")}')
        except Exception as e:
            result.append(f"南航签到程序异常 {e.with_traceback()}")

    send("南航签到","\n".join(result))


def m10086(**kwargs):
    result = []
    token = kwargs.get("token", "")
    if not token:
        send("10086签到",f'请输入SESSION_TOKEN')
    # 公众号签到
    meta = {
        "url": "https://wx.10086.cn/qwhdhub/api/mark/do/mark",
        "headers": {
            "x-requested-with": "XMLHttpRequest",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.42(0x18002a2a) NetType/4G Language/zh_CN",
            "login-check": "1",
            "Cookie": f"SESSION_TOKEN={token}",
        }
    }
    res = requests.request("GET", **meta)
    try:
        if res:
            result.append(f'公众号签到 {res.text}')
            res = res.json()
            result.append(f'10086_{token} {res.get("msg", "")}')

            # app签到
            meta.update({
                "method": "POST",
                "url": "https://wx.10086.cn/qwhdhub/api/mark/mark31/domark",
                "json": {"date": datetime.now().strftime("%Y%m%d")}
            })
            res = requests.request("POST", **meta)
            result.append(f'app 签到 {res.text}')

            # 任务列表
            meta.update({
                "url": "https://wx.10086.cn/qwhdhub/api/mark/task/taskList",
                "json": {},
            })
            res = requests.request("POST", **meta)
            print(res.text)
            for t in res.json()["data"]["tasks"]:
                taskName, taskId, taskType, jumpUrl = t["taskName"], t["taskId"], t["taskCategory"], t["jumpUrl"]

                # 任务详情
                meta.update({
                    "method": "POST",
                    "url": "https://wx.10086.cn/qwhdhub/api/mark/task/taskInfo",
                    "json": {"taskId": str(taskId)},
                })
                res = requests.request("POST", **meta)
                result.append(f'任务信息 {taskName} {taskType} {taskId} {res.text}')

                taskType = res.json()["data"]["taskType"]

                # app任务完成
                meta.update({
                    "url": "https://wx.10086.cn/qwhdhub/api/mark/task/finishTask",
                    "json": {"taskId": str(taskId), "taskType": str(taskType)},
                })
                res = requests.request("POST", **meta)
                result.append(f'完成任务 {taskName} {taskType} {taskId} {res.text}')

                # 领取奖励
                meta.update({
                    "url": "https://wx.10086.cn/qwhdhub/api/mark/task/getTaskAward",
                    "json": {"taskId": str(t["taskId"])}
                })
                res = requests.request("POST", **meta)
                result.append(f'领取奖励 {taskName} {taskType} {taskId} {res.text}')

    except Exception as e:
        result.append(f'10086 {token} 签到程序异常:{e}')

def req(**kwargs):
    url = kwargs.get("url", "")
    if not url:
        return None
    headers = kwargs.get("headers", {"User-Agent": "okhttp/3.12.1;jdmall;android;version/10.3.4;build/92451;"})
    proxies = kwargs.get("proxies", {})
    try:
        response = requests.request(
            method=kwargs.get("method", "GET"),
            url=url,
            params=kwargs.get("params", {}),
            data=kwargs.get("data", {}),
            json=kwargs.get("json", {}),
            files=kwargs.get("files", {}),
            headers=headers,
            proxies=proxies,
            cookies=kwargs.get("cookies", {}),
            verify=False,
            allow_redirects=True,
            timeout=20,
        )
        return response
    except Exception as e:
        retry = kwargs.get("retry", 0)
        retry += 1
        if retry > 2:
            return None
        return req(**kwargs | {"retry": retry})


if __name__ == "__main__":
    signBeanAct()
    csairSign()