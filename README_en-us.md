AI Drawing ComfyUI
#### Application Description
Deploy ComfyUI on HUAWEI CLOUD FunctionGraph to support custom models.

#### Pre-preparation
**Note: This app can be used only in Shanghai 1.**

To use this app, you need to subscribe to the following services. **Fees may be incurred during the use of this app.**:

| Service           | Description                                                 |
|-------------------|-------------------------------------------------------------|
| FunctionGraph     | Provides inference computing power for ComfyUI              |
| SFS               | Used to store model files, plugins, generated results, etc. |
| Dedicated Gateway | For accessing the ComfyUI and file management pages         |

You also need to be aware of:
1. This application supports custom models and comes with pre-installed base models. Custom models need to be uploaded to the network disk using the resource management tool.
2. The white screen takes a long time during the initial startup of the app. This is the cold start state of the service. Please wait patiently.

#### Application deployment
This application requires the use of a dedicated APIG trigger. If you do not yet have a dedicated APIG instance, please refer to <a href="https://support.huaweicloud.com/usermanual-apig/apig_03_0037.html" target="_blank" rel="noopener noreferrer">Purchasing a Dedicated APIG Instance</a> to purchase one in **the Shanghai Zone 1** and **enable the “Public Inbound Access”.**

**Notice: the price of a dedicated APIG instance is high, so please carefully read the <a href="https://support.huaweicloud.com/price-apig/apig_08_0001.html" target="_blank" rel="noopener noreferrer">API Gateway Pricing Standards</a> before purchasing.**

After completing the purchase, Click Application Configuration at the bottom of this page to quickly deploy the application. The deployment takes about one minute to create related resources. Wait until the creation is complete.

After an application is created, it has the following key resources:

| Cloud service    | Logical name       | Function                                                                                                               |
|------------------|--------------------|------------------------------------------------------------------------------------------------------------------------|
| Function service | comfyui            | AI drawing function, which can access the ComfyUI through its APIG trigger.                                            |
| Function Service | custom_models_tool | Manages application resources, such as model and custom node uploads, image downloads, etc., through its APIG trigger. |

#### Usage
After the application creation is complete, click "Go to Bind" on the application overview page to bind your custom domain name to the ComfyUI. For specific instructions, please refer to <a href="https://support.huaweicloud.com/usermanual-apig/apig_03_0006.html" target="_blank" rel="noopener noreferrer">Binding a Domain Name</a>. Once done, open your bound domain name in a browser to access the ComfyUI interface for drawing. Please note that the initial startup time might be longer for the first use, so please be patient.

#### Uploading Models and Custom Node

1. On the Application Overview page, click Initialize Custom Model and select a VPC, subnet, and file system as prompted. If the preceding resources do not exist, create them first. **Set the function access path to `/mnt/auto`**.

2. After initialization, click "Upload Models" to access the resource management interface. The initial username and password are both `admin`. Please log in and change the default password immediately to prevent data leakage.

3. In the resource management tool, you can see the contents stored in the file system, and the roles of commonly used files and directories are as follows:

   | Directory            | Purpose                                                                                    |
   |----------------------|--------------------------------------------------------------------------------------------|
   | comfyui/models       | Used to save model files for ComfyUI                                                       |
   | comfyui/custom_nodes | Used to save custom nodes                                                                  |
   | comfyui/outputs      | Used to save generated image results                                                       |
   | config.json          | Configuration file for Filebrowser. Do not modify if you are not familiar with its purpose |
   | database.db          | Data file for Filebrowser. Do not modify if you are not familiar with its purpose          |

4. After uploading, go back to the ComfyUI interface, you can see the newly added model.

5. For custom nodes, download them locally, unzip them into a directory, and upload them to `comfyui/custom_nodes`.

   > The <a href="https://github.com/Ma-Chang-an/filebrowser" target="_blank" rel="noopener noreferrer">resource management tool</a> we provide is based on the open-source project <a href="https://github.com/filebrowser/filebrowser" target="_blank" rel="noopener noreferrer">Filebrowser</a> with secondary development, adding OBS dumping capabilities. For more usage methods of the Filebrowser tool, please refer to the <a href="https://filebrowser.org/" target="_blank" rel="noopener noreferrer">official website</a>.

#### Downloading Large Files

FunctionGraph only supports downloading files smaller than 6MB. If you need to download large files, you can use the OBS dumping capability in our <a href="_https://github.com/Ma-Chang-an/filebrowser" target="_blank" rel="noopener noreferrer">resource management tool</a> . Here's how:

1. <a href="https://support.huaweicloud.com/usermanual-obs/zh-cn_topic_0045829088.html" target="_blank" rel="noopener noreferrer">Create an OBS bucket</a>. In the bucket overview, you can get the bucket name and endpoint information.
2. <a href="https://support.huaweicloud.com/usermanual-iam/iam_02_0003.html" target="_blank" rel="noopener noreferrer">Get AK/SK</a>.
3. Configure OBS information: In the resource management tool, go to "Settings" - "Personal Settings" - "OBS Settings" and enter the information obtained in the above steps. Click update.
4. Upload files: Go back to the file list, select the files to upload, click "Upload to OBS" in the upper right corner, and wait for the upload to complete. The path where the file is saved in the OBS bucket is the same as the path in the network disk.
5. Downloads from OBS , it is recommended to use Huawei Cloud's <a href="https://developer.huaweicloud.com/tools#section-1" target="_blank" rel="noopener noreferrer">OBS Browser+ or obsuti</a> provided by Huawei Cloud. Refer to the <a href="https://support.huaweicloud.com/browsertg-obs/obs_03_1000.html" target="_blank" rel="noopener noreferrer">OBS Browser+ Introduction</a> or <a href="https://support.huaweicloud.com/utiltg-obs/obs_11_0001.html" target="_blank" rel="noopener noreferrer">obsutil Introduction</a> for usage.


#### Using Moderation for Result Review

Stable Diffusion is an AIGC inference model. The final results generated using it may have significant uncertainty due to different prompts and model selections, and there may be risks of illegal and irregular content such as adult content and violence. It is recommended to use Huawei Cloud Moderation for result review during usage to reduce risks. For detailed usage guidelines, please refer to <a href="https://support.huaweicloud.com/api-moderation/moderation_03_0086.html" target="_blank" rel="noopener noreferrer">Image Content Moderation (V3)</a>.

#### Disclaimer

1. All projects used in this application, such as <a href="https://github.com/Stability-AI/stablediffusion" target="_blank" rel="noopener noreferrer">Stable-Diffusion</a>, <a href="https://github.com/comfyanonymous/ComfyUI" target="_blank" rel="noopener noreferrer">ComfyUI</a>, and the <a href="https://github.com/fg-serverless-app/fg-comfyui" target="_blank" rel="noopener noreferrer">ComfyUI Image Building Project</a>, are community open-source projects. Huawei Cloud only provides computing power support.

2. This application serves only as a simple example for users to refer to and learn from. If used in actual production environments, users are advised to refer to the image building project for self-improvement and optimization. Issues encountered during usage of function workflows can be consulted through service tickets. For issues related to open-source projects, users should seek help from the open-source community or resolve them on their own.

3. After deploying this application, an API Gateway (APIG) will be created for you. According to relevant regulations, after the application is successfully created, please bind a custom domain name as prompted. Then, access the WebUI interface using your own domain name.