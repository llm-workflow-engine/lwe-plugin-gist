# LLM Workflow Engine (LWE) Github Gist plugin

Github Gist plugin for [LLM Workflow Engine](https://github.com/llm-workflow-engine/llm-workflow-engine)

Post a conversation to [https://gist.github.com](https://gist.github.com)

## Installation

Grab your access token from [https://github.com/settings/tokens](https://github.com/settings/tokens) -- you'll need to have a
user account on [https://github.com](https://github.com) and be logged in to create the token. Recommend to create a 'classic'
token with only the `gist` scope.

Export the key into your local environment:

```bash
export GITHUB_GIST_ACCESS_TOKEN=<ACCESS_TOKEN>
```

### From packages

Install the latest version of this software directly from github with pip:

```bash
pip install git+https://github.com/llm-workflow-engine/lwe-plugin-gist
```

### From source (recommended for development)

Install the latest version of this software directly from git:

```bash
git clone https://github.com/llm-workflow-engine/lwe-plugin-gist.git
```

Install the development package:

```bash
cd lwe-plugin-gist
pip install -e .
```

## Configuration

Add the following to `config.yaml` in your profile:

```yaml
plugins:
  enabled:
    - gist
    # Any other plugins you want enabled...
  # These are the default values.
  gist:
    defaults:
      # File extension to use for the content.
      file_extension: md
      # Valid values: public, secret
      visibility: public
    # If true, include the link to the raw version of the gist.
    include_raw_link: false
    # If true, exclude any system messages when generating the
    # content of the gist.
    exclude_system_messages: false
```

## Usage

Use the `/gist` command to store the contents of the current conversation to [https://gist.github.com](https://gist.github.com).

Format is `/gist [public|secret] [file_extension] [custom title]`

From a running LWE shell:

```
# Use the defaults.
/gist
# A secret gist.
/gist secret
# Custom everything
/gist public yaml My custom title
```
