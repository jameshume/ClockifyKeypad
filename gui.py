import wx
from typing import Dict, List, Callable

class Model:
    """Model class that holds project and task data"""
    
    def __init__(self):
        self._observers: List[Callable] = []
        self._projects_data = {
            "Website Redesign": ["Design Mockups", "Code Review", "Bug Fixes", "Deployment"],
            "Mobile App": ["UI Design", "API Integration", "Unit Tests", "App Store Release"],
            "Database Migration": ["Schema Design", "Data Transfer", "Performance Testing", "Documentation"],
            "API Development": ["Endpoint Design", "Authentication", "Testing", "Documentation"],
            "Testing Framework": ["Test Planning", "Automation Scripts", "Bug Reports", "Code Coverage"]
        }
    
    def add_observer(self, callback: Callable):
        """Add observer callback for model updates"""
        self._observers.append(callback)
    
    def remove_observer(self, callback: Callable):
        """Remove observer callback"""
        if callback in self._observers:
            self._observers.remove(callback)
    
    def notify_observers(self):
        """Notify all observers of model changes"""
        for callback in self._observers:
            callback()
    
    def get_projects(self) -> List[str]:
        """Get list of all projects"""
        return list(self._projects_data.keys())
    
    def get_tasks_for_project(self, project: str) -> List[str]:
        """Get tasks for a specific project"""
        return self._projects_data.get(project, [])
    
    def add_project(self, project: str, tasks: List[str] = None):
        """Add a new project with tasks"""
        if tasks is None:
            tasks = []
        self._projects_data[project] = tasks
        self.notify_observers()
    
    def update_project_tasks(self, project: str, tasks: List[str]):
        """Update tasks for an existing project"""
        if project in self._projects_data:
            self._projects_data[project] = tasks
            self.notify_observers()

