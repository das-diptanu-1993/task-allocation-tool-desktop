from cx_Freeze import setup, Executable
  
setup(name = "Task_Allocation_Planner" ,
      version = "0.1" ,
      description = "" ,
      executables = [Executable("__App__.py")])