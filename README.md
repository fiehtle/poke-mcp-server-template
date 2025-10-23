# Poke-Attio MCP Server

A [FastMCP](https://github.com/jlowin/fastmcp) server that integrates Attio CRM with Poke AI assistant, enabling natural language interactions with your CRM data.

**Features:**
- 🔍 Search for people/contacts by name
- 🏢 Search for companies
- 📊 Get server and workspace information
- 🚀 Easy deployment to Render
- 🔐 Secure API key management

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/fiehtle/poke-mcp-server-template)

## Local Development

### Setup

1. Fork the repo, then clone it:

```bash
git clone <your-repo-url>
cd poke-attio-mcp-server
```

2. Create and activate environment:

```bash
conda create -n mcp-server python=3.13
conda activate mcp-server
pip install -r requirements.txt
```

3. Create `.env` file from template:

```bash
cp .env.example .env
```

4. Get your Attio API key:
   - Go to https://app.attio.com/settings/developers
   - Click "+ New access token"
   - Give it a name and select required scopes (recommend: all read-write permissions)
   - Copy the API key

5. Add your API key to `.env`:

```bash
ATTIO_API_KEY=your_api_key_here
ENVIRONMENT=development
```

### Test Locally

Start the server:

```bash
python src/server.py
```

In another terminal, test with MCP Inspector:

```bash
npx @modelcontextprotocol/inspector
```

Open http://localhost:3000 and connect to `http://localhost:8000/mcp` using "Streamable HTTP" transport (NOTE THE `/mcp`!).

**Try these tools:**
- `get_server_info` - Check connection to Attio
- `search_person` - Search for someone (e.g., name: "John")
- `search_company` - Search for a company

## Deployment to Render

### Quick Deploy

1. **Push your code to GitHub** (make sure `.env` is NOT committed!)

```bash
git add .
git commit -m "Update to Attio CRM integration"
git push origin main
```

2. **Deploy to Render:**
   - Go to [render.com](https://render.com)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Render will detect `render.yaml` automatically
   - Click "Apply"

3. **Add API Key to Render:**
   - Go to your service dashboard
   - Click "Environment" tab
   - Add environment variable:
     - **Key**: `ATTIO_API_KEY`
     - **Value**: `4405c2e2538fcbd3dc3984ec475d240dea0fdca1b659e0afc92263cdb610f2e3`
   - Click "Save Changes"
   - Service will automatically redeploy

4. **Get your MCP endpoint:**

Your server will be available at:
```
https://poke-attio-mcp.onrender.com/mcp
```
(Replace `poke-attio-mcp` with your actual service name)

**Note:** The `/mcp` suffix is important!

## Connect to Poke

1. **Go to Poke settings:**
   - Visit [poke.com/settings/connections](https://poke.com/settings/connections)
   
2. **Add new MCP connection:**
   - Click "Add Connection"
   - **Name**: `Attio CRM` (or whatever you prefer)
   - **URL**: `https://your-service-name.onrender.com/mcp`
   - **Transport**: Streamable HTTP
   - Save

3. **Test the connection:**

Try asking Poke:
```
"What tools are available in Attio CRM?"
"Search for a person named [name] in Attio"
"What's the email of [name]?"
```

**Troubleshooting:**
- If Poke doesn't call your MCP, try: `clearhistory` to delete message history
- Test explicitly: `Tell the subagent to use the "Attio CRM" integration's "search_person" tool`
- Check Render logs if the server isn't responding


## Available Tools

### `search_person`
Search for a person/contact by name.

**Example:** "What's the email of Mehdi Ghissassi?"

### `search_company`
Search for a company by name.

**Example:** "Show me details about Acme Corp"

### `get_server_info`
Get server information and verify Attio connection.

## Adding More Tools

Add more tools by decorating functions with `@mcp.tool` in `src/server.py`:

```python
@mcp.tool(description="Your tool description")
def your_tool_name(param: str) -> dict:
    """
    Your tool documentation
    
    Args:
        param: Parameter description
    
    Returns:
        Dictionary with results
    """
    # Your implementation
    return {"success": True}
```

See `instructions.md` for planned features like adding notes, managing deals, etc.

## Security Note

**Never commit your `.env` file or expose your API key!**
- `.env` is already in `.gitignore`
- Set API key as environment variable in Render
- Use `.env.example` as template for others
# Trigger redeploy Thu Oct 23 14:36:44 CEST 2025
# Trigger redeploy - Thu Oct 23 15:07:43 CEST 2025
