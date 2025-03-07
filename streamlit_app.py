import streamlit as st
import numpy as np
from datetime import datetime
import pandas as pd

from agent_tools import BasicSearchModel, ReasoningModel
from extensive_search import run_research
from task_manager import task_manager, TaskStatus

st.set_page_config(page_title="DeepResearchHS", 
                    page_icon=":books:", 
                    layout="wide", 
                    initial_sidebar_state="expanded",
                    menu_items={
                        'About': """
                        # DeepResearch GUI
                        
                        """,
                        'Get Help': 'https://www.streamlit.io/'
                    })

def format_time_delta(seconds):
    """Format time delta in a human-readable format."""
    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    
    if hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"

def save_markdown(content, filename):
    """Save content as a markdown file."""
    with open(filename, "w") as f:
        f.write(content)
    return filename

def main():
    st.title("DeepResearchHS")

    # Create tabs for main interface and task management
    tab1, tab2 = st.tabs(["Research", "Task Queue"])
    
    with tab1:
        search_query_text = st.text_area("Search Query:", height=180)
        
        # add combobox for model selection
        model_selector = st.selectbox("Mode:", ["Quick Search (Google)", "DeepResearch (Perplexity)", "DeepResearch (Google)"])
        
        # Dynamic button text based on selected mode
        button_text = "Search" if model_selector == "Quick Search (Google)" else "Run Deep Search"
        button = st.button(button_text)

        if button and search_query_text:
            if model_selector == "Quick Search (Google)":
                # Direct execution for Quick Search
                with st.spinner(f"Running {model_selector}..."):
                    searchAgent = BasicSearchModel() 
                    response = searchAgent(search_query_text)
                    response_title = "Quick Search Result"
                    
                    st.markdown(f"## {response_title}")
                    st.markdown(response)
                    
                    # Add download button for the result
                    st.download_button(
                        label="Download as Markdown",
                        data=response,
                        file_name=f"{model_selector.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                        mime="text/markdown"
                    )
            else:
                # Add task to queue for other modes
                try:
                    # Add task to queue
                    task_id = task_manager.add_task(search_query_text, model_selector)
                    
                    # Start the task in the background
                    if model_selector == "Perplexitiy DeepSearch":
                        #task_manager.start_task(task_id, get_article, search_query_text)
                        pass
                    elif model_selector == "DeepResearch (Google)":
                        task_manager.start_task(task_id, run_research, search_query_text)
                    
                    st.success(f"Query added to Task Queue! Check the Task Queue tab for progress.")
                    
                    # Create a notification
                    st.balloons()
                except ValueError as e:
                    st.error(str(e))

        # Queue button removed as requested
    
    with tab2:
        st.header("Task Queue")
        
        # Add refresh button
        if st.button("Refresh Task List"):
            st.rerun()
        
        # Get all tasks
        tasks = task_manager.get_all_tasks()
        
        if not tasks:
            st.info("No tasks in the queue.")
        else:
            # Create a DataFrame for better display
            task_data = []
            for task in tasks:
                elapsed_time, is_running = task_manager.get_task_elapsed_time(task['id'])
                
                # Create task entry
                task_entry = {
                    "ID": task['id'],
                    "Description": task_manager.get_task_brief(task['id']),
                    "Type": task['task_type'],
                    "Status": task['status'],
                    "Created": datetime.fromtimestamp(task['created_at']).strftime('%Y-%m-%d %H:%M:%S'),
                    "Elapsed": format_time_delta(elapsed_time),
                    "Is Running": is_running
                }
                task_data.append(task_entry)
            
            # Display tasks as a dataframe
            df = pd.DataFrame(task_data)
            st.dataframe(df[["Description", "Type", "Status", "Created", "Elapsed"]], use_container_width=True)
            
            # Display individual task details with expanders
            for task in tasks:
                with st.expander(f"{task_manager.get_task_brief(task['id'])} ({task['status']})"):
                    st.write(f"**Query:** {task['query']}")
                    st.write(f"**Type:** {task['task_type']}")
                    st.write(f"**Status:** {task['status']}")
                    
                    elapsed_time, is_running = task_manager.get_task_elapsed_time(task['id'])
                    st.write(f"**Elapsed Time:** {format_time_delta(elapsed_time)}")
                    
                    # Show cancel button for running or queued tasks
                    if task['status'] in [TaskStatus.QUEUED, TaskStatus.RUNNING]:
                        if st.button(f"Cancel Task", key=f"cancel_{task['id']}"):
                            if task_manager.cancel_task(task['id']):
                                st.success("Task cancelled successfully!")
                                st.rerun()
                            else:
                                st.error("Failed to cancel task.")
                    
                    # Show result for completed tasks
                    if task['status'] == TaskStatus.COMPLETED and task['result']:
                        st.markdown("### Result:")
                        # Using a toggle instead of nested expander
                        if st.toggle("Show/Hide Result", key=f"toggle_result_{task['id']}"):
                            st.markdown(task['result'])
                        
                        # Add download button
                        st.download_button(
                            label="Download Result as Markdown",
                            data=task['result'],
                            file_name=f"{task['task_type'].lower().replace(' ', '_')}_{datetime.fromtimestamp(task['created_at']).strftime('%Y%m%d_%H%M%S')}.md",
                            mime="text/markdown",
                            key=f"download_{task['id']}"
                        )
                    
                    # Show error for failed tasks
                    if task['status'] == TaskStatus.FAILED and task['error']:
                        st.error(f"Error: {task['error']}")
                    
                    # Add a button to remove the task
                    if st.button(f"Remove Task", key=f"remove_{task['id']}"):
                        if task_manager.remove_task(task['id']):
                            st.success("Task removed successfully!")
                            st.rerun()
                        else:
                            st.error("Failed to remove task.")

if __name__ == "__main__":
    main()