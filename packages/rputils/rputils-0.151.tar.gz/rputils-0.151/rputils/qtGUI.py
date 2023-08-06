#!/usr/bin/env python
# Written by: DGC

# python imports
from PyQt4 import QtGui, QtCore

import sys
import time
import os

# local imports
import DiceRollers
import PdfViewer
import ProbabilityDensity
import ProgramUtils
import Resources.finder

#==============================================================================
class MainApp(QtGui.QApplication):

    def __init__(self):
        super(MainApp, self).__init__(sys.argv)
        self.window = MainWindow()

    def MainLoop(self):
        self.window.show()
        sys.exit(self.exec_())

#==============================================================================
class MainWindow(QtGui.QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        program = ProgramUtils.Program()

        self.setWindowTitle(
            program.info["name"] + " " + program.info["version"]
            )

        self.setWindowIcon(
            QtGui.QIcon(Resources.finder.find_image_file(program.info["icon"]))
            )
        self.center()

        self.dice_pool = DiceRollers.DicePool()

        self.file_dialog_dir = "."
        self.initialise_UI()

    def center(self):
        """ Centre the window in the screen. """
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def initialise_UI(self):
        """ Make all the widgets, toolbars and status bar. """
        self.dice_selecter = DiceSelecterDock()
        QtCore.QObject.connect(
            self.dice_selecter,
            QtCore.SIGNAL("dice_added"),
            self.dice_pool.add_dice
            )

        dice_pool_viewer = DicePoolViewer(self.dice_pool)

        QtCore.QObject.connect(
            self.dice_selecter,
            QtCore.SIGNAL("dice_added"),
            dice_pool_viewer.update_table
            )

        QtCore.QObject.connect(
            dice_pool_viewer,
            QtCore.SIGNAL("show_probability"),
            self.open_probability_window
            )
        self.setCentralWidget(dice_pool_viewer)

        dice_history = DiceHistoryDock()
        QtCore.QObject.connect(
            dice_pool_viewer,
            QtCore.SIGNAL("dice_rolled"),
            dice_history.update
            )
        QtCore.QObject.connect(
            dice_pool_viewer,
            QtCore.SIGNAL("reset"),
            dice_history.reset
            )

        # set the corner areas for docking
        self.setCorner(
            QtCore.Qt.TopLeftCorner,
            QtCore.Qt.LeftDockWidgetArea
            )
        self.setCorner(
            QtCore.Qt.BottomLeftCorner,
            QtCore.Qt.LeftDockWidgetArea
            )
        self.setCorner(
            QtCore.Qt.BottomRightCorner,
            QtCore.Qt.RightDockWidgetArea
            )
        self.setCorner(
            QtCore.Qt.TopRightCorner,
            QtCore.Qt.RightDockWidgetArea
            )

        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.dice_selecter)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, dice_history)
        self.make_menu_bar()

    def make_menu_bar(self):
        pdf_menu = self.menuBar().addMenu("&PDF")
        open_local_pdf = pdf_menu.addAction("&Open Local PDF")
        open_local_pdf.setIcon(
            QtGui.QIcon(Resources.finder.find_image_file("Pdf.png"))
            )
        QtCore.QObject.connect(
            open_local_pdf,
            QtCore.SIGNAL("triggered()"),
            self.open_local_pdf
            )

        open_remote_pdf = pdf_menu.addAction("PDF From &URL")
        open_remote_pdf.setIcon(
            QtGui.QIcon(Resources.finder.find_image_file("Pdf.png"))
            )
        QtCore.QObject.connect(
            open_remote_pdf,
            QtCore.SIGNAL("triggered()"),
            self.open_remote_pdf
            )

        tool_menu = self.menuBar().addMenu("&Tools")
        add_dice = tool_menu.addAction("&New Dice")
        # use a D6 icon
        add_dice.setIcon(
            QtGui.QIcon(Resources.finder.find_image_file("D6.png"))
            )
        QtCore.QObject.connect(
            add_dice,
            QtCore.SIGNAL("triggered()"),
            self.raise_dice_creator
            )

        restore_defaults = tool_menu.addAction(
            "&Restore Default Configuration"
            )
        restore_defaults.setIcon(
            QtGui.QIcon(Resources.finder.find_image_file("Restore.png"))
            )
        QtCore.QObject.connect(
            restore_defaults,
            QtCore.SIGNAL("triggered()"),
            self.restore_default_config
            )
        context_menu = self.createPopupMenu()
        context_menu.setTitle("&View")
        self.menuBar().addMenu(context_menu)

    def restore_default_config(self):
        message_box = QtGui.QMessageBox()
        message_box.setText("Reset the configuration?")
        message_box.setWindowTitle("Configuration Reset")

        message_box.setWindowIcon(
            QtGui.QIcon(Resources.finder.find_image_file(program.info["icon"]))
            )

        current_session = QtGui.QPushButton("Just for this session")
        message_box.addButton(
            current_session,
            QtGui.QMessageBox.AcceptRole
            )
        always = QtGui.QPushButton("Permanently")
        message_box.addButton(always, QtGui.QMessageBox.DestructiveRole)

        no = QtGui.QPushButton("Cancel")
        message_box.addButton(no, QtGui.QMessageBox.RejectRole)
        
        message_box.exec_()
        reset = False
        if (message_box.clickedButton() == current_session):
            reset = True
        elif (message_box.clickedButton() == always):
            reset = True
            custom_xml = Resources.finder.find_resource_file("Custom.xml")
            if (os.path.isfile(custom_xml)):
                os.remove(custom_xml)
        if (reset):
            program = ProgramUtils.Program()
            program.restore_defaults()
            self.dice_selecter.dice_selecter.set_library(program.dice_library)

    def raise_dice_creator(self):
        creator = DiceCreator()
        if (creator.exec_()):
            dice = creator.dice
            # add it to the library, and Config.xml
            library = ProgramUtils.Program().dice_library
            library.add_dice(dice)
            # reset the dice selector
            self.dice_selecter.dice_selecter.set_library(library)

    def open_local_pdf(self):
        dialog = QtGui.QFileDialog()
        dialog.setFileMode(QtGui.QFileDialog.ExistingFile)
        file_extensions = "PDF (*.pdf)"
        file_name = dialog.getOpenFileName(
            self,
            "PDF",
            self.file_dialog_dir,
            file_extensions
            )
        if (file_name):
            # this means the dialog was not cancelled
            # save the directory
            self.file_dialog_dir = os.path.dirname(str(file_name))
            # make QUrl from the name
            url = QtCore.QUrl.fromLocalFile(file_name)
            # view the pdf
            self.__view_pdf(url)

    def open_remote_pdf(self):
        # get a Url
        dialog = QtGui.QInputDialog()
        url_as_text = dialog.getText(
            self,
            "PDF From URL",
            "Enter URL"
            )
        # this returns a tuple of the form (text entered, ok clicked)
        if (url_as_text[1]):
            # if ok was clicked
            url = QtCore.QUrl(url_as_text[0])
            self.__view_pdf(url)

    def __view_pdf(self, url):
        # open the Url in the PdfViewer
        viewer = PdfViewer.ViewerDock()
        viewer.set_url(url)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, viewer)
        viewer.setFloating(True)

    def open_probability_window(self):
        self.probability_window = ProbabilityDensityDock(self.dice_pool)
        self.addDockWidget(
            QtCore.Qt.LeftDockWidgetArea, 
            self.probability_window
            )
        self.probability_window.setFloating(True)

