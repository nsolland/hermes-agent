# SaladCloud provider for Hermes Agent

Use SaladCloud AI Gateway's `qwen3.6-35b-a3b` model in [Hermes Agent](https://github.com/NousResearch/hermes-agent).

The plugin uses SaladCloud's OpenAI-compatible API at `https://ai.salad.cloud/v1`. It intentionally exposes only `qwen3.6-35b-a3b`.

## Requirements

- A current Hermes Agent build with user model-provider plugin support
- Closed-beta access to SaladCloud AI Gateway
- A Salad API key from the [SaladCloud portal](https://portal.salad.com/)

## Install

Update Hermes first. Older builds use a fixed `--provider` allow-list and reject
standalone providers before plugin discovery runs.

```bash
hermes update
```

Clone this repository into Hermes' user model-provider directory:

```bash
mkdir -p ~/.hermes/plugins/model-providers
git clone https://github.com/SaladTechnologies/hermes-saladcloud-provider.git \
  ~/.hermes/plugins/model-providers/saladcloud
```

If `HERMES_HOME` points elsewhere, install the repository under `$HERMES_HOME/plugins/model-providers/saladcloud` instead.

## Configure

Set the API key using the environment variable from SaladCloud's documentation:

```bash
export SALAD_API_KEY="your-salad-api-key"
```

Then select the provider and model:

```bash
hermes chat --provider saladcloud -m qwen3.6-35b-a3b
```

`SALAD_CLOUD_API_KEY` remains available as a compatibility alias. `SALAD_BASE_URL` can override the default endpoint.

## Verify

```bash
hermes doctor
```

If `hermes chat` reports that `saladcloud` is an invalid `--provider` choice,
the installed Hermes build predates user model-provider support. Run
`hermes update`, then retry the command.

For current access, model, and billing details, see the official [getting-started guide](https://docs.salad.com/ai-gateway/tutorials/getting-started), [model reference](https://docs.salad.com/ai-gateway/reference/models), and [pricing reference](https://docs.salad.com/ai-gateway/reference/pricing).
