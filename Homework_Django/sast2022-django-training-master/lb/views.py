from telnetlib import STATUS
from django.http import (
    HttpRequest,
    JsonResponse,
    HttpResponseNotAllowed,
)
from requests import JSONDecodeError
from lb.models import Submission, User
from django.forms.models import model_to_dict
from django.db.models import F
import json
from lb import utils
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.views.decorators.http import require_http_methods as method



def hello(req: HttpRequest):
    return JsonResponse({
        "code": 0,
        "msg": "hello"
    })
# 默认界面显示

@method(["GET"])
def leaderboard(req: HttpRequest):
    return JsonResponse(
        utils.get_leaderboard(),
        safe=False,
    )
# 显示排行榜内容

@method(["GET"])
def history(req: HttpRequest, user_name: str):
    now_user = User.objects.filter(username = user_name)
    if now_user:
        res = Submission.objects.filter(user = now_user.first())
        # 取出对应user_name的所有提交
        if res:
            return JsonResponse(
                [
                    {
                        "score": obj.score,
                        "subs": [int(x) for x in obj.subs.split()],
                        "time": obj.time,
                    }
                    for obj in res
                ],            
                safe=False,
            )
        else:
            # 用户user字段存在，但无提交记录
            # 在当前后端框架，该响应不会触发
            return JsonResponse({
                "code":-2,
                "msg":'该用户无提交记录'
            },status = 404)
    else:
        return JsonResponse({
            "code":-1,
            "msg":'该用户不存在'
        },status = 404)
        # 请求用户user字段不存在


@method(["POST"])
@csrf_exempt
def submit(req: HttpRequest):
    dic = json.loads(req.body)
    if (dic.__contains__('user') and dic.__contains__('avatar') and dic.__contains__('content')) == False:
        return JsonResponse({
            "code":-1,
            "msg":"参数不全嘤嘤嘤",
        }) 
    if len(dic['user']) > 255:
        return JsonResponse({
            "code":-2,
            "msg":"你的名字太长啦"
        }) 
    if len(dic['avatar'])> 100000:
        return JsonResponse({
            "code":-3,
            "msg":"你的头像太大啦，是不是忘了压缩了"
        })
    try:
        now_score,now_subs = utils.judge(dic['content'])
        now_subs_str = [str(x) for x in now_subs]
        now_subs_str = ' '.join(now_subs_str)
        # 把当前三个子任务得分组合成为一个字符串，方便后续与utils.judge对接。
    except Exception as e:
        return JsonResponse({
            "code":-4,
            "msg":Exception
        })
    q = User.objects.filter(username = dic['user'])
    # 找到该用户对应的user对象，从而方便创建submission对象
    if len(q) == False:
        q = User.objects.create(username = dic['user'], votes = 0)
    else:
        q = q.first()
    Submission.objects.create(user = q, avatar = dic['avatar'], score = now_score, subs = now_subs_str)
    return JsonResponse({
        "code":0,
        "msg":"提交成功",
        "data":{
            "leaderboard":utils.get_leaderboard()
        }
    })



@method(["POST"])
@csrf_exempt
def vote(req: HttpRequest):
    if 'User-Agent' not in req.headers \
            or 'requests' in req.headers['User-Agent']:
        return JsonResponse({
            "code": -1
        })
    # user-agent不满足要求，返回-1
    dic = json.loads(req.body)

    if dic.__contains__('user') == False:
        return JsonResponse({
            "code":-2,
            "msg":'缺失user字段'
        }) 
    q = User.objects.filter(username = dic['user'])
    if len(q) == 0:
        return JsonResponse({
            "code":-3,
            "msg":"投票用户不存在"
        })
    q = q.first()
    q.votes = q.votes + 1
    q.save()
    # 改变votes字段并保存
    return JsonResponse({
        "code":0,
        "msg":"投票成功",
        "data":{
            "leaderboard":utils.get_leaderboard()
        }
    })