# aws-iam-rotate

[![Open Source Love png2](https://badges.frapsoft.com/os/v2/open-source.png?v=103)](https://github.com/ellerbrock/open-source-badges/)
[![GPLv2 license](https://img.shields.io/badge/License-GPLv2-blue.svg)](https://github.com/chicks-net/aws-iam-rotate/blob/master/LICENSE)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/chicks-net/aws-iam-rotate/graphs/commit-activity)


This tool replaces the
[AWS](https://aws.amazon.com/) [IAM](https://aws.amazon.com/iam/)
key in your `~/.aws/credentials` with a fresh key.
<!-- It won't replace your existing IAM key until it verifies that the new key works. -->

## Installation

1. You need [pipenv](https://docs.pipenv.org/) installed.
1. Do `pipenv sync` to get the venv created.
1. Use the wrapper script `rotate-iam` to take care of invoking pipenv and rotating your IAM key.

## Usage

```
./rotate-iam
```

It respects your `AWS_PROFILE` [environment variable](https://en.wikipedia.org/wiki/Environment_variable)
to find which key to update.

```
AWS_PROFILE=foo ./rotate-iam
```

## Plans

* validate keypair before writing to disk
* deactivate old key
* issue template
* github actions