#==============================================================================
class DiceSelecterDock(QtGui.QDockWidget):

    def __init__(self):
        super(DiceSelecterDock, self).__init__("Dice Selecter")
        self.dice_selecter = DiceSelecter()
        QtCore.QObject.connect(
            self.dice_selecter,
            QtCore.SIGNAL("dice_added"),
            self.emit_signal
            )
        self.setWidget(self.dice_selecter)

    def emit_signal(self, dice_name):
        self.emit(QtCore.SIGNAL("dice_added"), dice_name)

#==============================================================================
class DiceSelecter(QtGui.QWidget):

    def __init__(self):
        super(DiceSelecter, self).__init__()
        self.layout = QtGui.QVBoxLayout()

        library = ProgramUtils.Program().dice_library
        self.set_library(library)

        # make the window wider
        self.setMinimumWidth(120)

    def set_library(self, library):
        # clear the current library first
        for i in range(self.layout.count()):
           self.layout.itemAt(i).widget().close()
        # sort the names on the numbers of sides of the library item.
        names = sorted(
            library.keys(),
            lambda x,y: cmp(library[x].sides, library[y].sides)
            )
        for name in names:
            self.append_dice(library[name])

    def append_dice(self, dice):
        # make the button
        button = QtGui.QToolButton()

        # if there is a label, set it as the tool tip
        if (not dice.label is None):
            button.setToolTip(dice.label)

        # if there is an image set it as the icon, otherwise set the label as
        # the text
        if (not dice.image is None):
            button.setIcon(QtGui.QIcon(dice.image))
        else:
            button.setText(dice.label)

        button.clicked.connect(lambda event: self.append_event(dice))

        # make the buttons and button icon larger
        button.setMinimumSize(QtCore.QSize(60, 60))
        button.setIconSize(QtCore.QSize(60, 60))

        self.layout.addWidget(button, 0, QtCore.Qt.AlignHCenter)
        self.setLayout(self.layout)

    def append_event(self, dice):
        self.emit(QtCore.SIGNAL("dice_added"), dice.label)

