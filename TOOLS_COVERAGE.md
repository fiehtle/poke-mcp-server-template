# Tools Coverage Matrix

Last updated: 2026-03-05

This document maps Attio capabilities across:

- Official Attio MCP (hosted by Attio)
- This companion MCP (`attio-complement`)
- Attio REST API endpoints (OpenAPI)

## How Assistants Should Choose Tools

1. Use official Attio MCP for semantic workflows (emails, semantic note/call search, workspace teams).
2. Use this companion MCP for typed REST wrappers (lists, entries, attributes, comments/threads, webhooks, files).
3. Use `attio_raw_request` only when no typed wrapper exists yet.

## Capability Matrix

| Capability | Official Attio MCP | Companion MCP | REST Endpoint Coverage | Assistant Guidance |
| --- | --- | --- | --- | --- |
| Identity/workspace token context | `whoami` | `attio_identify` | `GET /v2/self` | Either tool is fine. |
| Record search and profile lookup | `search-records`, `get-records-by-ids` | `attio_raw_request` | `POST /v2/objects/records/search`, `GET /v2/objects/{object}/records/{record_id}` | Prefer official MCP unless you need exact raw payload behavior. |
| Record create/upsert | `create-record`, `upsert-record` | `attio_raw_request` | `POST/PUT /v2/objects/{object}/records` | Prefer official MCP for simple CRM prompts; raw for advanced schema cases. |
| Lists CRUD | Not exposed | `attio_list_lists`, `attio_get_list`, `attio_create_list`, `attio_update_list` | `GET/POST /v2/lists`, `GET/PATCH /v2/lists/{list}` | Use companion MCP. |
| List entries query + CRUD | Not exposed | `attio_query_list_entries`, `attio_create_list_entry`, `attio_assert_list_entry`, `attio_get_list_entry`, `attio_update_list_entry`, `attio_delete_list_entry`, `attio_get_list_entry_attribute_values` | `/v2/lists/{list}/entries*` | Use companion MCP. |
| Attribute definitions / metadata | `list-attribute-definitions` (read) | `attio_list_attributes`, `attio_get_attribute`, `attio_list_select_options`, `attio_list_statuses` | `/v2/{target}/{identifier}/attributes*` | Use companion MCP when you need IDs/options/statuses for list/object schema work. |
| Notes (metadata + semantic) | `search-notes-by-metadata`, `semantic-search-notes`, `get-note-body`, `create-note` | `attio_raw_request` | `GET/POST /v2/notes`, `GET/DELETE /v2/notes/{note_id}` | Prefer official MCP for semantic note retrieval. |
| Tasks | `create-task`, `update-task` | `attio_raw_request` | `/v2/tasks*` | Prefer official MCP for common task workflows. |
| Meetings/call recordings | `search-meetings`, `search-call-recordings-by-metadata`, `semantic-search-call-recordings`, `get-call-recording` | `attio_raw_request` | `/v2/meetings*`, `/v2/meetings/{meeting_id}/call_recordings*` | Prefer official MCP for semantic call analysis. |
| Emails | `search-emails-by-metadata`, `semantic-search-emails`, `get-email-content` | Not available | Not present in public OpenAPI path list | Use official MCP. |
| Workspace members | `list-workspace-members` | `attio_raw_request` | `/v2/workspace_members*` | Either; official MCP is simpler. |
| Workspace teams | `list-workspace-teams` | Not available | Not present in public OpenAPI path list | Use official MCP. |
| Comments + threads | Not exposed | `attio_list_threads`, `attio_get_thread`, `attio_create_comment_on_thread`, `attio_create_comment_on_record`, `attio_create_comment_on_entry`, `attio_get_comment`, `attio_delete_comment` | `/v2/threads*`, `/v2/comments*` | Use companion MCP. |
| Webhooks | Not exposed | `attio_list_webhooks`, `attio_get_webhook`, `attio_create_webhook`, `attio_update_webhook`, `attio_delete_webhook` | `/v2/webhooks*` | Use companion MCP. |
| Files (alpha) | Not exposed | `attio_list_files`, `attio_get_file`, `attio_create_attio_folder`, `attio_create_connected_file_entry`, `attio_delete_file`, `attio_get_file_download_url` | `/v2/files*` | Use companion MCP; expect API changes because this surface is alpha. |
| SCIM | Not exposed | `attio_raw_request` | `/scim/v2/Schemas`, `/scim/v2/Users`, `/scim/v2/Groups` | Use `attio_raw_request` for now. |