class MainView(wx.Frame):
    """View class - handles GUI display and user interactions"""
    
    def __init__(self):
        super().__init__(None, title="MVP GUI Application", size=(600, 400))
        
        # Create main panel
        panel = wx.Panel(self)
        
        # Create main sizer
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # Left side - Grid of text panels
        left_sizer = wx.GridSizer(2, 3, 10, 10)  # 2 rows, 3 cols, 10px spacing
        
        # Create 6 text panels
        self.text_panels = []
        self.text_labels = []  # Store references to labels
        self.selected_panel = None
        self.selected_panel_index = None
        
        for i in range(6):
            text_panel = wx.Panel(panel, size=(120, 100))
            text_panel.SetBackgroundColour(wx.Colour(255, 255, 255))
            
            # Add "Text" label
            text_sizer = wx.BoxSizer(wx.VERTICAL)
            text_label = wx.StaticText(text_panel, label="Text")
            text_label.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
            text_sizer.Add(text_label, 1, wx.CENTER | wx.ALL | wx.EXPAND, 5)
            text_panel.SetSizer(text_sizer)
            
            # Make panels clickable
            text_panel.Bind(wx.EVT_LEFT_DOWN, lambda evt, panel_idx=i: self.on_panel_click(evt, panel_idx))
            text_label.Bind(wx.EVT_LEFT_DOWN, lambda evt, panel_idx=i: self.on_panel_click(evt, panel_idx))
            
            # Draw border
            text_panel.Bind(wx.EVT_PAINT, lambda evt, panel=text_panel, is_red=(i==5): self.on_paint_panel(evt, panel, is_red))
            
            self.text_panels.append(text_panel)
            self.text_labels.append(text_label)  # Store label reference
            left_sizer.Add(text_panel, 0, wx.EXPAND)
        
        # Right side - Controls
        right_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Project field
        project_sizer = wx.BoxSizer(wx.HORIZONTAL)
        project_label = wx.StaticText(panel, label="Project")
        self.project_combo = wx.ComboBox(panel, style=wx.CB_READONLY, size=(150, -1))
        project_sizer.Add(project_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)
        project_sizer.Add(self.project_combo, 1, wx.EXPAND)
        
        # Task field
        task_sizer = wx.BoxSizer(wx.HORIZONTAL)
        task_label = wx.StaticText(panel, label="Task")
        self.task_combo = wx.ComboBox(panel, style=wx.CB_READONLY, size=(150, -1))
        task_sizer.Add(task_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)
        task_sizer.Add(self.task_combo, 1, wx.EXPAND)
        
        # Buttons
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.save_btn = wx.Button(panel, label="Save")
        self.exit_btn = wx.Button(panel, label="Exit")
        
        # Button state tracking
        self.selected_button = None
        self.save_btn.SetBackgroundColour(wx.Colour(240, 240, 240))
        self.exit_btn.SetBackgroundColour(wx.Colour(240, 240, 240))
        
        button_sizer.Add(self.save_btn, 0, wx.RIGHT, 10)
        button_sizer.Add(self.exit_btn, 0)
        
        # Add to right sizer
        right_sizer.Add(project_sizer, 0, wx.EXPAND | wx.BOTTOM, 20)
        right_sizer.Add(task_sizer, 0, wx.EXPAND | wx.BOTTOM, 30)
        right_sizer.Add(button_sizer, 0, wx.ALIGN_LEFT)
        
        # Add left and right to main sizer
        main_sizer.Add(left_sizer, 1, wx.EXPAND | wx.ALL, 20)
        main_sizer.Add(right_sizer, 0, wx.EXPAND | wx.ALL, 20)
        
        panel.SetSizer(main_sizer)
        
        # Bind events
        self.save_btn.Bind(wx.EVT_BUTTON, self.on_save_click)
        self.exit_btn.Bind(wx.EVT_BUTTON, self.on_exit_click)
        self.project_combo.Bind(wx.EVT_COMBOBOX, self.on_project_change)
        self.task_combo.Bind(wx.EVT_COMBOBOX, self.on_task_change)
        
        # Center the frame
        self.Center()
        
        # Presenter will be set externally
        self.presenter = None
    
    def set_presenter(self, presenter):
        """Set the presenter for this view"""
        self.presenter = presenter
    
    def populate_projects(self, projects: List[str]):
        """Populate the project dropdown"""
        current_selection = self.project_combo.GetValue()
        self.project_combo.Clear()
        self.project_combo.AppendItems(projects)
        
        # Restore selection if it still exists
        if current_selection in projects:
            self.project_combo.SetValue(current_selection)
    
    def populate_tasks(self, tasks: List[str]):
        """Populate the task dropdown"""
        current_selection = self.task_combo.GetValue()
        self.task_combo.Clear()
        self.task_combo.AppendItems(tasks)
        
        # Restore selection if it still exists
        if current_selection in tasks:
            self.task_combo.SetValue(current_selection)
    
    def get_selected_project(self) -> str:
        """Get currently selected project"""
        return self.project_combo.GetValue()
    
    def get_selected_task(self) -> str:
        """Get currently selected task"""
        return self.task_combo.GetValue()
    
    def on_panel_click(self, event, panel_index):
        """Handle panel click - select and highlight"""
        self.selected_panel = self.text_panels[panel_index]
        self.selected_panel_index = panel_index
        
        # Update panel backgrounds and refresh
        for i, panel in enumerate(self.text_panels):
            if panel == self.selected_panel:
                panel.SetBackgroundColour(wx.Colour(220, 230, 255))  # Light blue background
            else:
                panel.SetBackgroundColour(wx.Colour(255, 255, 255))  # White background
            panel.Refresh()
        
        print(f"Panel {panel_index + 1} selected!")  # Debug message
    
    def on_paint_panel(self, event, panel, is_red=False):
        """Draw border around panels"""
        dc = wx.PaintDC(panel)
        dc.Clear()
        
        size = panel.GetSize()
        
        # Determine border color and width
        if panel == self.selected_panel:
            dc.SetPen(wx.Pen(wx.Colour(0, 0, 255), 3))  # Blue border for selected
        elif is_red:
            dc.SetPen(wx.Pen(wx.Colour(255, 0, 0), 2))  # Red border for panel 6
        else:
            dc.SetPen(wx.Pen(wx.Colour(0, 0, 0), 2))    # Black border for others
        
        dc.SetBrush(wx.Brush(wx.Colour(255, 255, 255), wx.BRUSHSTYLE_TRANSPARENT))
        dc.DrawRectangle(0, 0, size.width, size.height)
    
    def on_project_change(self, event):
        """Handle project selection change"""
        if self.presenter:
            self.presenter.on_project_selected(self.get_selected_project())
    
    def on_task_change(self, event):
        """Handle task selection change"""
        if self.presenter:
            self.presenter.on_task_selected(self.get_selected_task())
    
    def on_save_click(self, event):
        """Handle Save button click - select and execute"""
        self.selected_button = self.save_btn
        self.highlight_selected_button()
        
        if self.presenter:
            self.presenter.on_save_clicked()
    
    def on_exit_click(self, event):
        """Handle Exit button click - select and execute"""
        self.selected_button = self.exit_btn
        self.highlight_selected_button()
        
        if self.presenter:
            self.presenter.on_exit_clicked()
    
    def highlight_selected_button(self):
        """Highlight the selected button"""
        # Reset both buttons to normal color
        self.save_btn.SetBackgroundColour(wx.Colour(240, 240, 240))
        self.exit_btn.SetBackgroundColour(wx.Colour(240, 240, 240))
        
        # Highlight selected button
        if self.selected_button:
            self.selected_button.SetBackgroundColour(wx.Colour(100, 149, 237))  # Cornflower blue
        
        # Force refresh to show changes immediately
        self.save_btn.Refresh()
        self.exit_btn.Refresh()
        self.Update()
    
    def update_selected_panel_text(self, project: str, task: str):
        """Update the selected panel's text"""
        if self.selected_panel and self.selected_panel_index is not None:
            # Combine project and task text
            combined_text = f"{project}\n{task}" if project and task else project or task or "Text"
            
            label = self.text_labels[self.selected_panel_index]
            label.SetLabel(combined_text)
            label.Wrap(100)  # Wrap text to fit in panel
            self.selected_panel.Layout()  # Refresh layout
    
    def update_selected_button_text(self, project: str, task: str):
        """Update the selected button's text"""
        if self.selected_button:
            button_text = f"{project} - {task}" if project and task else project or task
            if button_text:
                self.selected_button.SetLabel(button_text)
                # Maintain highlighting after text change
                self.highlight_selected_button()
    
    def show_save_message(self, project: str, task: str):
        """Show save confirmation message"""
        wx.MessageBox(f"Saved!\nProject: {project}\nTask: {task}", "Save", wx.OK | wx.ICON_INFORMATION)

