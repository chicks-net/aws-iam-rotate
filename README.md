# aws-iam-rotate

[![Open Source Love png2](https://badges.frapsoft.com/os/v2/open-source.png?v=103)](https://github.com/ellerbrock/open-source-badges/)
[![GPLv2 license](https://img.shields.io/badge/License-GPLv2-blue.svg)](https://github.com/chicks-net/aws-iam-rotate/blob/master/LICENSE)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/chicks-net/aws-iam-rotate/graphs/commit-activity)

Rotate your [AWS](https://aws.amazon.com/) [IAM](https://aws.amazon.com/iam/) key.

This tool replaces the IAM key in your `~/.aws/credentials` with a fresh key.
It won't replace your existing IAM key until it verifies that the new key works.

## Installation

You need [pipenv](https://docs.pipenv.org/) first.  Then do `pipenv sync` to get the venv created.

Then you can use the wrapper script `rotateiam` to take care of invoking pipenv and running the operation.
