#!/usr/bin/env python 
# coding=utf-8


from model import Model

class Presenter:

    def __init__(self, view):

        self.__model = Model()
        self.__view = view

        # Run communication and start thread
        self.__model.begin()
        self.__model.start()

        # Signal connection
        self.__view.send_data.connect(self.__model.write)
        self.__view.baudrate_changed.connect(
                lambda x: setattr(self.__model, 'br', x))
        self.__view.port_changed.connect(
                lambda x: setattr(self.__model, 'port', x))
        self.__view.eol_changed.connect(self.__model.set_eol)

        self.__view.pause_m.connect(self.__model.pause)
        self.__view.start_m.connect(self.start_model)

        self.__model.error.connect(self.__view.show_error)
        self.__model.port_conf_change.connect(self.__view.update_status_bar)

        self.__view.set_queue(self.__model.get_queue())
        self.__view.set_end_cmd(self.end_cmd)
        self.__view.set_port(self.__model.port)
        self.__view.update_gui()

    def start_model(self):
        '''
        Initalizate serial settings in model and start thread.
        '''
        if not self.__model.paused.is_set():
            self.__model.resume()

    def end_cmd(self):
        '''
        Stop model thread.
        '''
        self.__model.stop()
