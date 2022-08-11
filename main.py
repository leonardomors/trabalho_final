from kivy.app import App
from mainwidget import MainWidget
from kivy.lang.builder import Builder



class MainApp(App):
    """
    classe do aplicativolabel
    """
    def build(self): 
        """
        construtor do aplicativo
        """
        self._widget = MainWidget(scan_time = 1000, server_ip = '127.0.0.1', port = 502,

        modbus_addrs = {
            'fornalha': 1000,
            'gas_ref' : 1001,
            'gasolina': 1002,
            'nafta': 1003,
            'querosene': 1004,
            'diesel': 1005,
            'oleo_lub': 1006,
            'oleo_comb': 1007,
            'residuos': 1008
        },

        db_path = "//home//juliane//Documentos//supervisorio_aula-master//db/scada.db"
        )

    
        

        
        return self._widget

    def on_stop(self):
        """
        Metodo para apicacao fechada
        """

        self._widget.stopRefresh()

if __name__ == '__main__':
    Builder.load_string(open("mainwidget.kv", encoding= 'utf-8').read(), rulesonly=True)
    Builder.load_string(open("popups.kv", encoding= 'utf-8').read(), rulesonly=True)
    MainApp().run()
