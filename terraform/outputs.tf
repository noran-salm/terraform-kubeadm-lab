output "vpc_id" {
  value = aws_vpc.main.id
}

output "public_subnet_ids" {
  value = aws_subnet.public[*].id
}

output "bastion_public_ip" {
  value = aws_instance.ec2-lab.public_ip
}

output "bastion_instance_id" {
  value = aws_instance.ec2-lab.id
}

output "autoscaling_group_name" {
  value = aws_autoscaling_group.app_asg.name
}

output "ami_id" {
  value = data.aws_ami.ubuntu.id
}

output "ecr_repository_url" {
  description = "ECR repository URL"
  value       = aws_ecr_repository.library_app.repository_url
}

output "ecr_repository_arn" {
  description = "ECR repository ARN"
  value       = aws_ecr_repository.library_app.arn
}
