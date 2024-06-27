variable "enterprise_project_id" {
  type        = string
  description = " Specifies enterprise_project_id"
  default     = "0"
}
variable "agency_name" {
  type        = string
  description = " Specifies the agency to which the function belongs."
  default     = ""
}
variable "region" {
  type        = string
  description = " Specifies the region."
  default     = "cn-east-3"
}

variable "sd_image_version" {
  type        = string
  description = "sd_image_version"
  default     = "sd1.5"
}

variable "apig_id" {
  type        = string
  description = "apig_id"
  default     = ""
}