"""
Security and Row-Level Security (RLS) Enforcement Engine
Evaluates caller identity, role, scope, and requested domains against the permission matrix.
Injects physical WHERE filters into queries and rejects cross-territory leaks.
"""
from typing import Dict, List, Optional, Any, Set
import duckdb

class SecurityEngine:
    def __init__(self, con: duckdb.DuckDBPyConnection):
        self.con = con
        self._load_metadata()

    def _load_metadata(self):
        # Cache territories, sub-regions, regions
        t_rows = self.con.execute("SELECT territory_code, sub_region, region_code FROM territories").fetchall()
        self.territory_to_subregion = {r[0]: r[1] for r in t_rows}
        self.territory_to_region = {r[0]: r[2] for r in t_rows}
        
        # Sub-region mapping to territories
        self.subregion_to_territories: Dict[str, List[str]] = {}
        self.region_to_territories: Dict[str, List[str]] = {}
        for t_code, sub_reg, reg_code in t_rows:
            self.subregion_to_territories.setdefault(sub_reg, []).append(t_code)
            self.region_to_territories.setdefault(reg_code, []).append(t_code)

        # Users cache
        u_rows = self.con.execute("SELECT user_id, role, region, sub_region, territory_code FROM users_and_roles").fetchall()
        self.users = {
            r[0]: {
                "user_id": r[0],
                "role": r[1],
                "region": r[2],
                "sub_region": r[3],
                "territory_code": r[4]
            }
            for r in u_rows
        }

        # Permissions cache: (role, domain) -> access_scope
        p_rows = self.con.execute("SELECT role, data_domain, access_scope FROM permission_matrix").fetchall()
        self.permissions: Dict[str, Dict[str, str]] = {}
        for role, domain, scope in p_rows:
            self.permissions.setdefault(role, {})[domain] = scope

    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        return self.users.get(user_id)

    def get_allowed_territories(self, user_id: str, domain: str) -> Optional[List[str]]:
        """
        Returns:
            - None if user has global unrestricted access
            - List of allowed territory codes
            - Empty list [] if access denied
        """
        user = self.get_user(user_id)
        if not user:
            return []

        role = user["role"]
        role_perms = self.permissions.get(role, {})
        scope = role_perms.get(domain, role_perms.get("*", "None"))

        if scope == "Global":
            return None  # All territories permitted
        elif scope == "Own region":
            reg = user["region"]
            return self.region_to_territories.get(reg, [])
        elif scope == "Own sub-region":
            sub_reg = user["sub_region"]
            return self.subregion_to_territories.get(sub_reg, [])
        elif scope == "Own territory":
            t_code = user["territory_code"]
            return [t_code] if t_code else []
        elif scope == "Assigned distributors":
            # For Key Account Manager
            d_rows = self.con.execute(
                "SELECT territory_code FROM distributors WHERE kam_user_id = ?", [user_id]
            ).fetchall()
            return list(set(r[0] for r in d_rows))
        else:
            return []

    def check_access(self, user_id: str, domain: str, requested_territory: Optional[str] = None, table_alias: str = "") -> Dict[str, Any]:
        """
        Validates whether user has access to a domain and specifically requested territory.
        Returns validation status, error/warning message, and SQL injection clause.
        """
        user = self.get_user(user_id)
        if not user:
            return {
                "allowed": False,
                "reason": f"Unknown user ID '{user_id}'."
            }

        allowed_territories = self.get_allowed_territories(user_id, domain)

        # Check domain permission
        if allowed_territories == []:
            return {
                "allowed": False,
                "reason": f"Role '{user['role']}' does not have access to domain '{domain}'."
            }

        # Check requested territory against scope
        if requested_territory:
            if allowed_territories is not None and requested_territory not in allowed_territories:
                return {
                    "allowed": False,
                    "reason": (
                        f"Access Denied: User '{user_id}' ({user['role']}) is scoped to "
                        f"{user.get('territory_code') or user.get('sub_region') or user.get('region')} "
                        f"and cannot query territory '{requested_territory}'."
                    )
                }

        # Build SQL RLS filter
        if allowed_territories is None:
            rls_sql = "1=1"
        else:
            formatted_t = ", ".join(f"'{t}'" for t in allowed_territories)
            prefix = f"{table_alias}." if table_alias else ""
            rls_sql = f"{prefix}territory_code IN ({formatted_t})"

        return {
            "allowed": True,
            "user": user,
            "scope": "Global" if allowed_territories is None else allowed_territories,
            "rls_sql": rls_sql
        }
