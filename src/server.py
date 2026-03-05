#!/usr/bin/env python3
from __future__ import annotations

import os
from typing import Any, Literal

from dotenv import load_dotenv
from fastmcp import FastMCP

try:
    from .attio_client import AttioAPIError, AttioClient
except ImportError:
    from attio_client import AttioAPIError, AttioClient

load_dotenv()

TargetType = Literal["objects", "lists"]
StorageProvider = Literal["attio", "dropbox", "box", "google-drive", "microsoft-onedrive"]

mcp = FastMCP("Attio Complement MCP")
_client: AttioClient | None = None


def get_client() -> AttioClient:
    global _client
    if _client is None:
        _client = AttioClient()
    return _client


def call_attio(
    method: str,
    path: str,
    *,
    params: dict[str, Any] | None = None,
    body: dict[str, Any] | None = None,
) -> dict[str, Any]:
    try:
        return get_client().request(method, path, params=params, json_body=body)
    except AttioAPIError as exc:
        raise RuntimeError(str(exc)) from exc


def resolve_comment_author_id(author_workspace_member_id: str | None) -> str:
    if author_workspace_member_id:
        return author_workspace_member_id

    identity = call_attio("GET", "/v2/self")
    resolved = identity.get("authorized_by_workspace_member_id")
    if not isinstance(resolved, str) or not resolved:
        raise ValueError(
            "Could not infer author workspace member ID from /v2/self. "
            "Pass author_workspace_member_id explicitly."
        )

    return resolved


def build_comment_data(
    *,
    content: str,
    author_workspace_member_id: str,
    created_at: str | None = None,
) -> dict[str, Any]:
    data: dict[str, Any] = {
        "format": "plaintext",
        "content": content,
        "author": {
            "type": "workspace-member",
            "id": author_workspace_member_id,
        },
    }

    if created_at is not None:
        data["created_at"] = created_at

    return data


@mcp.tool(
    description=(
        "Return wrapper categories and usage guidance so assistants can pick the best tool before "
        "falling back to raw requests."
    )
)
def attio_capabilities() -> dict[str, Any]:
    return {
        "server": "Attio Complement MCP",
        "selection_order": [
            "Use typed list/list-entry tools first.",
            "Use typed attribute tools to discover slugs/IDs before writes.",
            "Use typed comment/thread, webhook, and file tools where available.",
            "Use attio_raw_request only when a typed tool is missing.",
        ],
        "categories": {
            "identity": ["attio_identify"],
            "lists": [
                "attio_list_lists",
                "attio_get_list",
                "attio_create_list",
                "attio_update_list",
            ],
            "entries": [
                "attio_query_list_entries",
                "attio_create_list_entry",
                "attio_assert_list_entry",
                "attio_get_list_entry",
                "attio_update_list_entry",
                "attio_delete_list_entry",
                "attio_get_list_entry_attribute_values",
            ],
            "attributes": [
                "attio_list_attributes",
                "attio_get_attribute",
                "attio_list_select_options",
                "attio_list_statuses",
            ],
            "comments_threads": [
                "attio_list_threads",
                "attio_get_thread",
                "attio_create_comment_on_thread",
                "attio_create_comment_on_record",
                "attio_create_comment_on_entry",
                "attio_get_comment",
                "attio_delete_comment",
            ],
            "webhooks": [
                "attio_list_webhooks",
                "attio_get_webhook",
                "attio_create_webhook",
                "attio_update_webhook",
                "attio_delete_webhook",
            ],
            "files": [
                "attio_list_files",
                "attio_get_file",
                "attio_create_attio_folder",
                "attio_create_connected_file_entry",
                "attio_delete_file",
                "attio_get_file_download_url",
            ],
            "fallback": ["attio_raw_request"],
        },
    }


@mcp.tool(description="Identify the current Attio token/workspace (GET /v2/self).")
def attio_identify() -> dict[str, Any]:
    return call_attio("GET", "/v2/self")


