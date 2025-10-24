# Poke-Attio MCP Server

A comprehensive [FastMCP](https://github.com/jlowin/fastmcp) server that integrates Attio CRM with Poke AI assistant, enabling natural language interactions with your CRM data through intelligent, self-documenting tools.

## 🌟 Features

### **Self-Documenting & Self-Guiding**
- 📚 **Built-in documentation tools** - Poke can discover usage patterns on-the-fly
- 🎯 **Workflow examples** - Real-world patterns for common tasks
- 🔍 **Filter syntax guide** - Comprehensive reference for all query types
- 💡 **Smart error messages** - Helpful suggestions when things go wrong

### **Universal Data Access**
- 🔍 **Query any object** - People, companies, and custom objects
- 📊 **Flexible filtering** - 13+ attribute types with full operator support
- 📋 **List management** - Pipeline tracking with status-based workflows
- 🏷️ **Status discovery** - Automatic status ID resolution

### **Writing Capabilities**
- 📝 **Create notes** - Attach context to any record
- ✏️ **Update list entries** - Change statuses and attributes
- ➕ **Add to lists** - Bulk list membership management

### **Developer Experience**
- 🚀 **Easy deployment** to Render with one click
- 🔐 **Secure API key** management via environment variables
- ⚡ **Lightning fast** documentation tools (9-11ms response time)
- 🧪 **Comprehensive testing** - Integration test suite included

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/fiehtle/poke-mcp-server-template)

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Attio account with API access
- GitHub account (for deployment)

### Local Development

1. **Clone and setup:**

```bash
git clone <your-repo-url>
cd poke-attio-mcp-server
```

2. **Create environment:**

```bash
conda create -n mcp-server python=3.13
conda activate mcp-server
pip install -r requirements.txt
```

3. **Get your Attio API key:**
   - Go to https://app.attio.com/settings/developers
   - Click "+ New access token"
   - Give it a name and select scopes (recommend: full read-write)
   - Copy the API key

4. **Set environment variable:**

```bash
export ATTIO_API_KEY=your_api_key_here
```

> **Security Note:** Never commit API keys! Use environment variables only.

5. **Start the server:**

```bash
python src/server.py
```

6. **Test with MCP Inspector:**

```bash
npx @modelcontextprotocol/inspector
```

Open http://localhost:3000 and connect to `http://localhost:8000/mcp` using "Streamable HTTP" transport.

## 📖 Available Tools

### **Documentation & Discovery**

#### `get_usage_examples()`
Get real-world workflow patterns and examples.

**Returns:**
- List management workflows (4-step process)
- Prospect research patterns
- Deal tracking examples
- Common filter templates
- Pro tips for effective querying

#### `get_filter_guide()`
Comprehensive filter syntax reference.

**Returns:**
- Filter operators by attribute type (13 types)
- Real-world filter examples
- Common pitfalls and solutions
- Performance optimization tips

#### `get_server_info()`
Server status and tool overview with categorization.

**Returns:**
- Available tools by category
- Quick start guide
- Tool selection guidelines
- Integration capabilities

#### `list_available_objects()`
Discover what object types exist in your workspace.

**Example:** "What objects are in Attio?"

#### `get_object_schema(object_type)`
See all attributes and types for an object.

**Example:** "What fields does a person have?"

### **Querying & Search**

#### `query_records(object_type, filters, limit)`
Universal tool for querying ANY object with flexible filters.

**Examples:**
```python
# Find people in London
query_records("people", {"primary_location": {"$contains": "London"}}, limit=20)

# Find companies with funding > $5M
query_records("companies", {"funding_raised_usd": {"$gt": 5000000}}, limit=10)

# Find people with strong connections
query_records("people", {"strongest_connection_strength_legacy": {"$gt": 0.8}})
```

