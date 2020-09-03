# aws-iam-rotate

Rotate your [AWS](https://aws.amazon.com/) [IAM](https://aws.amazon.com/iam/) key.

This tool replaces the IAM key in your `~/.aws/credentials` with a fresh key.
It won't replace your existing IAM key until it verifies that the new key works.

## Installation

You need [pipenv](https://docs.pipenv.org/) first.  Then do `pipenv sync` to get the venv created.

Then you can use the wrapper script `rotateiam` to take care of invoking pipenv and running the operation.
