
# # Fetch running EC2 instances created by the Auto Scaling Group
# data "aws_instances" "asg_nodes" {
#   instance_tags = {
#     Name = "${var.project_name}-asg-instance"
#   }

#   instance_state_names = ["running", "pending"]

#   # Ensure the ASG finishes launching instances before querying their IPs
#   depends_on = [aws_autoscaling_group.app_asg]
# }

# resource "local_file" "ansible_inventory" {
#   filename = "${path.module}/../ansible/inventory.ini"
#   content = templatefile("${path.module}/inventory.tftpl", {
#     bastion_ip = aws_instance.ec2-lab.public_ip
#     # Assigns the 1st ASG instance as master, and the rest as workers
#     master_ips = slice(data.aws_instances.asg_nodes.private_ips, 0, 1)
#     worker_ips = slice(data.aws_instances.asg_nodes.private_ips, 1, length(data.aws_instances.asg_nodes.private_ips))
#   })
# }

# Fetch running EC2 instances created by the Auto Scaling Group
data "aws_instances" "asg_nodes" {
  instance_tags = {
    Name = "${var.project_name}-asg-instance"
  }

  instance_state_names = ["running"]

  depends_on = [
    aws_autoscaling_group.app_asg
  ]
}

resource "local_file" "ansible_inventory" {
  filename = "${path.module}/../ansible/inventory.ini"

  content = templatefile("${path.module}/inventory.tftpl", {
    bastion_ip = aws_instance.ec2-lab.public_ip

    master_ips = slice(
      sort(data.aws_instances.asg_nodes.private_ips),
      0,
      1
    )

    worker_ips = slice(
      sort(data.aws_instances.asg_nodes.private_ips),
      1,
      length(data.aws_instances.asg_nodes.private_ips)
    )
  })
}