**Supported filters:**
- Text: `$eq`, `$ne`, `$contains`
- Numbers: `$eq`, `$ne`, `$gt`, `$lt`, `$gte`, `$lte`
- Dates: `$eq`, `$ne`, `$gt`, `$lt`, `$gte`, `$lte`
- Status/Select: `$eq`, `$ne` (requires IDs!)
- Location: `$eq`, `$ne`, `$contains`
- And more...

#### `list_all_lists()`
List all available lists in your workspace.

**Returns:** List names, IDs, parent objects, creation dates

#### `get_list_statuses(list_identifier)`
Get all available statuses for a list with their IDs.

**Critical for:** Status-based filtering (must use IDs, not display names!)

**Example:**
```python
# Step 1: Get status IDs
get_list_statuses("LP Fundraising")
# Returns: {"Due Diligence": "c8fb3791-...", "Committed": "530b05f6-...", ...}

# Step 2: Use status ID in filter
get_list_entries("LP Fundraising", {"status": {"$eq": "c8fb3791-..."}})
```

#### `get_list_entries(list_identifier, filters, limit)`
Query list entries with list-specific attributes.

**Returns:** Entry values + parent record values

**Example:** "Show me all deals in due diligence stage"

### **Writing & Updates**

#### `create_note(object_type, record_identifier, title, content)`
Add notes to ANY record type (people, companies, etc.).

**Example:** "Add a note to John's record about our meeting"

#### `update_list_entry(list_identifier, person_identifier, attribute_updates)`
Update list entry attributes like status.

**Example:** "Move Sarah to 'Next to Close' status in LP Fundraising"

#### `add_to_list(list_identifier, person_identifiers, entry_attributes)`
Add people to lists (supports bulk operations).

**Example:** "Add these 5 people to the London list"

### **Legacy Tools (Use New Alternatives)**

- ~~`search_person`~~ → Use `query_records("people", ...)`
- ~~`search_company`~~ → Use `query_records("companies", ...)`
- ~~`add_note_to_person`~~ → Use `create_note(object_type="people", ...)`
- ~~`add_note_to_company`~~ → Use `create_note(object_type="companies", ...)`

## 🎯 Common Workflows

### 1. **List Management**
```
1. list_all_lists() → Discover available lists
2. get_list_statuses("List Name") → Get status IDs
3. get_list_entries("List Name", filters={...}) → Query by status
4. update_list_entry(...) → Move to next stage
```

### 2. **Prospect Research**
```
"Find people in London who haven't been contacted recently"
→ query_records("people", {
    "primary_location": {"$contains": "London"},
    "last_interaction": {"$lt": "2024-01-01T00:00:00.000Z"}
  })
```

### 3. **Deal Tracking**
```
1. get_list_entries("Deal Flow") → Get all deals
2. get_list_statuses("Deal Flow") → Find status IDs
3. get_list_entries("Deal Flow", {"deal_stage": {"$eq": "status_id"}}) → Filter by stage
```

## 🔧 Deployment to Render

### Method 1: One-Click Deploy

Click the "Deploy to Render" button above and follow the prompts.

### Method 2: Manual Deploy

1. **Push to GitHub:**

```bash
git add .
git commit -m "Deploy Attio MCP server"
git push origin main
```

