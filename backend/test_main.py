import traceback
import sys

try:
    import main
    print("MAIN IMPORTED SUCCESSFULLY!")
except Exception as e:
    with open("my_import_error.txt", "w") as f:
        traceback.print_exc(file=f)
