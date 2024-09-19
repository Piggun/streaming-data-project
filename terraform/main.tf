provider "aws" {
  region = "eu-west-2"
}

resource "aws_sqs_queue" "terraform_queue" {
  name                      = "the-guardian-articles"
  message_retention_seconds = 259200
}

resource "aws_dynamodb_table" "my_table" {
  name           = "request-counter"
  hash_key         = "Date"
  read_capacity  = 10
  write_capacity = 10

  attribute {
    name = "Date"
    type = "S"
  }
}