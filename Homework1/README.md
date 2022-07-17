# 计算机系2022科协暑培Homework1

> author: zyj

## 项目简介：

运用python脚本，从生词表`collection.txt`中选取指定区间与指定数目的生词输出到文件夹./wordbook下untraslated_.txt文件中，并将每一个生词与其近义词通过翻译得到其中文意义后输出到文件夹./wordbook下translated_.txt文件中。

同时脚本支持随机选取与有序选取两种选取方式，可以一次性生成多组生词表与对应翻译后中文表。

## 环境配置：

项目的基本环境配置在`./requirements.yaml`下，请运行如下指令 `conda env create -n <env_name> -f ./requirements.yaml` 添加新的 conda 环境。

其他扩展库包括`pygtrans、Ipython、tqdm`，均可在添加了上述conda环境之后使用如下指令进行安装（以tqdm为例）：

```shell
pip install tqdm
```

## 项目参数说明：

* -r/--random:在生词表中随机选取单词产生单词本，若不输入-r参数则默认为false，表示有序选取。

* -n/--num:选取的单词数目，若不输入-n参数则默认为40个。

* -s/--start:在生词表中选取的单词区间左端点编号，若不输入-s参数则默认为0

* --end:在生词表中选取的单词区间右端点编号，若不输入--end参数则默认为100。该参数与-s参数一同构成了生词的选取区间[start, end)。

若用户要求随机选取单词，则先选取出原生词表中制指定的区间[start,end),再在其中随机选取num个生词。

若num大于区间内所有词组数，则自动将num修改为区间内词组数总和

若end大于文件词组总数或小于start，则输出`选取的生词区间不合法，翻译失败`，并结束本次翻译。

使用示例说明：

```shell
python selector.py -r -n 50 -s 10 --end 100
```

运行上述指令可以完成一次翻译。

通过运行`pipeline.py`文件可以完成批量翻译。
