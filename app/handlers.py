from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Project, Task


HELP_TEXT = """*WhatsApp Project Tracker*

*Commands:*
• `new project <name>` — Create a project
• `list projects` — Show all projects
• `status <project>` — Project overview + tasks
• `add task <project> | <task>` — Add a task
• `list tasks <project>` — List tasks in a project
• `done <task_id>` — Mark a task as done
• `undone <task_id>` — Reopen a task
• `delete project <name>` — Delete a project
• `help` — Show this message

Examples:
`new project Website Redesign`
`add task Website Redesign | Design homepage mockup`
`done 3`
"""


async def handle_message(text: str, session: AsyncSession) -> str:
    text = text.strip()
    lower = text.lower()

    if lower in ("help", "hi", "hello", "start", "/help", "/start"):
        return HELP_TEXT

    # new project <name>
    if lower.startswith("new project "):
        name = text[12:].strip()
        if not name:
            return "Please provide a project name.\nExample: `new project Website Redesign`"
        return await create_project(session, name)

    # list projects
    if lower in ("list projects", "projects", "list"):
        return await list_projects(session)

    # status <project>
    if lower.startswith("status "):
        name = text[7:].strip()
        return await project_status(session, name)

    # add task <project> | <task>
    if lower.startswith("add task "):
        return await add_task(session, text[9:].strip())

    # list tasks <project>
    if lower.startswith("list tasks "):
        name = text[11:].strip()
        return await list_tasks(session, name)

    # done <task_id>
    if lower.startswith("done "):
        try:
            task_id = int(text[5:].strip())
            return await mark_done(session, task_id, done=True)
        except ValueError:
            return "Please provide a valid task ID.\nExample: `done 5`"

    # undone <task_id>
    if lower.startswith("undone "):
        try:
            task_id = int(text[7:].strip())
            return await mark_done(session, task_id, done=False)
        except ValueError:
            return "Please provide a valid task ID.\nExample: `undone 5`"

    # delete project <name>
    if lower.startswith("delete project "):
        name = text[15:].strip()
        return await delete_project(session, name)

    return (
        "I didn't understand that command.\n\n"
        "Type *help* to see available commands."
    )


async def create_project(session: AsyncSession, name: str) -> str:
    result = await session.execute(select(Project).where(Project.name.ilike(name)))
    existing = result.scalar_one_or_none()
    if existing:
        return f"Project *{name}* already exists."

    project = Project(name=name)
    session.add(project)
    await session.commit()
    return f"✅ Project created: *{name}*"


async def list_projects(session: AsyncSession) -> str:
    result = await session.execute(
        select(Project).order_by(Project.created_at.desc())
    )
    projects = result.scalars().all()

    if not projects:
        return "No projects yet.\nCreate one with:\n`new project My Project`"

    lines = ["*Your Projects:*\n"]
    for p in projects:
        status_emoji = {"active": "🟢", "completed": "✅", "archived": "📦"}.get(p.status, "•")
        lines.append(f"{status_emoji} *{p.name}* (id: {p.id})")

    return "\n".join(lines)


async def project_status(session: AsyncSession, name: str) -> str:
    result = await session.execute(
        select(Project)
        .options(selectinload(Project.tasks))
        .where(Project.name.ilike(name))
    )
    project = result.scalar_one_or_none()
    if not project:
        return f"Project *{name}* not found."

    total = len(project.tasks)
    done = sum(1 for t in project.tasks if t.is_done)
    pending = total - done

    lines = [
        f"*Project: {project.name}*",
        f"Status: {project.status}",
        f"Tasks: {done}/{total} done ({pending} remaining)\n",
    ]

    if project.tasks:
        lines.append("*Tasks:*")
        for t in sorted(project.tasks, key=lambda x: (x.is_done, x.id)):
            check = "✅" if t.is_done else "⬜"
            lines.append(f"{check} [{t.id}] {t.title}")
    else:
        lines.append("_No tasks yet._")

    return "\n".join(lines)


async def add_task(session: AsyncSession, raw: str) -> str:
    if "|" not in raw:
        return (
            "Format: `add task <project> | <task description>`\n"
            "Example: `add task Website | Design homepage`"
        )

    project_name, task_title = [part.strip() for part in raw.split("|", 1)]
    if not project_name or not task_title:
        return "Both project name and task description are required."

    result = await session.execute(
        select(Project).where(Project.name.ilike(project_name))
    )
    project = result.scalar_one_or_none()
    if not project:
        return f"Project *{project_name}* not found.\nCreate it first with `new project {project_name}`"

    task = Task(project_id=project.id, title=task_title)
    session.add(task)
    await session.commit()
    await session.refresh(task)

    return f"✅ Task added to *{project.name}*:\n[{task.id}] {task.title}"


async def list_tasks(session: AsyncSession, name: str) -> str:
    result = await session.execute(
        select(Project)
        .options(selectinload(Project.tasks))
        .where(Project.name.ilike(name))
    )
    project = result.scalar_one_or_none()
    if not project:
        return f"Project *{name}* not found."

    if not project.tasks:
        return f"No tasks in *{project.name}* yet."

    lines = [f"*Tasks in {project.name}:*\n"]
    for t in sorted(project.tasks, key=lambda x: (x.is_done, x.id)):
        check = "✅" if t.is_done else "⬜"
        lines.append(f"{check} [{t.id}] {t.title}")

    return "\n".join(lines)


async def mark_done(session: AsyncSession, task_id: int, done: bool) -> str:
    result = await session.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        return f"Task ID {task_id} not found."

    task.is_done = done
    task.completed_at = datetime.utcnow() if done else None
    await session.commit()

    if done:
        return f"✅ Task marked as done:\n[{task.id}] {task.title}"
    else:
        return f"⬜ Task reopened:\n[{task.id}] {task.title}"


async def delete_project(session: AsyncSession, name: str) -> str:
    result = await session.execute(
        select(Project).where(Project.name.ilike(name))
    )
    project = result.scalar_one_or_none()
    if not project:
        return f"Project *{name}* not found."

    await session.delete(project)
    await session.commit()
    return f"🗑️ Project *{name}* deleted (including all its tasks)."