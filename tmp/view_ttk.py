#!/usr/bin/env python
# coding=utf-8

from    tkinter     import *

class View(Frame):

    def __init__(self, master=None):
        Frame.__init__(self, master)                 
        self.master     = master

        self.queue      = None
        self.end_cmd    = None
        self.autoscroll = True

        self.__initUI()

    def __initUI(self):
        # self.master.geometry('400x300')
        self.master.title("GUI")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=2)
        self.grid(sticky=N+S+W+E)

        top = self.winfo_toplevel()
        top.columnconfigure(0, weight=1)
        top.rowconfigure(0, weight=1)
        top.rowconfigure(1, weight=2)


        cmd_frame = Frame(self)
        cmd_frame.columnconfigure(0, weight=1)
        cmd_frame.rowconfigure(0, weight=1)
        cmd_text = Text(cmd_frame, height='1.2', font='14')
        cmd_text.grid(row=0, column=0, sticky=W+E)

        send_btn = Button(cmd_frame, text="Send", height='1')
        send_btn.grid(row=0, column=1)
        cmd_frame.grid(row=0, column=0, sticky=W+E)

        self.editor = Frame(self)
        self.editor.columnconfigure(0, weight=1)
        self.editor.rowconfigure(0, weight=1)
        self.text = Text(self.editor)
        self.text.grid(row=0, column=0, sticky=N+S+W+E)

        s_start = Scrollbar(self.editor)
        s_start.grid(row=0, column=1, sticky=N+S+W+E)
        s_start.config(command=self.text.yview)
        self.text.config(yscrollcommand=s_start.set)

        self.editor.grid(row=1, column=0, sticky=N+S+W+E)

    def set_queue(self, queue):
        self.queue = queue

    def set_end_cmd(self, end_cmd):
        self.end_cmd = end_cmd
        self.master.protocol("WM_DELETE_WINDOW", end_cmd)

    def update_gui(self):
        # self.process_incoming()
        self.master.update()
        # self.text.after(10, self.update_gui)
    
    def process_incoming(self):
        while self.queue.qsize():
            try:
                msg = self.queue.get(0)
                # Check contents of message and do what it says
                # As a test, we simply print it
                self.text.insert(END, str(msg) + '\n')
                if self.autoscroll:
                    self.text.see(END)
            except Queue.Empty:
                pass

