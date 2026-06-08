# Access permissions module

The **Permissions** plugin manages HTTP route access in osysHome: view default restrictions from code, add per-user and per-role overrides, and reset custom rules.

| | |
|---|---|
| **Admin UI** | [/admin/Permissions](/admin/Permissions) |
| **Category** | System |
| **Version** | 0.1 |

---

## Overview

Each route (endpoint) can have:

1. **Default access** — roles required by the route handler in code (`required_roles` decorator). Shown as a blue badge. If nothing is set in code, the route is **No restrictions**.
2. **Additional rules** — optional overrides stored in the `_permissions` object. They can allow or deny specific users and roles for each HTTP method (GET, POST, PUT, DELETE).

Additional rules are applied on top of default access. A user or role cannot be both allowed and denied at the same time for the same method.

---

## Admin interface

### Toolbar

| Element | Purpose |
|---------|---------|
| **Search** | Find modules by name/title, or endpoints by name/URL |
| **Only with rules** | Show modules/routes that have custom permissions |
| **Expand / Collapse all** | Open or close all module cards |
| **Stats** | Count of modules, routes, and items with custom rules |

### Module card

- Click the header to expand/collapse the route list.
- **Configure module** — edit permissions for the whole blueprint (all methods at module level).
- **Reset** (↺) — remove custom module rules (visible when rules exist).

Each route row shows method cards with **Default access** and, if configured, additional allow/deny lines for users and roles.

### Edit dialog

For each HTTP method you can set:

| Field | Meaning |
|-------|---------|
| **Access for users** | Only these users may access (in addition to default access logic) |
| **Deny for users** | These users are blocked |
| **Access for roles** | Only these roles may access |
| **Deny for roles** | These roles are blocked |

**All users** (`*`) means every user. **Any role** (`*`) means every role.

**Save** writes rules to storage. **Reset rules** clears all additional rules for the current module or endpoint.

---

## Storage format

Permissions are stored as properties on the `_permissions` system object:

| Key | Scope |
|-----|--------|
| `_permissions.blueprint:ModuleName` | Whole module (blueprint) |
| `_permissions.ModuleName:endpoint_name` | Single endpoint |

Value is a JSON object per HTTP method:

```json
{
  "get": {
    "access_users": ["operator"],
    "denied_users": ["test"],
    "access_roles": ["admin"],
    "denied_roles": ["guest"]
  }
}
```

Empty object `{}` means no additional rules (only default access applies).

---

## API

### `GET /Permissions/list`

Returns all routes grouped by blueprint/module. Requires administrator role.

Each group includes:

- `title`, `category` — module metadata
- `permissions` — blueprint-level custom rules
- `endpoints[]` — routes with `methods[]`, each containing `required_roles`, `permissions`, `url`

### Saving via property API

```
POST /api/property/_permissions.{key}
Content-Type: application/json

{
  "data": { "get": { "access_users": ["user1"] } },
  "source": "Permissions"
}
```

Use colon (`:`) instead of dot in endpoint keys, e.g. `MCPServer:mcp_endpoint`.

---

## Roles

Built-in roles used in the UI and in `required_roles`:

| Role | Name |
|------|------|
| Any role | `*` |
| Guest | `guest` |
| User | `user` |
| Editor | `editor` |
| Administrator | `admin` |

---

## Related files

- `plugins/Permissions/__init__.py` — plugin class and list API
- `plugins/Permissions/templates/permissions.html` — admin UI
- `plugins/Permissions/translations/` — UI localization (`en.json`, `ru.json`)
