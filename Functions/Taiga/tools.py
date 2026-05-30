from typing import Optional
from .client import TaigaClient


def register_tools(mcp, client: TaigaClient) -> None:
    """Register all Taiga MCP tools against the given FastMCP instance."""

    # ── Auth / Me ─────────────────────────────────────────────────────────────

    @mcp.tool()
    def taiga_get_me() -> dict:
        """Return the currently authenticated Taiga user's profile."""
        return client.get_me()

    # ── Projects ──────────────────────────────────────────────────────────────

    @mcp.tool()
    def taiga_list_projects(member_id: Optional[int] = None) -> list:
        """List Taiga projects. Optionally filter by member user ID."""
        return client.list_projects(member=member_id)

    @mcp.tool()
    def taiga_get_project(project_id: int) -> dict:
        """Get full details of a Taiga project by its ID."""
        return client.get_project(project_id)

    @mcp.tool()
    def taiga_get_project_by_slug(slug: str) -> dict:
        """Get a Taiga project by its URL slug (e.g. 'my-project')."""
        return client.get_project_by_slug(slug)

    @mcp.tool()
    def taiga_create_project(name: str, description: str = "", is_private: bool = False) -> dict:
        """Create a new Taiga project."""
        return client.create_project(name=name, description=description, is_private=is_private)

    # ── Milestones (Sprints) ──────────────────────────────────────────────────

    @mcp.tool()
    def taiga_list_milestones(project_id: int, closed: Optional[bool] = None) -> list:
        """List milestones (sprints) for a project. Pass closed=True/False to filter."""
        return client.list_milestones(project_id, closed=closed)

    @mcp.tool()
    def taiga_get_milestone(milestone_id: int) -> dict:
        """Get a single milestone (sprint) by ID."""
        return client.get_milestone(milestone_id)

    @mcp.tool()
    def taiga_create_milestone(
        project_id: int,
        name: str,
        estimated_start: str,
        estimated_finish: str,
    ) -> dict:
        """Create a milestone (sprint). Dates must be 'YYYY-MM-DD'."""
        return client.create_milestone(
            project_id=project_id,
            name=name,
            estimated_start=estimated_start,
            estimated_finish=estimated_finish,
        )

    # ── User Stories ──────────────────────────────────────────────────────────

    @mcp.tool()
    def taiga_list_userstories(
        project_id: int,
        milestone_id: Optional[int] = None,
        status_id: Optional[int] = None,
    ) -> list:
        """List user stories in a project. Optionally filter by milestone or status ID."""
        return client.list_userstories(project_id, milestone=milestone_id, status=status_id)

    @mcp.tool()
    def taiga_get_userstory(userstory_id: int) -> dict:
        """Get a single user story by ID."""
        return client.get_userstory(userstory_id)

    @mcp.tool()
    def taiga_create_userstory(
        project_id: int,
        subject: str,
        description: str = "",
        milestone_id: Optional[int] = None,
        status_id: Optional[int] = None,
    ) -> dict:
        """Create a user story in a project."""
        kwargs = {}
        if description:
            kwargs["description"] = description
        if milestone_id is not None:
            kwargs["milestone"] = milestone_id
        if status_id is not None:
            kwargs["status"] = status_id
        return client.create_userstory(project_id=project_id, subject=subject, **kwargs)

    @mcp.tool()
    def taiga_update_userstory(
        userstory_id: int,
        version: int,
        subject: Optional[str] = None,
        description: Optional[str] = None,
        status_id: Optional[int] = None,
        milestone_id: Optional[int] = None,
    ) -> dict:
        """Update fields on an existing user story. version is required (from the current object)."""
        kwargs = {}
        if subject is not None:
            kwargs["subject"] = subject
        if description is not None:
            kwargs["description"] = description
        if status_id is not None:
            kwargs["status"] = status_id
        if milestone_id is not None:
            kwargs["milestone"] = milestone_id
        return client.update_userstory(userstory_id, version=version, **kwargs)

    # ── Tasks ─────────────────────────────────────────────────────────────────

    @mcp.tool()
    def taiga_list_tasks(
        project_id: int,
        milestone_id: Optional[int] = None,
        userstory_id: Optional[int] = None,
    ) -> list:
        """List tasks in a project. Optionally filter by milestone or user story ID."""
        return client.list_tasks(project_id, milestone=milestone_id, userstory=userstory_id)

    @mcp.tool()
    def taiga_get_task(task_id: int) -> dict:
        """Get a single task by ID."""
        return client.get_task(task_id)

    @mcp.tool()
    def taiga_create_task(
        project_id: int,
        subject: str,
        userstory_id: Optional[int] = None,
        milestone_id: Optional[int] = None,
        status_id: Optional[int] = None,
    ) -> dict:
        """Create a task in a project."""
        kwargs = {}
        if userstory_id is not None:
            kwargs["user_story"] = userstory_id
        if milestone_id is not None:
            kwargs["milestone"] = milestone_id
        if status_id is not None:
            kwargs["status"] = status_id
        return client.create_task(project_id=project_id, subject=subject, **kwargs)

    @mcp.tool()
    def taiga_update_task(
        task_id: int,
        version: int,
        subject: Optional[str] = None,
        status_id: Optional[int] = None,
        assigned_to: Optional[int] = None,
    ) -> dict:
        """Update fields on an existing task. version is required (from the current object)."""
        kwargs = {}
        if subject is not None:
            kwargs["subject"] = subject
        if status_id is not None:
            kwargs["status"] = status_id
        if assigned_to is not None:
            kwargs["assigned_to"] = assigned_to
        return client.update_task(task_id, version=version, **kwargs)

    # ── Issues ────────────────────────────────────────────────────────────────

    @mcp.tool()
    def taiga_list_issues(
        project_id: int,
        status_id: Optional[int] = None,
        priority_id: Optional[int] = None,
    ) -> list:
        """List issues in a project. Optionally filter by status or priority ID."""
        return client.list_issues(project_id, status=status_id, priority=priority_id)

    @mcp.tool()
    def taiga_get_issue(issue_id: int) -> dict:
        """Get a single issue by ID."""
        return client.get_issue(issue_id)

    @mcp.tool()
    def taiga_create_issue(
        project_id: int,
        subject: str,
        description: str = "",
        priority_id: Optional[int] = None,
        severity_id: Optional[int] = None,
        type_id: Optional[int] = None,
    ) -> dict:
        """Create an issue in a project."""
        kwargs = {}
        if description:
            kwargs["description"] = description
        if priority_id is not None:
            kwargs["priority"] = priority_id
        if severity_id is not None:
            kwargs["severity"] = severity_id
        if type_id is not None:
            kwargs["type"] = type_id
        return client.create_issue(project_id=project_id, subject=subject, **kwargs)

    @mcp.tool()
    def taiga_update_issue(
        issue_id: int,
        version: int,
        subject: Optional[str] = None,
        status_id: Optional[int] = None,
        priority_id: Optional[int] = None,
    ) -> dict:
        """Update fields on an existing issue. version is required (from the current object)."""
        kwargs = {}
        if subject is not None:
            kwargs["subject"] = subject
        if status_id is not None:
            kwargs["status"] = status_id
        if priority_id is not None:
            kwargs["priority"] = priority_id
        return client.update_issue(issue_id, version=version, **kwargs)

    # ── Comments ──────────────────────────────────────────────────────────────

    @mcp.tool()
    def taiga_add_comment(
        resource_type: str,
        resource_id: int,
        comment: str,
        version: int,
    ) -> dict:
        """Add a comment to a resource. resource_type: 'userstory' | 'task' | 'issue' | 'epic' | 'wiki'."""
        return client.add_comment(resource_type, resource_id, comment, version)

    @mcp.tool()
    def taiga_get_history(resource_type: str, resource_id: int) -> list:
        """Get the activity history and comments for a resource.
        resource_type: 'userstory' | 'task' | 'issue' | 'epic' | 'wiki'."""
        return client.get_history(resource_type, resource_id)

    # ── Search ────────────────────────────────────────────────────────────────

    @mcp.tool()
    def taiga_search(project_id: int, query: str) -> dict:
        """Full-text search across user stories, tasks, issues, and wiki pages in a project."""
        return client.search(project_id, query)

    # ── Metadata ─────────────────────────────────────────────────────────────

    @mcp.tool()
    def taiga_list_userstory_statuses(project_id: int) -> list:
        """List available user story statuses for a project."""
        return client.list_userstory_statuses(project_id)

    @mcp.tool()
    def taiga_list_task_statuses(project_id: int) -> list:
        """List available task statuses for a project."""
        return client.list_task_statuses(project_id)

    @mcp.tool()
    def taiga_list_issue_statuses(project_id: int) -> list:
        """List available issue statuses for a project."""
        return client.list_issue_statuses(project_id)

    @mcp.tool()
    def taiga_list_priorities(project_id: int) -> list:
        """List available issue priorities for a project."""
        return client.list_priorities(project_id)

    @mcp.tool()
    def taiga_list_members(project_id: int) -> list:
        """List members (users) of a project."""
        return client.list_users(project_id)