#==============================================================================
class DicePoolViewer(QtGui.QWidget):

    def __init__(self, dice_pool):
        super(DicePoolViewer, self).__init__()
        self.dice_pool = dice_pool

        self.table = QtGui.QTableWidget(0, 4, self)
        self.table.setMinimumSize(QtCore.QSize(400, 200))
        self.initialise_table()

        roll_button = QtGui.QPushButton("&Roll")
        hotkey = QtGui.QShortcut("Enter", self)
        QtCore.QObject.connect(
            hotkey,
            QtCore.SIGNAL("activated()"),
            self.roll
            )
        roll_button.clicked.connect(self.roll)

        reset_button = QtGui.QPushButton("Reset")
        reset_button.clicked.connect(self.reset)

        vertical_layout = QtGui.QVBoxLayout()
        vertical_layout.addWidget(self.table, 2, QtCore.Qt.AlignHCenter)
        
        self.probablity = QtGui.QLabel()
        self.update_probablity()

        distribution_button = QtGui.QPushButton("Show Probabilities")
        distribution_button.clicked.connect(self.show_probabilities)

        middle_layout = QtGui.QHBoxLayout()
        middle_layout.addWidget(self.probablity)
        middle_layout.addWidget(distribution_button)
        
        vertical_layout.addLayout(middle_layout)

        button_layout = QtGui.QHBoxLayout()
        button_layout.addWidget(roll_button)
        button_layout.addWidget(reset_button)

        vertical_layout.addLayout(button_layout, 0)

        self.setLayout(vertical_layout)

    def initialise_table(self):
        self.table.setRowCount(0)
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(
            ["Dice", "Number", "Add", "Remove"]
            )
        self.table.verticalHeader().hide()

        self.table.horizontalHeader().setStretchLastSection(False)

    def update_table(self):
        self.table.clear()
        self.initialise_table()

        for dice in self.dice_pool:
            # add the dice label/image to the table
            self.table.setRowCount(self.table.rowCount() + 1)

            label = None
            if (not dice.image is None):
                label = QtGui.QTableWidgetItem(
                    QtGui.QIcon(dice.image),
                    dice.label
                    )
            else:
                label = QtGui.QTableWidgetItem(dice.label)
            label.setFlags(QtCore.Qt.ItemIsEnabled)
            row_number = self.table.rowCount() - 1
            self.table.setItem(row_number, 0, label)

            # add the number of dice in the pool
            number_label = QtGui.QTableWidgetItem(str(self.dice_pool[dice]))
            number_label.setFlags(QtCore.Qt.ItemIsEnabled)
            number_label.setTextAlignment(QtCore.Qt.AlignCenter)
            self.table.setItem(row_number, 1, number_label)

            # put add button in table
            add = AddButton(dice.label)
            QtCore.QObject.connect(
                add,
                QtCore.SIGNAL("add_dice"),
                self.add_dice
                )
            self.table.setCellWidget(row_number, 2, add)

            # add remove button to table
            remove = RemoveButton(dice.label)
            QtCore.QObject.connect(
                remove,
                QtCore.SIGNAL("remove_dice"),
                self.remove_dice
                )
            self.table.setCellWidget(row_number, 3, remove)

            self.update_probablity()

    def add_dice(self, dice_name):
        self.dice_pool.add_dice(dice_name)
        self.update_table()

    def remove_dice(self, dice_name):
        self.dice_pool.remove_dice(dice_name)
        self.update_table()

    def update_probablity(self):
        label = "Expected Value: " + str(self.dice_pool.expected) + "\n"
        label += "Minimum: " + str(self.dice_pool.minimum) + "\n"
        label += "Maximum: " + str(self.dice_pool.maximum)
        self.probablity.setText(label)

    def roll(self):
        value = self.dice_pool.roll()
        self.emit(QtCore.SIGNAL("dice_rolled"), value)

    def reset(self):
        self.dice_pool.clear()
        self.table.clear()
        self.initialise_table()
        self.update_probablity()
        self.emit(QtCore.SIGNAL("reset"))

    def show_probabilities(self):
        self.emit(QtCore.SIGNAL("show_probability"))