## Companion MCP: Typed Wrapper Map

### Discovery and planning

- `attio_capabilities`

### Lists and entries

- `attio_list_lists` -> `GET /v2/lists`
- `attio_get_list` -> `GET /v2/lists/{list}`
- `attio_create_list` -> `POST /v2/lists`
- `attio_update_list` -> `PATCH /v2/lists/{list}`
- `attio_query_list_entries` -> `POST /v2/lists/{list}/entries/query`
- `attio_create_list_entry` -> `POST /v2/lists/{list}/entries`
- `attio_assert_list_entry` -> `PUT /v2/lists/{list}/entries`
- `attio_get_list_entry` -> `GET /v2/lists/{list}/entries/{entry_id}`
- `attio_update_list_entry` -> `PATCH|PUT /v2/lists/{list}/entries/{entry_id}`
- `attio_delete_list_entry` -> `DELETE /v2/lists/{list}/entries/{entry_id}`
- `attio_get_list_entry_attribute_values` -> `GET /v2/lists/{list}/entries/{entry_id}/attributes/{attribute}/values`

### Attributes

- `attio_list_attributes` -> `GET /v2/{target}/{identifier}/attributes`
- `attio_get_attribute` -> `GET /v2/{target}/{identifier}/attributes/{attribute}`
- `attio_list_select_options` -> `GET /v2/{target}/{identifier}/attributes/{attribute}/options`
- `attio_list_statuses` -> `GET /v2/{target}/{identifier}/attributes/{attribute}/statuses`

### Comments and threads

- `attio_list_threads` -> `GET /v2/threads`
- `attio_get_thread` -> `GET /v2/threads/{thread_id}`
- `attio_create_comment_on_thread` -> `POST /v2/comments` (thread target)
- `attio_create_comment_on_record` -> `POST /v2/comments` (record target)
- `attio_create_comment_on_entry` -> `POST /v2/comments` (entry target)
- `attio_get_comment` -> `GET /v2/comments/{comment_id}`
- `attio_delete_comment` -> `DELETE /v2/comments/{comment_id}`

### Webhooks

- `attio_list_webhooks` -> `GET /v2/webhooks`
- `attio_get_webhook` -> `GET /v2/webhooks/{webhook_id}`
- `attio_create_webhook` -> `POST /v2/webhooks`
- `attio_update_webhook` -> `PATCH /v2/webhooks/{webhook_id}`
- `attio_delete_webhook` -> `DELETE /v2/webhooks/{webhook_id}`

### Files (alpha)

- `attio_list_files` -> `GET /v2/files`
- `attio_get_file` -> `GET /v2/files/{file_id}`
- `attio_create_attio_folder` -> `POST /v2/files` (`file_type=folder`)
- `attio_create_connected_file_entry` -> `POST /v2/files` (`file_type=connected-file|connected-folder`)
- `attio_delete_file` -> `DELETE /v2/files/{file_id}`
- `attio_get_file_download_url` -> `GET /v2/files/{file_id}/download` (returns redirect URL)

### Fallback

- `attio_raw_request` -> Any allowed path under `/v2/` or `/scim/v2/`

## Known Gaps (Typed wrappers not added yet)

- Full typed wrappers for object/record CRUD and query (`/v2/objects*`, `/v2/objects/{object}/records*`)
- Typed wrappers for notes/tasks/meetings/call recordings
- Typed wrappers for attribute write operations (create/update options/statuses)
- SCIM typed wrappers

All of these remain reachable with `attio_raw_request`.
