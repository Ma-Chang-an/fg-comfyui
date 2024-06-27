terraform {
  required_providers {
    huaweicloud = {
      source  = "huawei.com/provider/huaweicloud"
      version = "= 1.64.1"
    }
  }
}

# Configure the HuaweiCloud Provider
provider "huaweicloud" {
  endpoints = {
    apig = var.region == "cn-north-7" ? format("apig.%s.ulanqab.huawei.com", var.region) : format("apig.%s.myhuaweicloud.com", var.region)
    obs  = var.region == "cn-north-7" ? format("obs.%s.ulanqab.huawei.com", var.region) : format("obs.%s.myhuaweicloud.com", var.region)
    fgs  = var.region == "cn-north-7" ? format("functiongraph.%s.ulanqab.huawei.com", var.region) : format("functiongraph.%s.myhuaweicloud.com", var.region)
  }
  auth_url = format("https://iam.%s.myhuaweicloud.com/v3", var.region)
  insecure = true
  region   = var.region
}
locals {
  timestamp = formatdate("YYYYMMDDhhmmss", timestamp())
}

# Configure the API
resource "huaweicloud_apig_group" "comfyui_apig_group" {
  instance_id = var.apig_id
  name        = format("%s_%s", "comfyui_apig_group", local.timestamp)
  description = "comfyui_apig_group"
}

resource "huaweicloud_apig_group" "filebrowser_apig_group" {
  instance_id = var.apig_id
  name        = format("%s_%s", "filebrowser_apig_group", local.timestamp)
  description = "filebrowser_apig_group"
}

resource "huaweicloud_identity_agency" "agency" {
  count                  = var.agency_name == "" ? 1 : 0
  name                   = "fgs-app-adminagency"
  description            = "agency"
  delegated_service_name = "op_svc_cff"

  all_resources_roles = ["OBS Administrator", "DIS Administrator", "LTS Administrator", "NLP Administrator", "MPC Administrator", "VPC Administrator", "SWR FullAccess", "SFS Turbo FullAccess", "SFS FullAccess"]
}

resource "huaweicloud_fgs_function" "comfyui" {
  name                  = format("%s_%s", "comfyui", local.timestamp)
  functiongraph_version = "v2"
  agency                = var.agency_name != "" ? var.agency_name : huaweicloud_identity_agency.agency[0].name
  handler               = "-"
  app                   = "default"
  runtime               = "http"
  memory_size           = 128
  timeout               = 600
  max_instance_num      = "1"

  custom_image {
    url = format("swr.%s.myhuaweicloud.com/custom_container/fg-comfyui:%s", var.region, var.sd_image_version)
  }
}

resource "huaweicloud_fgs_function" "custom_models_tool" {
  name                  = format("%s-%s", "custom-models-tool", local.timestamp)
  functiongraph_version = "v2"
  agency                = var.agency_name != "" ? var.agency_name : huaweicloud_identity_agency.agency[0].name
  handler               = "-"
  app                   = "default"
  enterprise_project_id = var.enterprise_project_id
  description           = "custom-models-tool"
  runtime               = "http"
  memory_size           = 256
  timeout               = 600

  custom_image {
    url = format("swr.%s.myhuaweicloud.com/custom_container/filebrowser:sd", var.region)
  }
}

resource "huaweicloud_fgs_function_trigger" "createTrigger" {
  function_urn = huaweicloud_fgs_function.comfyui.id
  type         = "DEDICATEDGATEWAY"
  status       = "ACTIVE"

  event_data   = jsonencode({
    "instance_id": var.apig_id
    "group_id": huaweicloud_apig_group.comfyui_apig_group.id
    "name": "stable_diffusion",
    "env_name": "RELEASE",
    "auth": "NONE",
    "type": 1,
    "path": "/",
    "protocol": "HTTPS",
    "req_method": "ANY",
    "match_mode": "SWA",
    "env_id": "DEFAULT_ENVIRONMENT_RELEASE_ID",
    "sl_domain": format("%s.apig.%s.huaweicloudapis.com", huaweicloud_apig_group.comfyui_apig_group.id, var.region)
    "func_info": {"timeout": 60000}
  })
}

resource "huaweicloud_fgs_function_trigger" "obs_model_trigger" {
  function_urn = huaweicloud_fgs_function.custom_models_tool.id
  type         = "DEDICATEDGATEWAY"
  status       = "ACTIVE"

  event_data   = jsonencode({
    "instance_id": var.apig_id
    "group_id": huaweicloud_apig_group.filebrowser_apig_group.id
    "name": "filebrowser",
    "env_name": "RELEASE",
    "auth": "NONE",
    "type": 1,
    "path": "/filebrowser",
    "protocol": "HTTPS",
    "req_method": "ANY",
    "match_mode": "SWA",
    "env_id": "DEFAULT_ENVIRONMENT_RELEASE_ID",
    "sl_domain": format("%s.apig.%s.huaweicloudapis.com", huaweicloud_apig_group.filebrowser_apig_group.id, var.region)
    "func_info": {"timeout": 60000}
  })
}