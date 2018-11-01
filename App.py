import pandas
import numpy
import tkinter
import operator
from tkinter import filedialog


class AutoScrollbar(tkinter.Scrollbar):
    # a scrollbar that hides itself if it's not needed.  only
    # works if you use the grid geometry manager.
    def set(self, lo, hi):
        if float(lo) <= 0.0 and float(hi) >= 1.0:
            # grid_remove is currently missing from Tkinter!
            self.tk.call("grid", "remove", self)
        else:
            self.grid()
        tkinter.Scrollbar.set(self, lo, hi)

    def pack(self, **kw):
        raise tkinter.TclError("cannot use pack with this widget")

    def place(self, **kw):
        raise tkinter.TclError("cannot use place with this widget")


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
        self.numeric_columns = None
        self.labels = []
        self.entries = []
        self.rb = tkinter.StringVar()

        #
        # create scrolled canvas
        self.window_scroll_v = AutoScrollbar(self.window, orient=tkinter.VERTICAL)
        self.window_scroll_v.grid(row=0, column=1, sticky=tkinter.N + tkinter.S)
        self.window_scroll_h = AutoScrollbar(self.window, orient=tkinter.HORIZONTAL)
        self.window_scroll_h.grid(row=1, column=0, sticky=tkinter.E + tkinter.W)

        self.canvas = tkinter.Canvas(self.window,
                                     yscrollcommand=self.window_scroll_v.set,
                                     xscrollcommand=self.window_scroll_h.set)
        self.canvas.grid(row=0, column=0, sticky=tkinter.N + tkinter.S + tkinter.E + tkinter.W)

        self.window_scroll_v.config(command=self.canvas.yview)
        self.window_scroll_h.config(command=self.canvas.xview)

        # make the canvas expandable
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_columnconfigure(0, weight=1)

        #
        # create canvas content
        self.window_frame = tkinter.Frame(self.canvas)
        self.window_frame.rowconfigure(1, weight=1)
        self.window_frame.columnconfigure(1, weight=1)

        self.initial_button_load_data = tkinter.Button(self.window_frame,
                                                       width=40,
                                                       height=13,
                                                       text="Press to load data",
                                                       command=self.load_data)
        self.initial_button_load_data.pack()

        self.categorical_table_frame = tkinter.Frame(self.window_frame)
        self.categorical_table_scroll_h = tkinter.Scrollbar(self.categorical_table_frame, orient=tkinter.HORIZONTAL)
        self.categorical_table_scroll_h.pack(side=tkinter.BOTTOM, fill=tkinter.X)
        self.categorical_table_scroll_v = tkinter.Scrollbar(self.categorical_table_frame, orient=tkinter.VERTICAL)
        self.categorical_table_scroll_v.pack(side=tkinter.LEFT, fill=tkinter.Y)
        self.categorical_table_text_box = tkinter.Text(self.categorical_table_frame,
                                                       width=80,
                                                       height=13,
                                                       wrap=tkinter.NONE,
                                                       yscrollcommand=self.categorical_table_scroll_v.set,
                                                       xscrollcommand=self.categorical_table_scroll_h.set)
        self.categorical_table_text_box.pack()
        self.categorical_table_scroll_h.config(command=self.categorical_table_text_box.xview)
        self.categorical_table_scroll_v.config(command=self.categorical_table_text_box.yview)

        self.entry_frame = tkinter.Frame(self.window_frame)
        tkinter.Label(self.entry_frame,
                      name="a",
                      text="ATTRIBUTES",
                      padx=30).grid(row=0,
                                    column=0,
                                    sticky=tkinter.W)
        tkinter.Label(self.entry_frame,
                      name="b",
                      text="Select to classify",
                      padx=30).grid(row=0,
                                    column=3,
                                    sticky=tkinter.W)

        self.control_frame = tkinter.Frame(self.window_frame, padx=20, pady=30)
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
                                        height=6,
                                        yscrollcommand=self.result_view_scroll.set)
        self.result_view.pack()
        self.result_view_frame.grid(row=0, column=1, rowspan=2, sticky=tkinter.NW, padx=10)

        self.canvas.create_window(0, 0, anchor=tkinter.NW, window=self.window_frame)
        self.window_frame.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

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
        self.__clear__()
        # print the categorical table
        cat_tab_string = "\n"
        # find numerical columns
        self.numeric_columns = self.data.applymap(numpy.isreal).all().to_dict()
        i = 1
        for cd in self.cat_data:
            cat_tab_string += cd + "  [" + self.cat_data[cd].cat.categories.dtype_str + "]\n"
            label = tkinter.Label(self.entry_frame, text=cd+":")
            label.grid(row=i, column=1, sticky=tkinter.E)
            self.labels.append(label)
            entry = tkinter.Entry(self.entry_frame)
            entry.grid(row=i, column=2)
            self.entries.append(entry)
            # do not add radio button for numeric values
            if self.numeric_columns[cd] is False:
                tkinter.Radiobutton(self.entry_frame, variable=self.rb, value=cd,
                                    anchor=tkinter.CENTER).grid(row=i, column=3)
                cat_tab_string += "       " + str(self.cat_data[cd].cat.categories.tolist()) + "\n\n"
            else:
                cat_tab_string += "       (" + str(min(self.data[cd])) + "," + str(max(self.data[cd])) + ")\n\n"
            i += 1

        self.categorical_table_text_box.insert(tkinter.INSERT, cat_tab_string)
        self.categorical_table_frame.pack(anchor=tkinter.NW)
        self.entry_frame.pack(pady=10, anchor=tkinter.NW)
        self.control_frame.pack(anchor=tkinter.NW)
        self.canvas.create_window(0, 0, anchor=tkinter.NW, window=self.window_frame)
        self.window_frame.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def __clear__(self):
        for widget in self.entry_frame.winfo_children():
            if widget.winfo_name() not in ("a", "b"):
                widget.destroy()
        self.labels.clear()
        self.entries.clear()
        self.categorical_table_text_box.delete("1.0", tkinter.END)
        self.result_view.delete("1.0", tkinter.END)
        self.initial_button_load_data.destroy()

    '''
        Naive Bayesian Classifier
    '''
    def __bayesify__(self):
        self.result_view.delete("1.0", tkinter.END)
        # get input
        to_classify = self.rb.get()
        if to_classify == "":
            self.result_view.insert(tkinter.INSERT, "I don't know what to classify.")
            return
        event = {}
        for i in range(0, len(self.entries)):
            value = self.entries[i].get()
            if value != "":
                key = self.labels[i]["text"].replace(':', '')
                if key != to_classify:
                    event[key] = self.entries[i].get()

        classes = self.cat_data[to_classify].cat.categories
        classes_counts = self.cat_data[to_classify].value_counts()

        # parametrisation of numerical data
        param_columns = ['A']
        param_columns.extend(classes.tolist())
        mu = pandas.DataFrame(columns=param_columns)
        sigma = pandas.DataFrame(columns=param_columns)
        for column in self.numeric_columns.items():
            # select numeric columns
            if column[1] is True:
                row_mu = [column[0]]
                row_sigma = [column[0]]
                for c in classes:
                    # select data for the class
                    datum = self.data[self.data[to_classify] == c][column[0]]
                    # compute mean
                    m = sum(datum) / len(datum)
                    row_mu.append(m)
                    # compute variance (unbiased)
                    row_sigma.append(sum(numpy.power((datum - m), 2)) / (len(datum) - 1))
                mu.loc[len(mu)] = row_mu
                sigma.loc[len(sigma)] = row_sigma

        hypothesis = {}
        for c in classes:

            # prior probability
            hypothesis[c] = classes_counts[c] / len(self.data)

            # posterior probabilities
            for category, value in event.items():
                if mu['A'].isin([category]).any() and sigma['A'].isin([category]).any():
                    # Gaussian
                    m = mu[mu['A'] == category][c].values[0]
                    s = sigma[sigma['A'] == category][c].values[0]
                    hypothesis[c] *= numpy.exp((-numpy.power(float(value) - m, 2)) / (2 * s)) / numpy.sqrt(2 * numpy.pi * s)
                else:
                    hypothesis[c] *= len(self.data[(self.data[category] == value) & (self.data[to_classify] == c)]) / classes_counts[c]

        # normalisation
        hypothesis = {k: v / total for total in (sum(hypothesis.values()),) for k, v in hypothesis.items()}
        print(hypothesis)

        result = ""
        for key, value in sorted(hypothesis.items(), key=operator.itemgetter(1), reverse=True):
            result += "{0:18} {1:1}\n".format(key, ("%.2f%%" % (100 * value)))
        self.result_view.insert(tkinter.INSERT, result)


App(tkinter.Tk())
