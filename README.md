# Attio Complement MCP

Companion MCP server for Attio that fills important gaps from the hosted Attio MCP, starting with complete `lists` and `list entries` support.

Built with [FastMCP](https://github.com/jlowin/fastmcp) and streamable HTTP transport.

## Why this exists

The official Attio MCP is great for semantic CRM workflows, but the REST API includes endpoints not currently exposed there (for example, list and list-entry CRUD/query capabilities). This server complements those gaps.

## Implemented tools

- `attio_capabilities` (assistant-facing discovery/selection guide)
- Identity: `attio_identify`
- Lists: `attio_list_lists`, `attio_get_list`, `attio_create_list`, `attio_update_list`
- Entries: `attio_query_list_entries`, `attio_create_list_entry`, `attio_assert_list_entry`, `attio_get_list_entry`, `attio_update_list_entry`, `attio_delete_list_entry`, `attio_get_list_entry_attribute_values`
- Attributes: `attio_list_attributes`, `attio_get_attribute`, `attio_list_select_options`, `attio_list_statuses`
- Comments/Threads: `attio_list_threads`, `attio_get_thread`, `attio_create_comment_on_thread`, `attio_create_comment_on_record`, `attio_create_comment_on_entry`, `attio_get_comment`, `attio_delete_comment`
- Webhooks: `attio_list_webhooks`, `attio_get_webhook`, `attio_create_webhook`, `attio_update_webhook`, `attio_delete_webhook`
- Files: `attio_list_files`, `attio_get_file`, `attio_create_attio_folder`, `attio_create_connected_file_entry`, `attio_delete_file`, `attio_get_file_download_url`
- `attio_raw_request` (fallback for any `/v2/*` or `/scim/v2/*` endpoint not yet wrapped)

## Local setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Set in `.env`:

```bash
ATTIO_ACCESS_TOKEN=your_attio_token
ATTIO_BASE_URL=https://api.attio.com
PORT=8000
```

Run:

```bash
python src/server.py
```

Then connect with MCP Inspector or your client at:

- `http://localhost:8000/mcp` (Streamable HTTP)

## Using with Poke + official Attio MCP

Use both connectors side by side:

- Official Attio MCP: semantic search, email, meeting workflows
- This MCP: list/list-entry operations and any missing endpoint via `attio_raw_request`

For the complete matrix, see:

- `TOOLS_COVERAGE.md`
- `USE_CASES.md` (Render deployment + acceptance test prompts for Poke)

When you want the assistant to force this connector, explicitly reference this integration name and the tool name in your prompt.

## Deployment (Render)

`render.yaml` is included. Deploy as a web service and use:

- `https://<your-service>.onrender.com/mcp`
