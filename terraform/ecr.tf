
resource "aws_ecr_repository" "library_app" {
  name                 = "library-app"
  image_tag_mutability = "IMMUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  encryption_configuration {
    encryption_type = "AES256"
  }

  tags = {
    Name        = "library-app"
    Environment = "dev"
    ManagedBy   = "Terraform"
  }
}

