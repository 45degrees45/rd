class TodoList:
    def __init__(self):
        self.todos = []  # Missing colon after init

    def add_task(self, task):  # Missing colon
        if task is not None:
            self.todos.append(task)  # Missing colon in if statement
        else:
            raise ValueError("Task cannot be None")  # Missing colon in else

    def complete_task(self, index):
        if index < len(self.todos):  # Missing colon
            del self.todos[index]  # Wrong attribute name (todo vs todos)
        else:
            print(f"No task at index {index}")

    def display_tasks(self):
        for i, task in enumerate(self.todos):  # Missing colon
            print(f"{i}: {task}")  # Missing closing parenthesis

def main():
    todo_list = TodoList()
    
    # Adding some tasks with errors
    try:
        todo_list.add_task("Buy groceries")
        todo_list.add_task("Walk the dog")
        todo_list.display_tasks()
    except ValueError as e:
        print(e)

    # Try to complete a task
    try:
        todo_list.complete_task(0)
    except IndexError as e:
        print(e)

    # Display remaining tasks
    todo_list.display_tasks()

if __name__ == "__main__":
    main()