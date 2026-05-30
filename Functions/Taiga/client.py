import requests
from typing import Any, Optional


class TaigaError(Exception):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        super().__init__(f"[{status_code}] {message}")


class TaigaClient:
    """Client for the Taiga REST API v1.

    Usage:
        client = TaigaClient("https://api.taiga.io", username="me", password="secret")
        # -- or set token directly --
        client = TaigaClient("https://api.taiga.io")
        client.set_token("my-auth-token")
    """

    def __init__(self, base_url: str, username: str = None, password: str = None):
        self.base_url = base_url.rstrip("/") + "/api/v1"
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        self.auth_token: Optional[str] = None
        self.refresh_token: Optional[str] = None

        if username and password:
            self.login(username, password)

    # ── Auth ──────────────────────────────────────────────────────────────────

    def login(self, username: str, password: str) -> dict:
        """Authenticate with username/password and store the Bearer token."""
        resp = self._request("POST", "/auth", json={
            "type": "normal",
            "username": username,
            "password": password,
        }, auth=False)
        self.auth_token = resp["auth_token"]
        self.refresh_token = resp.get("refresh")
        self.session.headers["Authorization"] = f"Bearer {self.auth_token}"
        return resp

    def refresh_auth(self) -> dict:
        """Obtain a new auth token using the stored refresh token."""
        if not self.refresh_token:
            raise TaigaError(401, "No refresh token available.")
        resp = self._request("POST", "/auth/refresh", json={"refresh": self.refresh_token}, auth=False)
        self.auth_token = resp["auth_token"]
        self.session.headers["Authorization"] = f"Bearer {self.auth_token}"
        return resp

    def set_token(self, token: str) -> None:
        """Set a pre-existing auth token directly (e.g. from an env variable)."""
        self.auth_token = token
        self.session.headers["Authorization"] = f"Bearer {token}"

    # ── HTTP helpers ──────────────────────────────────────────────────────────

    def _request(self, method: str, endpoint: str, auth: bool = True, **kwargs) -> Any:
        url = self.base_url + endpoint
        if auth and not self.auth_token:
            raise TaigaError(401, "Not authenticated — call login() or set_token() first.")
        resp = self.session.request(method, url, **kwargs)
        if resp.status_code == 204:
            return True
        if not resp.ok:
            try:
                detail = resp.json()
            except Exception:
                detail = resp.text
            raise TaigaError(resp.status_code, str(detail))
        return resp.json()

    def _get(self, endpoint: str, params: dict = None) -> Any:
        return self._request("GET", endpoint, params=params)

    def _post(self, endpoint: str, data: dict) -> Any:
        return self._request("POST", endpoint, json=data)

    def _patch(self, endpoint: str, data: dict) -> Any:
        return self._request("PATCH", endpoint, json=data)

    def _put(self, endpoint: str, data: dict) -> Any:
        return self._request("PUT", endpoint, json=data)

    def _delete(self, endpoint: str) -> bool:
        return self._request("DELETE", endpoint)

    # ── Users ─────────────────────────────────────────────────────────────────

    def get_me(self) -> dict:
        """Return the currently authenticated user's profile."""
        return self._get("/users/me")

    def get_user(self, user_id: int) -> dict:
        return self._get(f"/users/{user_id}")

    def list_users(self, project_id: int) -> list:
        return self._get("/users", params={"project": project_id})

    def update_me(self, **kwargs) -> dict:
        """Update the authenticated user's profile fields."""
        return self._patch("/users/me", kwargs)

    def change_password(self, current_password: str, new_password: str) -> bool:
        return self._post("/users/change_password", {
            "current_password": current_password,
            "password": new_password,
        })

    # ── Projects ──────────────────────────────────────────────────────────────

    def list_projects(self, member: int = None, order_by: str = None) -> list:
        params = {}
        if member is not None:
            params["member"] = member
        if order_by:
            params["order_by"] = order_by
        return self._get("/projects", params=params or None)

    def get_project(self, project_id: int) -> dict:
        return self._get(f"/projects/{project_id}")

    def get_project_by_slug(self, slug: str) -> dict:
        return self._get("/projects/by_slug", params={"slug": slug})

    def create_project(self, name: str, description: str = "", is_private: bool = False, **kwargs) -> dict:
        return self._post("/projects", {
            "name": name,
            "description": description,
            "is_private": is_private,
            **kwargs,
        })

    def update_project(self, project_id: int, version: int, **kwargs) -> dict:
        return self._patch(f"/projects/{project_id}", {"version": version, **kwargs})

    def delete_project(self, project_id: int) -> bool:
        return self._delete(f"/projects/{project_id}")

    def duplicate_project(self, project_id: int, name: str, description: str = "", is_private: bool = False) -> dict:
        return self._post(f"/projects/{project_id}/duplicate", {
            "name": name,
            "description": description,
            "is_private": is_private,
        })

    def get_project_stats(self, project_id: int) -> dict:
        return self._get(f"/projects/{project_id}/stats")

    def get_project_issues_stats(self, project_id: int) -> dict:
        return self._get(f"/projects/{project_id}/issues_stats")

    # ── Memberships ───────────────────────────────────────────────────────────

    def list_memberships(self, project_id: int) -> list:
        return self._get("/memberships", params={"project": project_id})

    def get_membership(self, membership_id: int) -> dict:
        return self._get(f"/memberships/{membership_id}")

    def create_membership(self, project_id: int, email: str, role_id: int) -> dict:
        return self._post("/memberships", {
            "project": project_id,
            "email": email,
            "role": role_id,
        })

    def update_membership(self, membership_id: int, role_id: int) -> dict:
        return self._patch(f"/memberships/{membership_id}", {"role": role_id})

    def delete_membership(self, membership_id: int) -> bool:
        return self._delete(f"/memberships/{membership_id}")

    # ── Roles ─────────────────────────────────────────────────────────────────

    def list_roles(self, project_id: int) -> list:
        return self._get("/roles", params={"project": project_id})

    def get_role(self, role_id: int) -> dict:
        return self._get(f"/roles/{role_id}")

    # ── Milestones (Sprints) ──────────────────────────────────────────────────

    def list_milestones(self, project_id: int, closed: bool = None) -> list:
        params: dict = {"project": project_id}
        if closed is not None:
            params["closed"] = closed
        return self._get("/milestones", params=params)

    def get_milestone(self, milestone_id: int) -> dict:
        return self._get(f"/milestones/{milestone_id}")

    def create_milestone(
        self,
        project_id: int,
        name: str,
        estimated_start: str,
        estimated_finish: str,
        **kwargs,
    ) -> dict:
        """estimated_start / estimated_finish must be 'YYYY-MM-DD' strings."""
        return self._post("/milestones", {
            "project": project_id,
            "name": name,
            "estimated_start": estimated_start,
            "estimated_finish": estimated_finish,
            **kwargs,
        })

    def update_milestone(self, milestone_id: int, version: int, **kwargs) -> dict:
        return self._patch(f"/milestones/{milestone_id}", {"version": version, **kwargs})

    def delete_milestone(self, milestone_id: int) -> bool:
        return self._delete(f"/milestones/{milestone_id}")

    def get_milestone_stats(self, milestone_id: int) -> dict:
        return self._get(f"/milestones/{milestone_id}/stats")

    # ── Epics ─────────────────────────────────────────────────────────────────

    def list_epics(self, project_id: int, **filters) -> list:
        return self._get("/epics", params={"project": project_id, **filters})

    def get_epic(self, epic_id: int) -> dict:
        return self._get(f"/epics/{epic_id}")

    def create_epic(self, project_id: int, subject: str, **kwargs) -> dict:
        return self._post("/epics", {"project": project_id, "subject": subject, **kwargs})

    def update_epic(self, epic_id: int, version: int, **kwargs) -> dict:
        return self._patch(f"/epics/{epic_id}", {"version": version, **kwargs})

    def delete_epic(self, epic_id: int) -> bool:
        return self._delete(f"/epics/{epic_id}")

    # ── User Stories ──────────────────────────────────────────────────────────

    def list_userstories(
        self,
        project_id: int,
        milestone: int = None,
        status: int = None,
        **filters,
    ) -> list:
        params: dict = {"project": project_id, **filters}
        if milestone is not None:
            params["milestone"] = milestone
        if status is not None:
            params["status"] = status
        return self._get("/userstories", params=params)

    def get_userstory(self, userstory_id: int) -> dict:
        return self._get(f"/userstories/{userstory_id}")

    def create_userstory(self, project_id: int, subject: str, **kwargs) -> dict:
        return self._post("/userstories", {"project": project_id, "subject": subject, **kwargs})

    def update_userstory(self, userstory_id: int, version: int, **kwargs) -> dict:
        return self._patch(f"/userstories/{userstory_id}", {"version": version, **kwargs})

    def delete_userstory(self, userstory_id: int) -> bool:
        return self._delete(f"/userstories/{userstory_id}")

    def bulk_create_userstories(
        self,
        project_id: int,
        bulk_stories: str,
        milestone_id: int = None,
        status_id: int = None,
    ) -> list:
        """bulk_stories: newline-separated story subjects."""
        data: dict = {"project_id": project_id, "bulk_stories": bulk_stories}
        if milestone_id is not None:
            data["milestone_id"] = milestone_id
        if status_id is not None:
            data["status_id"] = status_id
        return self._post("/userstories/bulk_create", data)

    # ── Tasks ─────────────────────────────────────────────────────────────────

    def list_tasks(
        self,
        project_id: int,
        milestone: int = None,
        userstory: int = None,
        **filters,
    ) -> list:
        params: dict = {"project": project_id, **filters}
        if milestone is not None:
            params["milestone"] = milestone
        if userstory is not None:
            params["user_story"] = userstory
        return self._get("/tasks", params=params)

    def get_task(self, task_id: int) -> dict:
        return self._get(f"/tasks/{task_id}")

    def create_task(self, project_id: int, subject: str, **kwargs) -> dict:
        return self._post("/tasks", {"project": project_id, "subject": subject, **kwargs})

    def update_task(self, task_id: int, version: int, **kwargs) -> dict:
        return self._patch(f"/tasks/{task_id}", {"version": version, **kwargs})

    def delete_task(self, task_id: int) -> bool:
        return self._delete(f"/tasks/{task_id}")

    def bulk_create_tasks(
        self,
        project_id: int,
        milestone_id: int,
        bulk_tasks: str,
        userstory_id: int = None,
        status_id: int = None,
    ) -> list:
        """bulk_tasks: newline-separated task subjects."""
        data: dict = {
            "project_id": project_id,
            "milestone_id": milestone_id,
            "bulk_tasks": bulk_tasks,
        }
        if userstory_id is not None:
            data["userstory_id"] = userstory_id
        if status_id is not None:
            data["status_id"] = status_id
        return self._post("/tasks/bulk_create", data)

    # ── Issues ────────────────────────────────────────────────────────────────

    def list_issues(
        self,
        project_id: int,
        status: int = None,
        priority: int = None,
        severity: int = None,
        **filters,
    ) -> list:
        params: dict = {"project": project_id, **filters}
        if status is not None:
            params["status"] = status
        if priority is not None:
            params["priority"] = priority
        if severity is not None:
            params["severity"] = severity
        return self._get("/issues", params=params)

    def get_issue(self, issue_id: int) -> dict:
        return self._get(f"/issues/{issue_id}")

    def create_issue(self, project_id: int, subject: str, **kwargs) -> dict:
        return self._post("/issues", {"project": project_id, "subject": subject, **kwargs})

    def update_issue(self, issue_id: int, version: int, **kwargs) -> dict:
        return self._patch(f"/issues/{issue_id}", {"version": version, **kwargs})

    def delete_issue(self, issue_id: int) -> bool:
        return self._delete(f"/issues/{issue_id}")

    def bulk_create_issues(self, project_id: int, bulk_issues: list) -> list:
        """bulk_issues: list of dicts with at least a 'subject' key."""
        return self._post("/issues/bulk_create", {
            "project_id": project_id,
            "bulk_issues": bulk_issues,
        })

    # ── Wiki ──────────────────────────────────────────────────────────────────

    def list_wiki_pages(self, project_id: int) -> list:
        return self._get("/wiki", params={"project": project_id})

    def get_wiki_page(self, page_id: int) -> dict:
        return self._get(f"/wiki/{page_id}")

    def get_wiki_page_by_slug(self, project_id: int, slug: str) -> dict:
        return self._get("/wiki/by_slug", params={"project": project_id, "slug": slug})

    def create_wiki_page(self, project_id: int, slug: str, content: str) -> dict:
        return self._post("/wiki", {"project": project_id, "slug": slug, "content": content})

    def update_wiki_page(self, page_id: int, version: int, content: str, **kwargs) -> dict:
        return self._patch(f"/wiki/{page_id}", {"version": version, "content": content, **kwargs})

    def delete_wiki_page(self, page_id: int) -> bool:
        return self._delete(f"/wiki/{page_id}")

    # ── History & Comments ────────────────────────────────────────────────────

    def get_history(self, resource_type: str, resource_id: int) -> list:
        """resource_type: 'userstory' | 'task' | 'issue' | 'epic' | 'wiki'."""
        return self._get(f"/history/{resource_type}/{resource_id}")

    def add_comment(self, resource_type: str, resource_id: int, comment: str, version: int) -> dict:
        """Attach a comment to any resource by patching it with a comment field."""
        endpoint_map = {
            "userstory": f"/userstories/{resource_id}",
            "task": f"/tasks/{resource_id}",
            "issue": f"/issues/{resource_id}",
            "epic": f"/epics/{resource_id}",
            "wiki": f"/wiki/{resource_id}",
        }
        endpoint = endpoint_map.get(resource_type)
        if not endpoint:
            raise ValueError(f"Unknown resource_type '{resource_type}'. "
                             "Use: userstory, task, issue, epic, wiki.")
        return self._patch(endpoint, {"comment": comment, "version": version})

    def delete_comment(self, resource_type: str, resource_id: int, comment_id: str) -> bool:
        return self._post(
            f"/history/{resource_type}/{resource_id}/delete_comment",
            {"id": comment_id},
        )

    # ── Search ────────────────────────────────────────────────────────────────

    def search(self, project_id: int, query: str) -> dict:
        """Full-text search across user stories, tasks, issues, and wiki pages."""
        return self._get("/search", params={"project": project_id, "text": query})

    # ── Resolve ───────────────────────────────────────────────────────────────

    def resolve(
        self,
        project_slug: str,
        us: int = None,
        task: int = None,
        issue: int = None,
        milestone: int = None,
    ) -> dict:
        """Convert a project slug + ref numbers into their API IDs."""
        params: dict = {"project": project_slug}
        if us is not None:
            params["us"] = us
        if task is not None:
            params["task"] = task
        if issue is not None:
            params["issue"] = issue
        if milestone is not None:
            params["milestone"] = milestone
        return self._get("/resolver", params=params)

    # ── Statuses & Metadata ───────────────────────────────────────────────────

    def list_userstory_statuses(self, project_id: int) -> list:
        return self._get("/userstory-statuses", params={"project": project_id})

    def list_task_statuses(self, project_id: int) -> list:
        return self._get("/task-statuses", params={"project": project_id})

    def list_issue_statuses(self, project_id: int) -> list:
        return self._get("/issue-statuses", params={"project": project_id})

    def list_epic_statuses(self, project_id: int) -> list:
        return self._get("/epic-statuses", params={"project": project_id})

    def list_issue_types(self, project_id: int) -> list:
        return self._get("/issue-types", params={"project": project_id})

    def list_priorities(self, project_id: int) -> list:
        return self._get("/priorities", params={"project": project_id})

    def list_severities(self, project_id: int) -> list:
        return self._get("/severities", params={"project": project_id})

    def list_points(self, project_id: int) -> list:
        return self._get("/points", params={"project": project_id})

    # ── Webhooks ──────────────────────────────────────────────────────────────

    def list_webhooks(self, project_id: int) -> list:
        return self._get("/webhooks", params={"project": project_id})

    def get_webhook(self, webhook_id: int) -> dict:
        return self._get(f"/webhooks/{webhook_id}")

    def create_webhook(self, project_id: int, name: str, url: str, key: str) -> dict:
        return self._post("/webhooks", {
            "project": project_id,
            "name": name,
            "url": url,
            "key": key,
        })

    def update_webhook(self, webhook_id: int, **kwargs) -> dict:
        return self._patch(f"/webhooks/{webhook_id}", kwargs)

    def delete_webhook(self, webhook_id: int) -> bool:
        return self._delete(f"/webhooks/{webhook_id}")