2. **Deploy on Render:**
   - Go to [render.com](https://render.com)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Render will detect `render.yaml` automatically
   - Click "Apply"

3. **⚠️ CRITICAL: Add API Key to Render:**
   - Go to your service dashboard
   - Click "Environment" tab
   - Add environment variable:
     - **Key**: `ATTIO_API_KEY`
     - **Value**: `your_actual_api_key_here` (get from Attio settings)
   - Click "Save Changes"
   - Service will automatically redeploy

4. **Get your MCP endpoint:**

Your server will be available at:
```
https://your-service-name.onrender.com/mcp
```

**Note:** The `/mcp` suffix is required!

## 🔗 Connect to Poke

1. **Go to Poke settings:**
   - Visit [poke.com/settings/connections](https://poke.com/settings/connections)
   
2. **Add new MCP connection:**
   - Click "Add Connection"
   - **Name**: `Attio CRM`
   - **URL**: `https://your-service-name.onrender.com/mcp`
   - **Transport**: Streamable HTTP
   - Save

3. **Test the connection:**

Try asking Poke:
```
"What tools are available in Attio?"
"Show me usage examples for Attio"
"Find people in London in my Attio"
"What's in my LP Fundraising list?"
"Add a note to John's record about our call"
```

### Troubleshooting

**Poke isn't using the MCP:**
- Try: `clearhistory` to reset conversation
- Test explicitly: "Use the Attio CRM integration to list all lists"
- Check: Make sure URL ends with `/mcp`

**Authentication errors:**
- Verify API key is set in Render environment variables
- Check Render logs for specific error messages
- Regenerate API key in Attio if needed

**Filter errors:**
- Use `get_list_statuses()` to find status IDs (not display names!)
- Use `get_filter_guide()` for operator reference
- Check `get_usage_examples()` for patterns

## 📚 Documentation

The MCP server is **self-documenting**! Poke can call these tools to learn:

- `get_usage_examples()` - Workflow patterns and real examples
- `get_filter_guide()` - Complete filter syntax reference
- `get_server_info()` - Tool overview and capabilities

### Additional Resources

- **`DOCUMENTATION_INSIGHTS.md`** - Deep dive into API exploration findings
- **`ENHANCEMENT_SUMMARY.md`** - Summary of enhancements and features
- **`instructions.md`** - Project goals and development notes

## 🔐 Security

**Critical Security Practices:**

1. **Never commit API keys!**
   - Use environment variables only
   - `.env` is in `.gitignore` for local dev
   - Set `ATTIO_API_KEY` in Render environment

2. **Check git history:**
   ```bash
   git log -p | grep -i "api.*key"
   ```

3. **If API key is exposed:**
   - Revoke it immediately in Attio settings
   - Generate a new key
   - Update Render environment variable
   - Consider rewriting git history if public

4. **Access control:**
   - API key grants access to your entire Attio workspace
   - Anyone with your MCP URL + API key can access your data
   - Keep MCP endpoint URL private

## 🧪 Testing

Run the integration test suite:

```bash
python test_enhanced_documentation.py
```

**Tests include:**
- New documentation tools functionality
- Enhanced server info structure
- Existing functionality (regression)
- Enhanced error messages
- Performance benchmarks

## 🛠️ Development

### Adding New Tools

Decorate functions with `@mcp.tool` in `src/server.py`:

```python
@mcp.tool(description="Your tool description")
def your_tool_name(param: str, api_key: str = None) -> dict:
    """
    Tool documentation
    
    Args:
        param: Parameter description
        api_key: Optional API key (falls back to environment variable)
    
    Returns:
        Dictionary with results
    """
    # Use make_attio_request helper
    result = make_attio_request("/endpoint", api_key=api_key)
    
    return {
        "success": True,
        "data": result.get("data", []),
        "message": "Success message"
    }
```

### Helper Functions

- `make_attio_request(endpoint, method, data, api_key)` - Makes authenticated Attio API calls
- `_get_list_entries_internal(...)` - Internal list querying logic

## 📊 Integration Capabilities

### ✅ Good For:
- CRM search and discovery
- Note creation and context tracking
- Pipeline and deal tracking
- Read-only dashboards
- Data analysis and reporting
- Status tracking and workflow management

### ❌ Not Suitable For:
- Creating/updating core records (people, companies)
- Bulk data migration
- File management
- Custom object creation
- Deleting records

### ⚠️ Partial Support:
- List entry updates (can update list-specific attributes)
- List membership (can add, cannot remove)
- Note management (can create, cannot edit/delete)

## 🤝 Contributing

Issues and pull requests are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Test your changes
4. Submit a PR with clear description

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- Built with [FastMCP](https://github.com/jlowin/fastmcp)
- Integrates with [Attio CRM](https://attio.com)
- Designed for [Poke AI](https://poke.com)

---

**Made with ❤️ for seamless CRM interactions through natural language**
