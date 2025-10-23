# MCP Documentation Insights from API Exploration

## 📊 Key Findings

### 1. Data Structure Patterns

**Every attribute has version history tracking:**
```json
{
  "active_from": "2025-03-20T08:16:45.807000000Z",
  "active_until": null,
  "created_by_actor": {"type": "system", "id": null},
  "value": "actual_data_here",
  "attribute_type": "text"
}
```

**Critical insight:** To get the actual value, you need to access the `value` field (or specific fields like `email_address`, `full_name`, etc.)

**Actor types:**
- `system` - Attio automated actions
- `workspace-member` - Human users (has workspace member ID)

### 2. Attribute Types Discovered

#### People (32 attributes):
- **text**: record_id, description, job_title, avatar_url, social links
- **personal-name**: name (has first_name, last_name, full_name)
- **email-address**: email_addresses (has email_address, email_domain, email_local_specifier)
- **phone-number**: phone_numbers
- **location**: primary_location (has locality, region, country_code, latitude, longitude)
- **record-reference**: company (points to companies object)
- **interaction**: first/last calendar/email interactions (has interaction_type, interacted_at, owner_actor)
- **number**: twitter_follower_count, strongest_connection_strength_legacy
- **select**: strongest_connection_strength, events, status_4 (has option with id and title)
- **actor-reference**: created_by, strongest_connection_user
- **timestamp**: created_at
- **checkbox**: invitation_accepted
- **status**: status_16 (has status object with id, title, is_archived)

#### Companies (31 attributes):
- **domain**: domains (unique, multiselect)
- **currency**: funding_raised_usd
- **date**: foundation_date
- Similar to people for other fields

#### List-specific attributes (from Lecker Deal Flow):
- **select**: sector, funding_round, investment_vehicle, co_investors
- **status**: deal_stage (has status_id, title)
- **currency**: target_raise, valuation, amount_invested
- **date**: date_of_investment
- **actor-reference**: owner
- **text**: blurb

### 3. Filter Operators by Attribute Type

Based on the exploration and error messages:

| Attribute Type | Supported Operators | Notes |
|---------------|-------------------|-------|
| text | $eq, $ne, $contains | Case-sensitive |
| personal-name | $eq, $ne, $contains | Searches full_name |
| email-address | $eq, $ne, $contains | Searches email_address field |
| number | $eq, $ne, $gt, $lt, $gte, $lte | Numeric comparisons |
| timestamp | $eq, $ne, $gt, $lt, $gte, $lte | ISO 8601 format |
| date | $eq, $ne, $gt, $lt, $gte, $lte | YYYY-MM-DD format |
| select | $eq, $ne | Must use option_id, not title |
| status | $eq, $ne | Must use status_id, not title |
| location | $eq, $ne | Searches locality/region |
| interaction | $eq, $ne, $gt, $lt | Filters on interacted_at |
| checkbox | $eq | true/false |
| record-reference | $eq, $ne | Uses target_record_id |

**CRITICAL:** Status and Select fields require IDs, not display names!

### 4. Real-World Query Examples

#### Example 1: Find people in London who haven't been contacted recently
```json
{
  "object_type": "people",
  "filters": {
    "primary_location": {"$contains": "London"},
    "last_interaction": {"$lt": "2024-01-01T00:00:00.000Z"}
  }
}
```

#### Example 2: Find companies with recent funding
```json
{
  "object_type": "companies",
  "filters": {
    "funding_raised_usd": {"$gt": 1000000}
  }
}
```

#### Example 3: Find people with strong connections
```json
{
  "object_type": "people",
  "filters": {
    "strongest_connection_strength_legacy": {"$gt": 0.8}
  }
}
```

#### Example 4: Find LP prospects in due diligence (requires status ID)
```json
{
  "list_identifier": "LP Fundraising",
  "filters": {
    "status": {"$eq": "c8fb3791-8a5c-4092-85b9-56ea1503db04"}
  }
}
```

### 5. Tool Selection Guidelines

#### ✅ RECOMMENDED Tools:

1. **`query_records`** - Universal data querying
   - Use for: Any object type queries with complex filters
   - Advantages: Flexible, supports all filter operators
   - Returns: Full record data with version history

2. **`list_all_lists`** - List discovery
   - Use for: Finding available lists and their parent objects
   - Returns: List names, IDs, creation dates

3. **`get_list_statuses`** - Status discovery
   - Use for: Finding status IDs for list filtering
   - Returns: All statuses with IDs and entry counts
   - **Critical:** Always use before filtering by status

4. **`get_list_entries`** - List-specific queries
   - Use for: Pipeline management, list status filtering
   - Advantages: Includes both entry values and parent record values
   - Returns: Entry-specific data + referenced record data

5. **`create_note`** - Universal note creation
   - Use for: Adding notes to any record type
   - Advantages: Works with people, companies, and any object

6. **`get_object_schema`** - Schema discovery
   - Use for: Understanding available attributes and types
   - Returns: All attributes with types and constraints

#### ⚠️ LEGACY Tools (Avoid):

1. **`search_person`** - Replaced by `query_records`
   - Why avoid: Less flexible, requires name parameter
   - Use instead: `query_records('people', filters=...)`

