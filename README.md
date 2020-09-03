# aws-iam-rotate

Rotate your [AWS](https://aws.amazon.com/) [IAM](https://aws.amazon.com/iam/) key.

This tool replaces the IAM key in your `~/.aws/credentials` with a fresh key.
It won't replace your existing IAM key until it verifies that the new key works.
