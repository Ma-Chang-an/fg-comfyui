### AI绘画 ComfyUI

#### 应用说明
将ComfyUI部署到华为云函数工作流上,支持自定义模型

#### 前期准备
**注意：本应用且仅支持上海一区域使用**

使用本应用你需要开通以下服务，**使用中可能产生费用**：

| 服务                  | 介绍                    |
|---------------------|-----------------------|
| 函数工作流 FunctionGraph | 为ComfyUI提供推理算力和资源管理能力 |
| 弹性文件服务 SFS          | 用于存储模型文件、插件、生成结果等     |
| 专享版APIG             | 用于访问ComfyUI和文件管理页面    |

您还需要注意：
1. 本应用支持自定义模型，并且提前预置了基础模型，自定义模型需要通过资源管理工具上传到网络磁盘中
2. 应用初始启动有较长的白屏时间，这是服务完全冷启动的状态，请耐心等待

#### 应用部署
本应用需要使用专享版APIG触发器，如果您还没有专享版APIG实例请参考<a href="https://support.huaweicloud.com/usermanual-apig/apig_03_0037.html" target="_blank" rel="noopener noreferrer">购买专享版APIG实例</a>在**上海一区域**购买，**并开启“公网入口”**。

**请注意，专享版APIG实例价格较高，购买前请仔细阅读<a href="https://support.huaweicloud.com/price-apig/apig_08_0001.html" target="_blank" rel="noopener noreferrer">API网关计费标准</a>**。

购买完成后，点击本介绍页面下面的“应用配置”按钮，根据引导即可快速部署本应用。 部署过程需要创建相关资源，大约一分钟时间，请耐心等待创建完成。

应用创建完成后将会拥有以下关键资源，其功能介绍如下：

| 资源所属云服务 | 逻辑名称               | 功能                                |
|---------|--------------------|-----------------------------------|
| 函数服务    | comfyui            | AI绘图功能主体，可通过它的APIG触发器访问ComfyUI界面  |
| 函数服务    | custom_models_tool | 可通过它的APIG触发器管理应用资源，如模型、插件上传，图片下载等 |

#### 应用使用
应用创建完成后，**在应用总览页面点击“去绑定”为ComfyU绑定你的自定义域名，具体操作方案请参考<a href="https://support.huaweicloud.com/usermanual-apig/apig_03_0006.html" target="_blank" rel="noopener noreferrer">绑定域名</a>**，在浏览器中打开您绑定的域名即可访问ComfyU界面绘图，初次使用启动时间较长，请耐心等待。

#### 上传模型、自定义节点

1. 在应用总览页，点击“初始化自定义模型”，根据提示选择VPC、子网、文件系统，如果没有以上资源请先创建，**函数访问路径请固定填写`/mnt/auto`**

2. 初始化完成后，点击“上传模型”，即可访问资源管理界面，初始用户名和密码均为`admin`，请登陆后第一时间修改默认密码，以免造成数据泄露

3. 在资源管理管理工具中即可看到文件系统中保存的内容，常用文件和目录的作用如下：

   | 目录                    | 作用                               |
   |-----------------------|----------------------------------|
   | comfyui/models        | 用于保存ComfyUI的各类模型文件               |
   | comfyui/custom_nodes  | 用于保存自定义节点                        |
   | comfyui/outputs       | 用于保存图片生成结果                       |
   | config.json           | Filebrowser的配置文件，如果您不了解它的作用，请勿修改 |
   | database.db           | Filebrowser的数据文件，如果您不了解它的作用，请勿修改 |

4. 上传完成后回到ComfyUI界面后即可看到新增模型

5. 自定义节点请本地下载后解压成目录后上传到`comfyui/custom_nodes`

> 我们提供的<a href="https://github.com/Ma-Chang-an/filebrowser" target="_blank" rel="noopener noreferrer">资源管理工具</a>是基于开源项目<a href="https://github.com/filebrowser/filebrowser" target="_blank" rel="noopener noreferrer">Filebrowser</a>二次开发而来，为其添加了OBS转储能力，关于Filebrowser工具的更多使用方法请到<a href="https://filebrowser.org/" target="_blank" rel="noopener noreferrer">官方网站</a>查询

#### 大文件下载

函数工作流 FunctionGraph仅支持小于6M的文件下载，如果您有大文件下载需求，可以通过我们提供的<a href="https://github.com/Ma-Chang-an/filebrowser" target="_blank" rel="noopener noreferrer">资源管理工具</a>中的OBS转储能力，将大文件传输到您指定的OBS桶中，具体操作方法如下

1. <a href="https://support.huaweicloud.com/usermanual-obs/zh-cn_topic_0045829088.html" target="_blank" rel="noopener noreferrer">创建OBS桶</a>，在OBS桶的概览页面可以获取桶名和终端节点(EndPoint)信息
2. <a href="https://support.huaweicloud.com/usermanual-iam/iam_02_0003.html" target="_blank" rel="noopener noreferrer">获取AK/SK</a>
3. 配置OBS信息：在资源管理工具的“设置”-“个人设置”-“OBS设置”中输入上述步骤中获取的信息，点击更新
4. 上传文件：回到文件列表，选中需要上传的文件，点击右上角“上传到OBS”，等待上传完成即可，文件在OBS桶中保存的路径与网络磁盘中的路径相同
5. 到OBS下载：推荐您使用华为云提供的<a href="https://developer.huaweicloud.com/tools#section-1" target="_blank" rel="noopener noreferrer">OBS Browser+工具或者obsutil工具</a>下载，使用方法请参考<a href="https://support.huaweicloud.com/browsertg-obs/obs_03_1000.html" target="_blank" rel="noopener noreferrer">OBS Browser+简介</a>或<a href="https://support.huaweicloud.com/utiltg-obs/obs_11_0001.html" target="_blank" rel="noopener noreferrer">obsutil简介</a>。


#### 使用Moderation审核生成结果

Stable Diffusion是一种AIGC推理模型，使用它生成图片的最终结果会因提示词、模型选择的不同存在较大的不确定性，存在涉黄、暴力等违法违规风险，建议在使用过程中配合华为云Moderation对生成结果进行审核，以降低风险，详细使用指南请参考<a href="https://support.huaweicloud.com/api-moderation/moderation_03_0086.html" target="_blank" rel="noopener noreferrer">图像内容审核（V3）</a>。

#### 免责声明

1. 本应用使用到的<a href="https://github.com/Stability-AI/stablediffusion" target="_blank" rel="noopener noreferrer">Stable-Diffusion</a>、<a href="https://github.com/comfyanonymous/ComfyUI" target="_blank" rel="noopener noreferrer">ComfyUI</a>、以及<a href="https://github.com/fg-serverless-app/fg-comfyui" target="_blank" rel="noopener noreferrer">ComfyUI镜像构建工程</a>等项目均为社区开源项目，华为云仅提供算力支持；
2. 本应用仅作为简单案例供用户参考和学习使用，如果用于实际生产环境，请用户参考镜像构建工程自行完善和优化；使用过程中出现的函数工作流的问题，可以通过工单进行咨询，关于开源项目的问题还需用户到开源社区寻求帮助或者自行解决；
3. 本应用部署后会为您创建APIG网关，根据有关规定，请在应用创建成功后根据提示绑定自定义域名后，使用您的自有域名访问WebUI界面。

