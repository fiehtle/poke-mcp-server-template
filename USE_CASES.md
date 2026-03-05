# Render + Poke Acceptance Use Cases

Last updated: 2026-03-05

## 1) Deploy On Render

1. Push this repo to GitHub.
2. In Render, create a new **Web Service** from this repo (or use blueprint from `render.yaml`).
3. Set secret env var:
`ATTIO_ACCESS_TOKEN=<your token>`
4. Deploy and copy server URL:
`https://<service-name>.onrender.com/mcp`

## 2) Connect In Poke

1. Open Poke connections.
2. Add MCP integration:
Name: `attio-complement`
URL: `https://<service-name>.onrender.com/mcp`
3. Keep official Attio MCP connected too.

## 3) Non-Destructive Smoke Tests (Run First)

Run each prompt in Poke and verify it calls the `attio-complement` integration.

1. Identity check
Prompt:
`Use the "attio-complement" integration and run attio_identify. Return active, workspace_name, workspace_slug.`
Expected:
`active=true`, correct workspace slug/name.

2. List lists
Prompt:
`Use "attio-complement" and run attio_list_lists. Return name + api_slug for each list.`
Expected:
At least one list returned (if workspace has lists).

3. Get one list
Prompt:
`Use "attio-complement" and run attio_get_list with list="<known list slug>".`
Expected:
List metadata is returned without error.

4. Query entries
Prompt:
`Use "attio-complement" and run attio_query_list_entries with list="<known list slug>", limit=5, offset=0.`
Expected:
Data array returned (possibly empty).

5. Read list attributes
Prompt:
`Use "attio-complement" and run attio_list_attributes with target="lists", identifier="<list id>", limit=20.`
Expected:
Attribute definitions returned.

## 4) Controlled Write Tests (Optional)

Only run these against a dedicated test list.

1. Create test list
Prompt:
`Use "attio-complement" and run attio_create_list with name="MCP Test List", api_slug="mcp_test_list", parent_object="people", workspace_access="read-and-write".`

2. Add entry
Prompt:
`Use "attio-complement" and run attio_create_list_entry using list="mcp_test_list", parent_object="people", parent_record_id="<person_record_uuid>", entry_values={}.`

3. Update entry
Prompt:
`Use "attio-complement" and run attio_update_list_entry for that entry_id with entry_values={<attribute_slug>: <value>}.`

4. Delete entry
Prompt:
`Use "attio-complement" and run attio_delete_list_entry for that entry_id.`

## 5) Gap-Area Tests

1. Threads
Prompt:
`Use "attio-complement" and run attio_list_threads with object="people", record_id="<record_uuid>", limit=10.`

2. Webhooks
Prompt:
`Use "attio-complement" and run attio_list_webhooks with limit=10.`

3. Files
Prompt:
`Use "attio-complement" and run attio_list_files with object="people", record_id="<record_uuid>", limit=20.`

## 6) Fallback Endpoint Check

Prompt:
`Use "attio-complement" and run attio_raw_request with method="GET", path="/v2/workspace_members", params={"limit":10}.`

Expected:
Raw endpoint works when typed wrapper is not available.

## 7) Pass Criteria

- All non-destructive smoke tests pass.
- Poke consistently selects `attio-complement` when explicitly requested.
- At least one write flow (create/update/delete list entry) succeeds in test list.
- At least one gap-area endpoint (threads/webhooks/files) succeeds.
