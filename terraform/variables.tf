variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "eu-west-3"
}

variable "project_name" {
  type    = string
  default = "terraform-project"
}

variable "instance_type" {
  description = "instance_type"
  type        = string
  default     = "c7i-flex.large"
}

variable "key_name" {
  description = "Existing AWS EC2 Key Pair name"
  type        = string
  default     = "my-aws-key"
}

variable "my_ip" {
  description = "my public IP address"
  type        = string
}