# Lists and list entries


@mcp.tool(description="List all lists visible to the token (GET /v2/lists).")
def attio_list_lists() -> dict[str, Any]:
    return call_attio("GET", "/v2/lists")


@mcp.tool(description="Get a single list by list UUID or slug (GET /v2/lists/{list}).")
def attio_get_list(list: str) -> dict[str, Any]:
    return call_attio("GET", f"/v2/lists/{list}")


@mcp.tool(description="Create a list (POST /v2/lists).")
def attio_create_list(
    name: str,
    api_slug: str,
    parent_object: str,
    workspace_access: Literal["full-access", "read-and-write", "read-only"] | None = "read-and-write",
    workspace_member_access: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    body: dict[str, Any] = {
        "data": {
            "name": name,
            "api_slug": api_slug,
            "parent_object": parent_object,
            "workspace_access": workspace_access,
            "workspace_member_access": workspace_member_access or [],
        }
    }
    return call_attio("POST", "/v2/lists", body=body)


@mcp.tool(description="Update a list by UUID or slug (PATCH /v2/lists/{list}).")
def attio_update_list(
    list: str,
    name: str | None = None,
    api_slug: str | None = None,
    workspace_access: Literal["full-access", "read-and-write", "read-only"] | None = None,
    workspace_member_access: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    data: dict[str, Any] = {}
    if name is not None:
        data["name"] = name
    if api_slug is not None:
        data["api_slug"] = api_slug
    if workspace_access is not None:
        data["workspace_access"] = workspace_access
    if workspace_member_access is not None:
        data["workspace_member_access"] = workspace_member_access

    if not data:
        raise ValueError("Provide at least one field to update.")

    return call_attio("PATCH", f"/v2/lists/{list}", body={"data": data})


@mcp.tool(
    description=(
        "Query list entries with filter/sorts/pagination "
        "(POST /v2/lists/{list}/entries/query)."
    )
)
def attio_query_list_entries(
    list: str,
    filter: dict[str, Any] | None = None,
    sorts: list[dict[str, Any]] | None = None,
    limit: int = 100,
    offset: int = 0,
) -> dict[str, Any]:
    body: dict[str, Any] = {
        "limit": limit,
        "offset": offset,
    }
    if filter is not None:
        body["filter"] = filter
    if sorts is not None:
        body["sorts"] = sorts

    return call_attio("POST", f"/v2/lists/{list}/entries/query", body=body)


@mcp.tool(description="Create a list entry (POST /v2/lists/{list}/entries).")
def attio_create_list_entry(
    list: str,
    parent_object: str,
    parent_record_id: str,
    entry_values: dict[str, Any],
) -> dict[str, Any]:
    body = {
        "data": {
            "parent_object": parent_object,
            "parent_record_id": parent_record_id,
            "entry_values": entry_values,
        }
    }
    return call_attio("POST", f"/v2/lists/{list}/entries", body=body)


@mcp.tool(description="Assert a list entry by parent record (PUT /v2/lists/{list}/entries).")
def attio_assert_list_entry(
    list: str,
    parent_object: str,
    parent_record_id: str,
    entry_values: dict[str, Any],
) -> dict[str, Any]:
    body = {
        "data": {
            "parent_object": parent_object,
            "parent_record_id": parent_record_id,
            "entry_values": entry_values,
        }
    }
    return call_attio("PUT", f"/v2/lists/{list}/entries", body=body)


@mcp.tool(description="Get a list entry by entry UUID (GET /v2/lists/{list}/entries/{entry_id}).")
def attio_get_list_entry(list: str, entry_id: str) -> dict[str, Any]:
    return call_attio("GET", f"/v2/lists/{list}/entries/{entry_id}")


@mcp.tool(
    description=(
        "Update list-entry values. Uses PATCH by default (append multiselect values); "
        "set overwrite_multiselect_values=true to use PUT."
    )
)
def attio_update_list_entry(
    list: str,
    entry_id: str,
    entry_values: dict[str, Any],
    overwrite_multiselect_values: bool = False,
) -> dict[str, Any]:
    method = "PUT" if overwrite_multiselect_values else "PATCH"
    body = {"data": {"entry_values": entry_values}}
    return call_attio(method, f"/v2/lists/{list}/entries/{entry_id}", body=body)


@mcp.tool(description="Delete a list entry (DELETE /v2/lists/{list}/entries/{entry_id}).")
def attio_delete_list_entry(list: str, entry_id: str) -> dict[str, Any]:
    return call_attio("DELETE", f"/v2/lists/{list}/entries/{entry_id}")


@mcp.tool(
    description=(
        "Get values for one attribute on a list entry "
        "(GET /v2/lists/{list}/entries/{entry_id}/attributes/{attribute}/values)."
    )
)
def attio_get_list_entry_attribute_values(
    list: str,
    entry_id: str,
    attribute: str,
    show_historic: bool | None = None,
    limit: int | None = None,
    offset: int | None = None,
) -> dict[str, Any]:
    return call_attio(
        "GET",
        f"/v2/lists/{list}/entries/{entry_id}/attributes/{attribute}/values",
        params={
            "show_historic": show_historic,
            "limit": limit,
            "offset": offset,
        },
    )


# Attribute wrappers


@mcp.tool(description="List attributes on an object or list (GET /v2/{target}/{identifier}/attributes).")
def attio_list_attributes(
    target: TargetType,
    identifier: str,
    limit: int | None = None,
    offset: int | None = None,
    show_archived: bool | None = None,
) -> dict[str, Any]:
    return call_attio(
        "GET",
        f"/v2/{target}/{identifier}/attributes",
        params={
            "limit": limit,
            "offset": offset,
            "show_archived": show_archived,
        },
    )


@mcp.tool(description="Get one attribute on an object or list (GET /v2/{target}/{identifier}/attributes/{attribute}).")
def attio_get_attribute(
    target: TargetType,
    identifier: str,
    attribute: str,
) -> dict[str, Any]:
    return call_attio("GET", f"/v2/{target}/{identifier}/attributes/{attribute}")


@mcp.tool(
    description=(
        "List select options for an attribute "
        "(GET /v2/{target}/{identifier}/attributes/{attribute}/options)."
    )
)
def attio_list_select_options(
    target: TargetType,
    identifier: str,
    attribute: str,
    show_archived: bool | None = None,
) -> dict[str, Any]:
    return call_attio(
        "GET",
        f"/v2/{target}/{identifier}/attributes/{attribute}/options",
        params={"show_archived": show_archived},
    )


@mcp.tool(
    description=(
        "List statuses for a status attribute "
        "(GET /v2/{target}/{identifier}/attributes/{attribute}/statuses)."
    )
)
def attio_list_statuses(
    target: TargetType,
    identifier: str,
    attribute: str,
    show_archived: bool | None = None,
) -> dict[str, Any]:
    return call_attio(
        "GET",
        f"/v2/{target}/{identifier}/attributes/{attribute}/statuses",
        params={"show_archived": show_archived},
    )


# Comment/thread wrappers


@mcp.tool(description="List threads on records or list entries (GET /v2/threads).")
def attio_list_threads(
    object: str | None = None,
    record_id: str | None = None,
    list: str | None = None,
    entry_id: str | None = None,
    limit: int = 10,
    offset: int = 0,
) -> dict[str, Any]:
    if (object is None) != (record_id is None):
        raise ValueError("Pass both object and record_id together, or neither.")
    if (list is None) != (entry_id is None):
        raise ValueError("Pass both list and entry_id together, or neither.")

    return call_attio(
        "GET",
        "/v2/threads",
        params={
            "object": object,
            "record_id": record_id,
            "list": list,
            "entry_id": entry_id,
            "limit": limit,
            "offset": offset,
        },
    )


@mcp.tool(description="Get a thread with all comments (GET /v2/threads/{thread_id}).")
def attio_get_thread(thread_id: str) -> dict[str, Any]:
    return call_attio("GET", f"/v2/threads/{thread_id}")


@mcp.tool(description="Create a comment in an existing thread (POST /v2/comments).")
def attio_create_comment_on_thread(
    thread_id: str,
    content: str,
    author_workspace_member_id: str | None = None,
    created_at: str | None = None,
) -> dict[str, Any]:
    author_id = resolve_comment_author_id(author_workspace_member_id)
    data = build_comment_data(
        content=content,
        author_workspace_member_id=author_id,
        created_at=created_at,
    )
    data["thread_id"] = thread_id
    return call_attio("POST", "/v2/comments", body={"data": data})


@mcp.tool(description="Create a top-level comment on a record (POST /v2/comments).")
def attio_create_comment_on_record(
    object: str,
    record_id: str,
    content: str,
    author_workspace_member_id: str | None = None,
    created_at: str | None = None,
) -> dict[str, Any]:
    author_id = resolve_comment_author_id(author_workspace_member_id)
    data = build_comment_data(
        content=content,
        author_workspace_member_id=author_id,
        created_at=created_at,
    )
    data["record"] = {
        "object": object,
        "record_id": record_id,
    }
    return call_attio("POST", "/v2/comments", body={"data": data})


@mcp.tool(description="Create a top-level comment on a list entry (POST /v2/comments).")
def attio_create_comment_on_entry(
    list: str,
    entry_id: str,
    content: str,
    author_workspace_member_id: str | None = None,
    created_at: str | None = None,
) -> dict[str, Any]:
    author_id = resolve_comment_author_id(author_workspace_member_id)
    data = build_comment_data(
        content=content,
        author_workspace_member_id=author_id,
        created_at=created_at,
    )
    data["entry"] = {
        "list": list,
        "entry_id": entry_id,
    }
    return call_attio("POST", "/v2/comments", body={"data": data})


@mcp.tool(description="Get a comment by ID (GET /v2/comments/{comment_id}).")
def attio_get_comment(comment_id: str) -> dict[str, Any]:
    return call_attio("GET", f"/v2/comments/{comment_id}")


@mcp.tool(description="Delete a comment by ID (DELETE /v2/comments/{comment_id}).")
def attio_delete_comment(comment_id: str) -> dict[str, Any]:
    return call_attio("DELETE", f"/v2/comments/{comment_id}")


# Webhook wrappers


@mcp.tool(description="List webhooks (GET /v2/webhooks).")
def attio_list_webhooks(limit: int = 25, offset: int = 0) -> dict[str, Any]:
    return call_attio("GET", "/v2/webhooks", params={"limit": limit, "offset": offset})


@mcp.tool(description="Get a webhook by ID (GET /v2/webhooks/{webhook_id}).")
def attio_get_webhook(webhook_id: str) -> dict[str, Any]:
    return call_attio("GET", f"/v2/webhooks/{webhook_id}")


@mcp.tool(description="Create a webhook (POST /v2/webhooks).")
def attio_create_webhook(target_url: str, subscriptions: list[dict[str, Any]]) -> dict[str, Any]:
    body = {
        "data": {
            "target_url": target_url,
            "subscriptions": subscriptions,
        }
    }
    return call_attio("POST", "/v2/webhooks", body=body)


@mcp.tool(description="Update a webhook (PATCH /v2/webhooks/{webhook_id}).")
def attio_update_webhook(
    webhook_id: str,
    target_url: str | None = None,
    subscriptions: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    data: dict[str, Any] = {}
    if target_url is not None:
        data["target_url"] = target_url
    if subscriptions is not None:
        data["subscriptions"] = subscriptions

    if not data:
        raise ValueError("Provide target_url or subscriptions to update.")

    return call_attio("PATCH", f"/v2/webhooks/{webhook_id}", body={"data": data})


@mcp.tool(description="Delete a webhook (DELETE /v2/webhooks/{webhook_id}).")
def attio_delete_webhook(webhook_id: str) -> dict[str, Any]:
    return call_attio("DELETE", f"/v2/webhooks/{webhook_id}")


# File wrappers


@mcp.tool(description="List file entries for a record (GET /v2/files).")
def attio_list_files(
    object: str,
    record_id: str,
    storage_provider: StorageProvider | None = None,
    parent_folder_id: str | None = None,
    limit: int = 50,
    cursor: str | None = None,
) -> dict[str, Any]:
    return call_attio(
        "GET",
        "/v2/files",
        params={
            "object": object,
            "record_id": record_id,
            "storage_provider": storage_provider,
            "parent_folder_id": parent_folder_id,
            "limit": limit,
            "cursor": cursor,
        },
    )


@mcp.tool(description="Get one file entry by ID (GET /v2/files/{file_id}).")
def attio_get_file(file_id: str) -> dict[str, Any]:
    return call_attio("GET", f"/v2/files/{file_id}")


@mcp.tool(description="Create a native Attio folder entry on a record (POST /v2/files).")
def attio_create_attio_folder(
    object: str,
    record_id: str,
    name: str,
    parent_folder_id: str | None = None,
) -> dict[str, Any]:
    body: dict[str, Any] = {
        "object": object,
        "record_id": record_id,
        "file_type": "folder",
        "name": name,
    }
    if parent_folder_id is not None:
        body["parent_folder_id"] = parent_folder_id

    return call_attio("POST", "/v2/files", body=body)


@mcp.tool(description="Create a connected file or folder entry (POST /v2/files).")
def attio_create_connected_file_entry(
    object: str,
    record_id: str,
    storage_provider: Literal["dropbox", "box", "google-drive", "microsoft-onedrive"],
    external_provider_file_id: str,
    file_type: Literal["connected-file", "connected-folder"] = "connected-file",
    microsoft_drive_id: str | None = None,
) -> dict[str, Any]:
    body: dict[str, Any] = {
        "object": object,
        "record_id": record_id,
        "storage_provider": storage_provider,
        "external_provider_file_id": external_provider_file_id,
        "file_type": file_type,
    }
    if microsoft_drive_id is not None:
        body["microsoft_drive_id"] = microsoft_drive_id

    return call_attio("POST", "/v2/files", body=body)


@mcp.tool(description="Delete a file entry by ID (DELETE /v2/files/{file_id}).")
def attio_delete_file(file_id: str) -> dict[str, Any]:
    return call_attio("DELETE", f"/v2/files/{file_id}")


@mcp.tool(description="Get the signed download URL for a file (GET /v2/files/{file_id}/download).")
def attio_get_file_download_url(file_id: str) -> dict[str, Any]:
    try:
        return get_client().get_redirect_location(f"/v2/files/{file_id}/download")
    except AttioAPIError as exc:
        raise RuntimeError(str(exc)) from exc


# Fallback wrapper


@mcp.tool(
    description=(
        "Fallback Attio REST caller for unsupported endpoints in this MCP. "
        "Path must start with /v2/ or /scim/v2/."
    )
)
def attio_raw_request(
    method: Literal["GET", "POST", "PUT", "PATCH", "DELETE"],
    path: str,
    params: dict[str, Any] | None = None,
    body: dict[str, Any] | None = None,
) -> dict[str, Any]:
    normalized = path.strip()
    if not normalized.startswith("/"):
        normalized = f"/{normalized}"

    if not (normalized.startswith("/v2/") or normalized.startswith("/scim/v2/")):
        raise ValueError("path must start with /v2/ or /scim/v2/")

    return call_attio(method, normalized, params=params, body=body)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    host = "0.0.0.0"

    print(f"Starting Attio Complement MCP on {host}:{port}")

    mcp.run(
        transport="http",
        host=host,
        port=port,
        stateless_http=True,
    )
