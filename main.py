from kivy.app import App
from mainwidget import MainWidget
from kivy.lang.builder import Builder

class MyApp(App):
    """
    Classe do aplicativo
    """
    def build(self):
        """
        Construtor/método que gera o aplicativo com o widget principal
        """
        self._widget = MainWidget(scantime=1000, server_ip='127.0.0.1', port=503)
        return self._widget
        
if __name__ == '__main__': # Comando que faz com que o app abra apenas se for excutado o arquivo main diretamente
    Builder.load_string(open("mainwidget.kv", encoding="utf-8").read(), rulesonly=True)
    Builder.load_string(open("popups.kv", encoding="utf-8").read(), rulesonly=True)
    MyApp().run()
