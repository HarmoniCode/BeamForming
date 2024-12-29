from PyQt5.QtWidgets import QApplication
from heatmap_window import HeatMapWindow


if __name__ == "__main__":
    app = QApplication([])
    with open("styles/index.qss") as f:
        app.setStyleSheet(f.read())
    main_window = HeatMapWindow()
    main_window.show()
    app.exec_()