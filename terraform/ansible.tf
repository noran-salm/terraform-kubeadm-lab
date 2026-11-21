
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
    master_ips = slice(
      sort(data.aws_instances.asg_nodes.public_ips),
      0,
      1
    )

    worker_ips = slice(
      sort(data.aws_instances.asg_nodes.public_ips),
      1,
      2
    )
  })

  depends_on = [
    aws_autoscaling_group.app_asg
  ]
}