#==============================================================================
class DiceHistoryDock(QtGui.QDockWidget):

    def __init__(self):
        super(DiceHistoryDock, self).__init__("Dice Rolls")
        self.setFeatures(
            QtGui.QDockWidget.DockWidgetFloatable |
            QtGui.QDockWidget.DockWidgetMovable
            )
        self.history = DiceHistory()
        self.setWidget(self.history)

    def update(self, summery):
        self.history.update(summery)

    def reset(self):
        self.history.reset()

#==============================================================================
class DiceHistory(QtGui.QWidget):

    def __init__(self):
        super(DiceHistory, self).__init__()

        self.output = QtGui.QTextEdit()
        self.output.setReadOnly(True)

        layout = QtGui.QHBoxLayout()
        layout.addWidget(self.output)
        self.setLayout(layout)

    def update(self, summery):
        # return the cursor the the begining
        self.output.setTextCursor(QtGui.QTextCursor(self.output.document()))
        self.output.insertHtml(
            "<p>" +
            time.strftime("%d-%m %H:%M", time.localtime()) +
            " - " +
            "<FONT COLOR=\"#FF0000\">" +
            str(summery) +
            "</FONT>" +
            "<br><br></p>"
            )

    def reset(self):
        # return the cursor the the begining
        self.output.setTextCursor(QtGui.QTextCursor(self.output.document()))
        self.output.insertHtml(
            "<p>" +
            time.strftime("%d-%m %H:%M", time.localtime()) +
            " - " +
            "<FONT COLOR=\"#FF0000\">" +
            "Reset" +
            "</FONT>" +
            "<br><br></p>"
            )

#==============================================================================
class DiceCreator(QtGui.QDialog):

    def __init__(self):
        super(DiceCreator, self).__init__()
        self.setWindowTitle("Dice Creator")

        self.setWindowIcon(
            QtGui.QIcon(Resources.finder.find_image_file(program.info["icon"]))
            )
        self.setModal(True)

        self.initialise_ui()
        self.dice = None
        self.image = None
        self.file_dialog_dir = "."

    def initialise_ui(self):
        name = QtGui.QLabel("Dice name: ")
        self.name_input = QtGui.QLineEdit()

        sides = QtGui.QLabel("Number of Sides: ")
        self.sides_input = QtGui.QLineEdit()

        self.image_button = QtGui.QPushButton("Select Image")
        self.image_button.clicked.connect(self.find_image)

        ok_button = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok)
        ok_button.clicked.connect(self.accept)

        cancel_button = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Cancel)
        cancel_button.clicked.connect(self.reject)

        layout = QtGui.QGridLayout()
        layout.addWidget(name, 0, 0)
        layout.addWidget(self.name_input, 0, 1)

        layout.addWidget(sides, 1, 0)
        layout.addWidget(self.sides_input, 1, 1)

        layout.addWidget(self.image_button, 2, 0, 1, 2)

        layout.addWidget(ok_button, 3, 0)
        layout.addWidget(cancel_button, 3, 1)

        self.setLayout(layout)

    def accept(self):
        if (self.validate()):
            self.dice = ProgramUtils.DiceLibraryEntry(
                str(self.name_input.text()),
                int(self.sides_input.text()),
                self.image
                )
            super(DiceCreator, self).accept()

    def validate(self):
        ok = True
        error = ""
        if (self.name_input.text() == ""):
            error = "Undefined dice name."
            ok = False
        else:
            if (self.sides_input.text() == ""):
                error =  "Undefined number of sides."
                ok = False
            else:
                try:
                    sides = int(self.sides_input.text())
                    if (sides <= 0):
                        error = "Dice cannot have fewer than 0 sides."
                        ok = False
                except ValueError:
                    error = "Dice cannot have \""
                    error += str(self.sides_input.text())
                    error += "\" sides."
                    ok = False
        if (not ok):
            error_dialog = QtGui.QErrorMessage(self)
            error_dialog.showMessage(error)
            error_dialog.exec_()
        return ok

    def find_image(self):
        dialog = QtGui.QFileDialog()
        dialog.setFileMode(QtGui.QFileDialog.ExistingFile)
        file_extensions = "Images (*.bmp *.gif *.jpg *.png);;All files (*)"
        file_name = dialog.getOpenFileName(
            self,
            "Find Image",
            self.file_dialog_dir,
            file_extensions
            )
        if (file_name):
            # this means the dialog was not cancelled
            # save the directory
            self.file_dialog_dir = os.path.dirname(str(file_name))
            self.image = str(file_name)
            self.image_button.setText(os.path.basename(self.image))

