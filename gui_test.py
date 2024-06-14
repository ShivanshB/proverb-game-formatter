import tkinter as tk
import re
from tkinter import messagebox

# Global Variables
PDF_PATTERN = r'^.+\.pdf$'
DATA_SUBMITTED = False
user_input_data = {
    "filename": "",
    "proverb": "",
    "clue": "",
    "prev": "",
    "integers": []
}

def get_user_input():
    # create main window
    root = tk.Tk()
    root.title("Puzzle Parameters")

    # function to handle button click
    def on_submit():
        filename = filename_field.get().strip()
        proverb = proverb_field.get().strip()
        clue = clue_field.get().strip()
        prev = prev_field.get().strip()
        integer_list = reveal_letters.get().strip().split(',') # split string into a list

        errors = []

        if not filename:
            errors.append("Filename is required")
        elif not re.search(PDF_PATTERN, filename, re.IGNORECASE):
            errors.append("Filename must end in \".pdf\".")
        
        if not proverb:
            errors.append("Proverb is required.")

        try:
            # if the field is empty
            if len(integer_list) == 1 and '' in integer_list:
                integers = []
            else:
                integers = [int(num.strip()) for num in integer_list]
        except ValueError:
            errors.append("Please enter valid integers separated by commas.")

        if errors:
            messagebox.showerror("Validation Error(s)", "\n".join(errors))
            return
        else:
            messagebox.showinfo("Puzzle Created", f"proverb: {proverb}\nfilename: {filename}")
            user_input_data["filename"] = filename
            user_input_data["proverb"] = proverb
            user_input_data["clue"] = clue
            user_input_data["prev"] = prev
            user_input_data["integers"] = integer_list
            # mark data as submitted
            DATA_SUBMITTED = True

        root.destroy()


    tk.Label(root, text="Enter pdf filename.").pack()
    filename_field = tk.Entry(root, width=50)
    filename_field.pack()

    tk.Label(root, text="Enter proverb.").pack()
    proverb_field = tk.Entry(root, width=50)
    proverb_field.pack()

    tk.Label(root, text="Enter clue.").pack()
    clue_field = tk.Entry(root, width=50)
    clue_field.pack()

    tk.Label(root, text="Enter previous day's answer.").pack()
    prev_field = tk.Entry(root, width=50)
    prev_field.pack()

    tk.Label(root, text="Enter integers (comma-separated):").pack()
    reveal_letters = tk.Entry(root, width=50)
    reveal_letters.pack()

    submit_button = tk.Button(root, text="Submit", command=on_submit)
    submit_button.pack()

    root.mainloop()

if __name__ == '__main__':
    get_user_input()
    if DATA_SUBMITTED:
        # then generate puzzle
        return 



