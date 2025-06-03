# AWS IoT Core Configuration
# Replaces the local Mosquitto MQTT broker with managed AWS IoT Core

# IoT Policy for EVSE devices
resource "aws_iot_policy" "evse_device_policy" {
  name = "${var.project_name}-${var.environment}-evse-device-policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "iot:Connect"
        ]
        Resource = "arn:aws:iot:${var.region}:*:client/${var.project_name}-*"
      },
      {
        Effect = "Allow"
        Action = [
          "iot:Publish"
        ]
        Resource = [
          "arn:aws:iot:${var.region}:*:topic/evse/*/telemetry",
          "arn:aws:iot:${var.region}:*:topic/evse/*/status",
          "arn:aws:iot:${var.region}:*:topic/evse/*/session/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "iot:Subscribe",
          "iot:Receive"
        ]
        Resource = [
          "arn:aws:iot:${var.region}:*:topicfilter/evse/*/commands/*",
          "arn:aws:iot:${var.region}:*:topic/evse/*/commands/*"
        ]
      }
    ]
  })
}

# IoT Policy for backend application
resource "aws_iot_policy" "backend_policy" {
  name = "${var.project_name}-${var.environment}-backend-policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "iot:Connect"
        ]
        Resource = "arn:aws:iot:${var.region}:*:client/${var.project_name}-backend-*"
      },
      {
        Effect = "Allow"
        Action = [
          "iot:Subscribe",
          "iot:Receive"
        ]
        Resource = [
          "arn:aws:iot:${var.region}:*:topicfilter/evse/+/telemetry",
          "arn:aws:iot:${var.region}:*:topic/evse/+/telemetry",
          "arn:aws:iot:${var.region}:*:topicfilter/evse/+/status",
          "arn:aws:iot:${var.region}:*:topic/evse/+/status",
          "arn:aws:iot:${var.region}:*:topicfilter/evse/+/session/+",
          "arn:aws:iot:${var.region}:*:topic/evse/+/session/+"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "iot:Publish"
        ]
        Resource = [
          "arn:aws:iot:${var.region}:*:topic/evse/+/commands/+",
          "arn:aws:iot:${var.region}:*:topic/system/broadcast"
        ]
      }
    ]
  })
}

# IoT Thing Type for EVSE devices
resource "aws_iot_thing_type" "evse_device" {
  name = "${var.project_name}-${var.environment}-evse-device"

  properties {
    description = "EVSE charging station device type"
    attributes = [
      "location",
      "model",
      "max_power_w",
      "connector_type"
    ]
  }

  tags = {
    Name        = "${var.project_name}-${var.environment}-evse-device-type"
    Environment = var.environment
    Project     = var.project_name
  }
}

# Create example EVSE devices (for testing)
resource "aws_iot_thing" "evse_devices" {
  count = 3

  name           = "evse_unit_${format("%02d", count.index + 1)}"
  thing_type_name = aws_iot_thing_type.evse_device.name

  attributes = {
    location       = "Station ${count.index + 1}"
    model          = "SolarRally EVSE v2.0"
    max_power_w    = "7360"
    connector_type = "Type 2"
  }

  tags = {
    Name        = "evse_unit_${format("%02d", count.index + 1)}"
    Environment = var.environment
    Project     = var.project_name
  }
}

# Certificates for EVSE devices
resource "aws_iot_certificate" "evse_devices" {
  count  = 3
  active = true

  tags = {
    Name        = "${var.project_name}-${var.environment}-evse-${format("%02d", count.index + 1)}-cert"
    Environment = var.environment
    Project     = var.project_name
  }
}

# Attach policy to certificates
resource "aws_iot_policy_attachment" "evse_devices" {
  count  = 3
  policy = aws_iot_policy.evse_device_policy.name
  target = aws_iot_certificate.evse_devices[count.index].arn
}

# Attach certificates to things
resource "aws_iot_thing_principal_attachment" "evse_devices" {
  count     = 3
  thing     = aws_iot_thing.evse_devices[count.index].name
  principal = aws_iot_certificate.evse_devices[count.index].arn
}

# IoT Rule to process telemetry data
resource "aws_iot_topic_rule" "telemetry_processor" {
  name        = "${var.project_name}_${var.environment}_telemetry_processor"
  description = "Process EVSE telemetry data and store in database"
  enabled     = true
  sql         = "SELECT *, topic(2) as evse_unit_id FROM 'evse/+/telemetry'"
  sql_version = "2016-03-23"

  lambda {
    function_arn = aws_lambda_function.telemetry_processor.arn
  }

  tags = {
    Name        = "${var.project_name}-${var.environment}-telemetry-rule"
    Environment = var.environment
    Project     = var.project_name
  }
}

# Lambda function for processing telemetry
resource "aws_lambda_function" "telemetry_processor" {
  filename         = "telemetry_processor.zip"
  function_name    = "${var.project_name}-${var.environment}-telemetry-processor"
  role            = aws_iam_role.lambda_telemetry.arn
  handler         = "lambda_function.lambda_handler"
  runtime         = "python3.11"
  timeout         = 30

  environment {
    variables = {
      DB_SECRET_ARN = aws_secretsmanager_secret.db_password.arn
      ENVIRONMENT   = var.environment
    }
  }

  tags = {
    Name        = "${var.project_name}-${var.environment}-telemetry-processor"
    Environment = var.environment
    Project     = var.project_name
  }
}

# IAM role for Lambda function
resource "aws_iam_role" "lambda_telemetry" {
  name = "${var.project_name}-${var.environment}-lambda-telemetry-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name        = "${var.project_name}-${var.environment}-lambda-telemetry-role"
    Environment = var.environment
    Project     = var.project_name
  }
}

# Lambda execution policy
resource "aws_iam_role_policy_attachment" "lambda_telemetry_basic" {
  role       = aws_iam_role.lambda_telemetry.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Lambda VPC execution policy (if needed)
resource "aws_iam_role_policy_attachment" "lambda_telemetry_vpc" {
  role       = aws_iam_role.lambda_telemetry.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}

# Custom policy for Secrets Manager access
resource "aws_iam_role_policy" "lambda_telemetry_secrets" {
  name = "${var.project_name}-${var.environment}-lambda-secrets-policy"
  role = aws_iam_role.lambda_telemetry.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = aws_secretsmanager_secret.db_password.arn
      }
    ]
  })
}

# Permission for IoT to invoke Lambda
resource "aws_lambda_permission" "iot_invoke_lambda" {
  statement_id  = "AllowExecutionFromIoT"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.telemetry_processor.function_name
  principal     = "iot.amazonaws.com"
  source_arn    = aws_iot_topic_rule.telemetry_processor.arn
}

# Output IoT endpoint
data "aws_iot_endpoint" "current" {
  endpoint_type = "iot:Data-ATS"
}

output "iot_endpoint" {
  description = "AWS IoT Core endpoint"
  value       = data.aws_iot_endpoint.current.endpoint_url
}

output "evse_device_certificates" {
  description = "Certificate ARNs for EVSE devices"
  value       = aws_iot_certificate.evse_devices[*].arn
  sensitive   = true
}

output "evse_device_certificate_pems" {
  description = "Certificate PEMs for EVSE devices"
  value       = aws_iot_certificate.evse_devices[*].certificate_pem
  sensitive   = true
}

output "evse_device_private_keys" {
  description = "Private keys for EVSE devices"
  value       = aws_iot_certificate.evse_devices[*].private_key
  sensitive   = true
} 