2. **`search_company`** - Replaced by `query_records`
   - Why avoid: Less flexible, requires name parameter
   - Use instead: `query_records('companies', filters=...)`

3. **`add_note_to_person`** - Replaced by `create_note`
   - Why avoid: Object-specific, not extensible
   - Use instead: `create_note(object_type='people', ...)`

4. **`add_note_to_company`** - Replaced by `create_note`
   - Why avoid: Object-specific, not extensible
   - Use instead: `create_note(object_type='companies', ...)`

### 6. Integration Capabilities & Limitations

#### ✅ GOOD FOR:
- **CRM Search & Discovery**: Finding people, companies, relationships
- **Note Creation**: Adding context and follow-ups to records
- **Pipeline Management**: Tracking deals, fundraising, sales stages
- **Read-only Dashboards**: Displaying CRM data in other systems
- **Data Analysis**: Extracting insights from interaction history
- **Status Tracking**: Monitoring progress through workflows

#### ❌ NOT SUITABLE FOR:
- **Creating/Updating Records**: Cannot create people or companies
- **Bulk Migration**: Limited to read operations and notes
- **File Management**: No file upload/download capabilities
- **Custom Object Creation**: Cannot define new object types
- **Deleting Records**: Read-only access to core data
- **Modifying Schemas**: Cannot change attribute definitions

#### ⚠️ PARTIAL SUPPORT:
- **List Entry Updates**: Can update list-specific attributes (like status)
- **List Membership**: Can add people to lists, but cannot remove
- **Note Management**: Can create but not edit or delete notes

### 7. Common Pitfalls & Troubleshooting

#### Pitfall 1: Using Display Names Instead of IDs
**Error:** `"Unknown status for status field constraint: due diligence"`
**Fix:** Use `get_list_statuses()` to find the status ID first
**Example:**
```
1. Call get_list_statuses("LP Fundraising")
2. Find "Due Diligence" → c8fb3791-8a5c-4092-85b9-56ea1503db04
3. Use {"status": {"$eq": "c8fb3791-8a5c-4092-85b9-56ea1503db04"}}
```

#### Pitfall 2: Wrong Filter Operator for Attribute Type
**Error:** `"invalid_filter_operator"`
**Fix:** Check attribute type and use compatible operator
**Example:** Status fields only support `$eq`, not `$contains`

#### Pitfall 3: Not Extracting Values from Version History
**Problem:** Response has nested objects with active_from/active_until
**Fix:** Access the `value` field or specific fields (email_address, full_name, etc.)
**Example:**
```json
// Raw response
{"email_addresses": {"active_from": "...", "email_address": "john@example.com"}}

// Extract value
email = record["email_addresses"]["email_address"]
```

#### Pitfall 4: Assuming Multiselect Returns Single Value
**Problem:** Multiselect fields return arrays even for single values
**Fix:** Always handle as arrays
**Example:** `email_addresses` is multiselect, so iterate through values

### 8. Performance Optimization Tips

1. **Use Limits Wisely**
   - Default limit: 50 entries
   - For quick checks: Use `limit=5` or `limit=10`
   - For full data: Increase to `limit=100` (API maximum)

2. **Narrow Your Filters**
   - More specific filters = faster responses
   - Combine multiple filters to reduce result set
   - Example: `{"primary_location": ..., "last_interaction": ...}`

3. **Use get_list_statuses Once**
   - Cache status IDs for reuse
   - Don't call for every query
   - Status IDs are stable across queries

4. **Prefer query_records Over Legacy Tools**
   - More efficient API calls
   - Single tool handles all object types
   - Better error messages

### 9. Workflow Patterns

#### Workflow 1: List Management
```
1. list_all_lists() → Discover available lists
2. get_list_statuses("List Name") → Get status IDs
3. get_list_entries("List Name", filters={...}) → Query by status
4. update_list_entry(...) → Move to next stage
```

#### Workflow 2: Prospect Research
```
1. query_records("people", filters={"primary_location": ...}) → Find locals
2. For each person:
   - Check last_interaction date
   - Review company (via record-reference)
   - Add notes for follow-up
```

#### Workflow 3: Deal Tracking
```
1. get_list_entries("Deal Flow", filters={"deal_stage": ...}) → Active deals
2. For each deal:
   - Check target_raise, valuation
   - Review owner, co_investors
   - Update deal_stage based on progress
```

### 10. MCP Best Practices for Poke

1. **Always Start with Discovery**
   - Use `list_available_objects()` to see what exists
   - Use `get_object_schema()` to understand attributes
   - Use `list_all_lists()` and `get_list_statuses()` for list queries

2. **Build Queries Incrementally**
   - Start simple: `query_records("people", limit=5)`
   - Add filters one at a time
   - Test with small limits first

3. **Handle Version History**
   - Remember all data has active_from/active_until
   - Extract specific fields (value, email_address, full_name, etc.)
   - Don't display raw version history to users

4. **Use Helpful Error Messages**
   - The MCP now provides suggestions in errors
   - Follow the "help" field for guidance
   - Check "suggestion" field for next steps

5. **Cache Discovery Data**
   - Object schemas don't change often
   - Status IDs are stable
   - List names are consistent

## Next Steps

1. Update all tool descriptions with these insights
2. Add real-world examples to each tool
3. Create usage_examples and filter_guide tools
4. Improve error messages with context-specific help

