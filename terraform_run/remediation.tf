
resource "aws_instance" "isolate_p4d" {
  instance_type = "p4d.24xlarge"
  
  lifecycle {
    create_before_destroy = true
  }
  
  tags = {
    Name        = "isolated-p4d-critical"
    Status      = "ISOLATED"
    Reason      = "CRITICAL RISK - Ultra-high-cost instance detected"
    Isolation   = "true"
  }
}

resource "aws_security_group_rule" "isolate_p4d" {
  type              = "ingress"
  protocol          = "-1"
  from_port         = 0
  to_port           = 0
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_instance.isolate_p4d.id
  
  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_route" "isolate_public_access" {
  route_table_id         = data.aws_route_table.default.id
  destination_cidr_block = "0.0.0.0/0"
  instance_id            = aws_instance.isolate_p4d.id
  
  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_eip" "isolate_public_ip" {
  vpc        = var.vpc_id
  domain     = "vpc"
  
  tags = {
    Name = "isolated-p4d-eip"
  }
}
