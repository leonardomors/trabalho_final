from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy_garden.graph import LinePlot
from kivy.uix.boxlayout import BoxLayout

class ModbusPopup(Popup):
    """
    Popup da tela de conexção (modbus)
    """
    def __init__(self, server_ip, port, **kwargs):
        super().__init__(*kwargs)
        self.ids.txt_ip.text = str(server_ip)
        self.ids.txt_port.text = str(port)

    def set_info(self, message):
        self._info = Label(text= str(message), font_size=15, size_hint= (1,0.3))
        self.ids.layout.add_widget(self._info)

    def clear_info(self):
        if self._info is not None:
            self.ids.layout.remove_widget(self._info)
        


class ScanPopup(Popup):
    def __init__(self,scantime, **kwargs):
        super().__init__(**kwargs)
        self.ids.ti_scan.text = str(scantime)