#==============================================================================
class RemoveButton(QtGui.QToolButton):

    def __init__(self, dice_name):
        super(RemoveButton, self).__init__()
        self.dice_name = dice_name

        self.setMaximumSize(QtCore.QSize(40, 40))

        self.setIcon(
            QtGui.QIcon(Resources.finder.find_image_file("Remove.png"))
            )
        self.setToolTip("Remove 1 " + dice_name)
        self.clicked.connect(self.send_remove_call)

    def send_remove_call(self):
        self.emit(QtCore.SIGNAL("remove_dice"), self.dice_name)

#==============================================================================
class AddButton(QtGui.QToolButton):

    def __init__(self, dice_name):
        super(AddButton, self).__init__()
        self.dice_name = dice_name

        self.setMaximumSize(QtCore.QSize(40, 40))

        self.setIcon(
            QtGui.QIcon(Resources.finder.find_image_file("Add.png"))
            )
        self.setToolTip("Add 1 " + dice_name)
        self.clicked.connect(self.send_add_call)

    def send_add_call(self):
        self.emit(QtCore.SIGNAL("add_dice"), self.dice_name)

#==============================================================================
class ProbabilityDensityDock(QtGui.QDockWidget):

    def __init__(self, dice_pool):
        super(ProbabilityDensityDock, self).__init__("Probability Density")
        self.density_widget = ProbabilityDensityWidget(dice_pool)
        self.setWidget(self.density_widget)        

#==============================================================================
class ProbabilityDensityWidget(QtGui.QWidget):

    def __init__(self, dice_pool):
        super(ProbabilityDensityWidget, self).__init__()
        self.dice_pool = dice_pool
        self.density = ProbabilityDensity.ProbabilityDensity(self.dice_pool)
        self.setMinimumSize(QtCore.QSize(550, 350))
        
    def update(self):
        self.density.make_density()
        self.repaint()
        
    def paintEvent(self, e):
        # if the probability is too much to calculate
        if (not self.density.density is None):
            painter = QtGui.QPainter()
            painter.begin(self)
            self.draw_graph(painter)
            painter.end()
        
    def draw_graph(self, painter):
        pen = QtGui.QPen(QtCore.Qt.black, 2, QtCore.Qt.SolidLine)

        painter.setPen(pen)
        painter.setFont(QtGui.QFont("decorative", 8))
        
        # get the maximum density
        highest = max(
            self.density.density, 
            key = lambda x: self.density.density[x]
            )
        highest = self.density.density[highest]
        # the scale in y, fit to 240
        scale = 240 / highest
        if (scale < 1):
            scale = 1
        # the number of probabilities
        probability_number = len(self.density.density.keys())
        # the space between numbers in x, fit to 480
        space = 480 / probability_number
        # the value where the x axis is. highest goes down one as the graph 
        # starts from 0
        base = space + ((highest) * scale)
        # draw the chart
        for i, value in enumerate(self.density.density.keys()):
            number = self.density.density[value]
            painter.drawLine(
                space * (i + 1),
                base, 
                space * (i + 1),
                base - (scale * number)
                )
            painter.drawText(space * (i + 1), base + 20, str(value))

        # draw y axis
        painter.drawLine(space / 2, space, space / 2, base)
        # draw x axis
        painter.drawLine(
            space / 2,
            base, 
            space * (probability_number + 1.5), 
            base
            )

    def draw_scale(self):
        total = self.density.possibilities
        for i in range(1, highest):
            painter.drawLine(
                space / 2,
                base - (scale * i),
                space, 
                base - (scale * i)
                )
            painter.drawText(space, base - (scale * i), str(i / float(total)))
