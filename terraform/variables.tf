variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "eu-west-3"
}

variable "aws_profile" {
  description = "AWS CLI profile"
  type        = string
  default     = "ecr-lab"
}

variable "project_name" {
  type    = string
  default = "terraform-project"
}

variable "instance_type" {
  type    = string
  default = "t3.micro"
}

variable "key_name" {
  description = "Existing AWS EC2 Key Pair name"
  type        = string
  default = "my-aws-key"  
}

variable "my_ip" {
  description = "my public IP address"
  type        = string
}
