from lb.models import Submission, User
from random import randint
import functools
def get_leaderboard():
    """
    Get the current leaderboard
    :return: list[dict]
    """

    # 坏了，我似乎已经忘了 ORM 中该怎么调 API 了
    # 在这里你可选择
    #    1. 看一眼数据表, 然后后裸写 SQL
    #    2. 把所有数据一股脑取回来然后手工选出每个用户的最后一次提交
    #    3. 学习 Django API 完成这个查询

    # 方案1: 直接裸写 SQL 摆烂，注意，由于数据库类型等因素，这个查询未必能正确执行，如果使用这种方法可能需要进行调整
    # subs = list(Submission.objects.raw(
    #         """
    #         SELECT
    #             `lb_submission`.`id`,
    #             `lb_submission`.`avatar`,
    #             `lb_submission`.`score`,
    #             `lb_submission`.`subs`,
    #             `lb_submission`.`time`
    #         FROM `lb_submission`, (
    #             SELECT `user_id`, MAX(`time`) AS mt FROM `lb_submission` GROUP BY `user_id`
    #         ) `sq`
    #         WHERE
    #             `lb_submission`.`user_id`=`sq`.`user_id` AND
    #             `time`=`sq`.`mt`;
    #         ORDER BY
    #             `lb_submission`.`subs` DESC,
    #             `lb_submission`.`time` ASC
    #         ;
    #         """
    # ))
    # return [
    #     {
    #         "user": obj.user.username,
    #         "score": obj.score,
    #         "subs": [int(x) for x in obj.subs.split()],
    #         "avatar": obj.avatar,
    #         "time": obj.time,
    #         "votes": obj.user.votes
    #     }
    #     for obj in subs
    # ]

    # 方案2：一股脑拿回本地计算
    all_submission = Submission.objects.all()
    subs = {}
    for s in all_submission:
        if s.user_id not in subs or (s.user_id in subs and s.time > subs[s.user_id].time):
            subs[s.user_id] = s

    subs = sorted(subs.values(), key=lambda x: (-x.score, x.time))
    return [
        {
            "user": obj.user.username,
            "score": obj.score,
            "subs": [int(x) for x in obj.subs.split()],
            "avatar": obj.avatar,
            "time": obj.time,
            "votes": obj.user.votes
        }
        for obj in subs
    ]

    # 方案3：调用 Django 的 API (俺不会了
    # ...

def judge(content: str):
    """
    Convert submitted content to a main score and a list of sub scors
    :param content: the submitted content to be judged
    :return: main score, list[sub score]
    """
    try:
        file_std = open(r'lb/ground_truth.txt','r')
        std_answer = file_std.read().splitlines()
        now_answer = content.splitlines()
        # 打开文件，并按行分割转化为列表
    except Exception:
        raise Exception('文件打开失败')
    
    if len(std_answer) != len(now_answer):
        raise Exception('输入文件长度不符合规范，未包含所有图片')
    # 若输入文件与标准答案行数不一致，报错
    if(now_answer[0] != std_answer[0]):
        raise Exception('输入文件列名有误')
    # 输入文件列名需按照“图片名、山、天空、水”的顺序进行排列
    total_answer = [0,0,0]
    for i in range(1, len(std_answer)):
        std_sub_answer = std_answer[i].split(',')
        now_sub_answer = now_answer[i].split(',')
        if(now_sub_answer[0] != std_sub_answer[0]):
            raise Exception('图像名称有误')
        for j in range(1,4):
            if (now_sub_answer[j] != 'False') and ( now_sub_answer[j] != 'True') :
                raise Exception('对图像的判断不合规范')
            else:
                total_answer[j-1] += (now_sub_answer[j] == std_sub_answer[j])
    tot_len = len(std_answer) - 1
    for i in range(3):
        total_answer[i] = int(total_answer[i] * 100 / tot_len)
    # 总分为三个子任务的平均分然后舍去小数部分
    return int(sum(total_answer) / 3), total_answer
