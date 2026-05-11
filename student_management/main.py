import ttkbootstrap as tb
from ui import StudentManagementSystem

def main():
    root = tb.Window(themename="superhero")
    app = StudentManagementSystem(root)
    root.mainloop();

if __name__ == "__main__":
    main();