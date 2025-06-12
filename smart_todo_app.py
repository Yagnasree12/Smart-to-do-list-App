# -*- coding: utf-8 -*-
# Smart To-Do List App (enhanced)

import streamlit as st
from datetime import datetime, timedelta
import uuid
import os
import json
import plotly.graph_objects as go
import pandas as pd
import time

# Constants
TASK_FILE = "tasks.json"
CATEGORIES = ["Work", "Personal", "Study", "Other"]

def recommend_priority(task_text):
    text = task_text.lower()
    if any(word in text for word in ["urgent", "asap", "immediately", "now", "important"]):
        return "High"
    elif any(word in text for word in ["soon", "later", "tomorrow"]):
        return "Medium"
    return "Low"

def load_tasks():
    if os.path.exists(TASK_FILE):
        with open(TASK_FILE, 'r') as f:
            return json.load(f)
    return []

def save_tasks(tasks):
    with open(TASK_FILE, 'w') as f:
        json.dump(tasks, f, indent=2)

def pomodoro_timer():
    st.subheader("🍅 Pomodoro Timer (25 min work / 5 min break)")
    start = st.button("▶️ Start Work Timer")
    if start:
        with st.empty():
            for i in range(25 * 60, 0, -1):
                mins, secs = divmod(i, 60)
                st.metric(label="Work Timer", value=f"{mins:02d}:{secs:02d}")
                time.sleep(1)
            st.success("⏰ Work session complete! Take a 5-minute break!")

def show_analytics(tasks):
    completed = len([t for t in tasks if t['done']])
    pending = len([t for t in tasks if not t['done']])
    fig = go.Figure(data=[go.Pie(labels=['Completed', 'Pending'], values=[completed, pending], hole=0.3)])
    st.plotly_chart(fig)

def main():
    st.set_page_config(page_title="Smart To-Do List", layout="wide")

    if "tasks" not in st.session_state:
        st.session_state.tasks = load_tasks()

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        st.title("🔐 Login")
        username = st.text_input("Username")
        if st.button("Login") and username:
            st.session_state.logged_in = True
            st.experimental_rerun()
        return

    st.title("✅ Smart To-Do List")
    st.markdown("Organize your tasks with intelligence, structure, and style ✨")

    with st.sidebar:
        st.header("🎛️ Settings")
        dark_mode = st.toggle("🌙 Dark Mode")
        filter_category = st.selectbox("📂 Filter by Category", ["All"] + CATEGORIES)
        if st.button("💾 Save Tasks"):
            save_tasks(st.session_state.tasks)
            st.success("Tasks saved successfully")
        df = pd.DataFrame(st.session_state.tasks)
        if not df.empty:
            st.download_button("📤 Export CSV", df.to_csv(index=False), "tasks.csv")
        st.markdown("---")
        pomodoro_timer()

    if dark_mode:
        st.markdown(
            "<style>body { background-color: #0E1117; color: white; }</style>",
            unsafe_allow_html=True
        )

    st.subheader("➕ Add Task")
    with st.form("task_form", clear_on_submit=True):
        task_text = st.text_input("Task")
        due_date = st.date_input("Due Date", min_value=datetime.now().date())
        category = st.selectbox("Category", CATEGORIES)
        auto_priority = recommend_priority(task_text)
        priority = st.selectbox(f"Priority (suggested: {auto_priority})", ["Low", "Medium", "High"], index=["Low", "Medium", "High"].index(auto_priority))
        subtasks = st.text_area("Subtasks (one per line)").splitlines()
        notes = st.text_input("Notes")
        submitted = st.form_submit_button("Add Task")

        if submitted and task_text:
            st.session_state.tasks.append({
                "id": str(uuid.uuid4()),
                "text": task_text,
                "priority": priority,
                "due_date": str(due_date),
                "category": category,
                "subtasks": subtasks,
                "notes": notes,
                "done": False,
                "created": str(datetime.now())
            })

    st.subheader("📋 Task List")
    tasks_to_show = st.session_state.tasks
    if filter_category != "All":
        tasks_to_show = [t for t in tasks_to_show if t["category"] == filter_category]

    for task in tasks_to_show:
        cols = st.columns([0.05, 0.6, 0.15, 0.15, 0.05])
        task["done"] = cols[0].checkbox("", value=task["done"], key=task["id"])
        cols[1].markdown(f"**{'~~' if task['done'] else ''}{task['text']}{'~~' if task['done'] else ''}**\n📅 {task['due_date']} | 🔖 {task['category']} | 🧾 {task['notes']}")
        cols[2].write(f"Priority: {task['priority']}")
        if task['subtasks']:
            cols[1].markdown("**Subtasks:** " + ', '.join(task['subtasks']))
        delete = cols[4].button("🗑️", key=f"del-{task['id']}")
        if delete:
            st.session_state.tasks = [t for t in st.session_state.tasks if t['id'] != task['id']]
            st.experimental_rerun()

    st.subheader("📈 Productivity Overview")
    show_analytics(st.session_state.tasks)

    st.markdown("---")
    st.caption("🚀 Built with ❤️ by Sree | Streamlit App")

if __name__ == "__main__":
    main()