class Presenter:
    """Presenter class - mediates between Model and View"""
    
    def __init__(self, model: Model, view: MainView):
        self.model = model
        self.view = view
        
        # Set up bidirectional communication
        self.view.set_presenter(self)
        self.model.add_observer(self.on_model_updated)
        
        # Initialize view with model data
        self.on_model_updated()
    
    def on_model_updated(self):
        """Handle model updates - refresh view"""
        projects = self.model.get_projects()
        self.view.populate_projects(projects)
        
        # If a project is selected, update tasks
        selected_project = self.view.get_selected_project()
        if selected_project:
            tasks = self.model.get_tasks_for_project(selected_project)
            self.view.populate_tasks(tasks)
    
    def on_project_selected(self, project: str):
        """Handle project selection"""
        if project:
            tasks = self.model.get_tasks_for_project(project)
            self.view.populate_tasks(tasks)
        else:
            self.view.populate_tasks([])
        
        # Update selected content
        self.update_selected_content()
    
    def on_task_selected(self, task: str):
        """Handle task selection"""
        # Update selected content when task changes
        self.update_selected_content()
    
    def update_selected_content(self):
        """Update selected panel and button with current dropdown values"""
        project = self.view.get_selected_project()
        task = self.view.get_selected_task()
        
        # Update panel text
        self.view.update_selected_panel_text(project, task)
        
        # Update button text
        self.view.update_selected_button_text(project, task)
    
    def on_save_clicked(self):
        """Handle save button click"""
        project = self.view.get_selected_project()
        task = self.view.get_selected_task()
        self.view.show_save_message(project, task)
    
    def on_exit_clicked(self):
        """Handle exit button click"""
        # Small delay to show highlight before closing
        wx.CallLater(100, self.view.Close)

class App(wx.App):
    def OnInit(self):
        # Create Model, View, and Presenter
        model = Model()
        view = MainView()
        presenter = Presenter(model, view)
        
        view.Show()
        return True

if __name__ == '__main__':
    app = App()
    app.MainLoop()