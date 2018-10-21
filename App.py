import pandas
import tkinter
import operator
from tkinter import filedialog


class App:

    def __init__(self, window):
        self.window = window
        self.window.title("The Bayesian Trap Classifier")

        self.data = None
        self.cat_data = None
        self.input = None
        self.categories = None
        self.classes = None
        self.classes_counts = None

        self.initial_button_load_data = tkinter.Button(self.window, width=50, height=10,
                                                       text="Press to load data", command=self.load_data)
        self.initial_button_load_data.pack()

        self.categorical_table_frame = tkinter.Frame(self.window)
        self.categorical_table_scroll_h = tkinter.Scrollbar(self.categorical_table_frame, orient=tkinter.HORIZONTAL)
        self.categorical_table_scroll_h.pack(side=tkinter.BOTTOM, fill=tkinter.X)
        self.categorical_table_scroll_v = tkinter.Scrollbar(self.categorical_table_frame, orient=tkinter.VERTICAL)
        self.categorical_table_scroll_v.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        self.categorical_table_text_box = tkinter.Text(self.categorical_table_frame,
                                                       width=80,
                                                       height=10,
                                                       wrap=tkinter.NONE,
                                                       yscrollcommand=self.categorical_table_scroll_v.set,
                                                       xscrollcommand=self.categorical_table_scroll_h.set)
        self.categorical_table_text_box.pack()
        self.categorical_table_scroll_h.config(command=self.categorical_table_text_box.xview)
        self.categorical_table_scroll_v.config(command=self.categorical_table_text_box.yview)

        self.entry_frame = tkinter.Frame(self.window)
        tkinter.Label(self.entry_frame, text="ATTRIBUTES", padx=30).grid(row=0, column=0, sticky=tkinter.W)
        tkinter.Label(self.entry_frame, text="Select to classify", padx=30).grid(row=0, column=3, sticky=tkinter.W)
        self.labels = list()
        self.entries = list()
        self.rb = tkinter.StringVar()

        self.control_frame = tkinter.Frame(self.window, padx=20, pady=30)
        self.button_bayesify = tkinter.Button(self.control_frame,
                                              width=20,
                                              text="Bayesify",
                                              command=self.__bayesify__)
        self.button_bayesify.grid(row=0, column=0, sticky=tkinter.NW, padx=10)
        self.button_load_data = tkinter.Button(self.control_frame,
                                               width=20,
                                               text="Load new data",
                                               command=self.load_data)
        self.button_load_data.grid(row=1, column=0, sticky=tkinter.NW, padx=10)
        self.result_view_frame = tkinter.Frame(self.control_frame)
        self.result_view_scroll = tkinter.Scrollbar(self.result_view_frame, orient=tkinter.VERTICAL)
        self.result_view_scroll.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        self.result_view = tkinter.Text(self.result_view_frame,
                                        width=30,
                                        height=5,
                                        yscrollcommand=self.result_view_scroll.set)
        self.result_view.pack()
        self.result_view_frame.grid(row=0, column=1, rowspan=2, sticky=tkinter.NW, padx=10)

        self.window.mainloop()

    '''
        Load data from file and set the GUI
    '''
    def load_data(self):
        # get the filename
        filename = filedialog.askopenfilename(initialdir="/",
                                              title="Select file",
                                              filetypes=(("csv files", "*.csv"), ("all files", "*.*")))
        self.data = pandas.read_csv(filename)
        # categorisation
        self.cat_data = self.data.astype('category')
        # clear the categorical table view
        self.categorical_table_text_box.delete("1.0", tkinter.END)
        self.initial_button_load_data.destroy()

        # print the categorical table
        cat_tab = pandas.DataFrame()
        i = 1
        for cd in self.cat_data:
            cat_tab[cd] = pandas.Series(self.cat_data[cd].cat.categories)
            label = tkinter.Label(self.entry_frame, text=cd+":")
            label.grid(row=i, column=1, sticky=tkinter.E)
            self.labels.append(label)
            entry = tkinter.Entry(self.entry_frame)
            entry.grid(row=i, column=2)
            self.entries.append(entry)
            tkinter.Radiobutton(self.entry_frame, variable=self.rb, value=cd,
                                anchor=tkinter.CENTER).grid(row=i, column=3)
            i += 1

        self.categorical_table_text_box.insert(tkinter.INSERT, cat_tab.to_string())
        self.categorical_table_frame.pack(anchor=tkinter.NW)
        self.entry_frame.pack(pady=10, anchor=tkinter.NW)
        self.control_frame.pack(anchor=tkinter.NW)

    '''
        Naive Bayesian Classifier
    '''
    def __bayesify__(self):
        # get input
        to_classify = self.rb.get()
        if to_classify == "":
            self.result_view.insert(tkinter.INSERT, "I don't know what to classify.")
            return
        event = dict()
        for i in range(0, len(self.entries)):
            value = self.entries[i].get()
            if value != "":
                key = self.labels[i]["text"].replace(':', '')
                if key != to_classify:
                    event[key] = self.entries[i].get()

        classes = self.cat_data[to_classify].cat.categories
        classes_counts = self.cat_data[to_classify].value_counts()
        hypothesis = dict()
        for klass in classes:

            # ''' prior probability '''
            hypothesis[klass] = classes_counts[klass] / len(self.data)

            # ''' posterior probabilities '''
            for category, value in event.items():
                hypothesis[klass] *= len(self.data[(self.data[category] == value) & (self.data[to_classify] == klass)])\
                                     / classes_counts[klass]

        # ''' normalisation '''
        hypothesis = {k: v / total for total in (sum(hypothesis.values()),) for k, v in hypothesis.items()}

        result = ""
        for key, value in sorted(hypothesis.items(), key=operator.itemgetter(1), reverse=True):
            result += "{0:18} {1:1}\n".format(key, ("%.2f%%" % (100 * value)))
        self.result_view.insert(tkinter.INSERT, result)


App(tkinter.Tk())
