"""
 CASH STOCK REPORTER v1.0 by z3soft 
 QT desktop application. 
 It connects to the http://www.nbp.pl, retrieves a 30 last cash stocks and prints a plot.
 Written just for QT exercise.
 
 See HISTORY FOR history information.
 
read http://www.nbp.pl/kursy/xml/dir.txt 
 'xnnnzrrmmdd.xml'

 x - letter for type of table determination

    a - table for average stocks
    b - table for average stocks for unchanged cash
    c - table for average stocks of buy/sold cash
    h - table for stocks unit of accounts
"""

import sys
import urllib
import xml.dom.minidom
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from matplotlib.figure import Figure

NAME = 'CASH STOCK REPORTER v1.0'
AUTHOR = 'z3soft <http://z3soft.blogspot.de>'
HISTORY = """
History of changes:
v0.3 - working QT with CASH typed in the text field
v0.4 - working QT with CASE selected from drop down menu
v0.5 - changed to cash plot
v0.6 - menu expanded with preferences entry: 
	plot color, plot style
v0.7 - remove color/style slider
v1.0 - official version
	 
""" 
DEBUG = False

def log(_data, mode='normal'):
	""" loggin method. Set DEBUG to True if debug data are needed """
	if mode == 'debug':
		if DEBUG:
			print _data
	else:
		print _data
			
class Stock(QMainWindow):
	""" main Stock class """
	
	def __init__(self, parent=None):
		log(NAME, 'debug')
		
		QMainWindow.__init__(self, parent)
		self.comboBox = QComboBox()				
		self.setWindowTitle(NAME)		
		self.create_menu()
		self.create_main_frame()
		self.create_status_bar()
		self.plotColor = 'r'
		self.plotStyle = ''
		self.noOfFiles = 30	
		self.mDict = dict()
		self.getData()
		self.comboBox.addItems(sorted(self.mDict.keys())) 				
		self.on_draw()
		
		log('Initialized ' + str(self.noOfFiles) + ' files...')			
		
	def on_draw(self):
		comboChoose = self.comboBox.currentText()
		
		cashName, mtply, values = self.getCash(comboChoose)
				
		self.data = map(float, values)
		
		self.axes.clear()
		self.axes.grid(self.grid_cb.isChecked())
					
		_y = self.data
		_x = range(len(self.data))
			
		self.axes.plot(_x, _y, self.plotColor + self.plotStyle, label=str(cashName))
		self.axes.legend()
				
		self.canvas.draw()

	def create_menu(self):      
		# ------------------ FILE MENU --------------------  
		self.file_menu = self.menuBar().addMenu("&File")

		load_file_action = self.create_action("&Save plot",
            shortcut="Ctrl+S", slot=self.save_plot, 
            tip="Save the plot")
		quit_action = self.create_action("&Quit", slot=self.close, 
            shortcut="Ctrl+Q", tip="Close the application")

		self.add_actions(self.file_menu, 
            (load_file_action, None, quit_action))
		# ------------------ PREFS MENU --------------------
		self.pref_menu = self.menuBar().addMenu('&Preferences')
		pref_action = self.create_action('&Options', 
			shortcut='Ctrl+O', slot = self.prefs,
			tip = 'Configure options') 
		self.add_actions(self.pref_menu, (pref_action,))

		# ------------------ HELP MENU --------------------
		self.help_menu = self.menuBar().addMenu("&Help")
		about_action = self.create_action("&About", 
            shortcut='F1', slot=self.on_about, 
            tip='About this application')

		self.add_actions(self.help_menu, (about_action,))

	def create_main_frame(self):
		self.main_frame = QWidget()
		
		# Create the mpl Figure and FigCanvas objects. 
		# 5x4 inches, 100 dots-per-inch
		#
		self.dpi = 100
		self.fig = Figure((5.0, 4.0), dpi=self.dpi)
		self.canvas = FigureCanvas(self.fig)
		self.canvas.setParent(self.main_frame)
		
		# Since we have only one plot, we can use add_axes 
		# instead of add_subplot, but then the subplot
		# configuration tool in the navigation toolbar wouldn't
		# work.
		#
		self.axes = self.fig.add_subplot(111)
		
		# Bind the 'pick' event for clicking on one of the bars
		#
		self.canvas.mpl_connect('pick_event', self.on_pick)
		
		# Create the navigation toolbar, tied to the canvas
		#
		self.mpl_toolbar = NavigationToolbar(self.canvas, self.main_frame)
		
		# Other GUI controls
		# 
		self.connect(self.comboBox, SIGNAL('currentIndexChanged(const QString&)'), self.on_draw)
		
		self.draw_button = QPushButton("&Draw")
		self.connect(self.draw_button, SIGNAL('clicked()'), self.on_draw)
		
		self.grid_cb = QCheckBox("Show &Grid")
		self.grid_cb.setChecked(False)
		self.connect(self.grid_cb, SIGNAL('stateChanged(int)'), self.on_draw)
				
		#
		# Layout with box sizers
		# 
		hbox = QHBoxLayout()
		
		for w in [  self.comboBox, self.draw_button, self.grid_cb]:
			hbox.addWidget(w)
			hbox.setAlignment(w, Qt.AlignVCenter)
		
		vbox = QVBoxLayout()
		vbox.addWidget(self.canvas)
		vbox.addWidget(self.mpl_toolbar)
		vbox.addLayout(hbox)
		
		self.main_frame.setLayout(vbox)
		self.setCentralWidget(self.main_frame)
	
	def create_status_bar(self):
		self.status_text = QLabel(NAME)
		self.statusBar().addWidget(self.status_text, 1)

	def create_action(  self, text, slot=None, shortcut=None, 
						icon=None, tip=None, checkable=False, 
						signal="triggered()"):
		action = QAction(text, self)
		if icon is not None:
			action.setIcon(QIcon(":/%s.png" % icon))
		if shortcut is not None:
			action.setShortcut(shortcut)
		if tip is not None:
			action.setToolTip(tip)
			action.setStatusTip(tip)
		if slot is not None:
			self.connect(action, SIGNAL(signal), slot)
		if checkable:
			action.setCheckable(True)
		return action
	
	def save_plot(self):
		file_choices = "PNG (*.png)|*.png"
		
		path = unicode(QFileDialog.getSaveFileName(self, 
						'Save file', '', 
						file_choices))
		if path:
			self.canvas.print_figure(path, dpi=self.dpi)
			self.statusBar().showMessage('Saved to %s' % path, 2000)

	def prefs(self):			
		self.statusBar().showMessage('Preferences')
		
		#
		# Pass the parent - self (the calling form) to the dialog
		# to take advantage of the fact that by default PyQt centers a dialog over
		# its parent and also because the dialogs that have a parent do not get a 
		# separate entry in the taskbar.
		#
		dialog = PropertitesDlg(self)
		#
		# Mark current color as selected
		#
		for k,v in PropertitesDlg.COLORS.items():
			if v == self.plotColor:
				_colorStr = k
				break
		_indexC = dialog.colorComboBox.findText(_colorStr)
		if _indexC != -1:
			dialog.colorComboBox.setCurrentIndex(_indexC)

		#
		# Mark current line style as selected
		#
		for k,v in PropertitesDlg.STYLES.items():
			if v == self.plotStyle:
				_styleStr = k
				break
		_indexS = dialog.styleComboBox.findText(_styleStr)
		if _indexS != -1:
			dialog.styleComboBox.setCurrentIndex(_indexS)
						#
		# Open a properties dumb dialog and grab results 
		#
		if dialog.exec_():			
			self.plotColor = PropertitesDlg.COLORS.get(str(dialog.colorComboBox.currentText()))		
			self.plotStyle = PropertitesDlg.STYLES.get(str(dialog.styleComboBox.currentText()))
			self.on_draw()
				
	def add_actions(self, target, actions):
		for action in actions:
			if action is None:
				target.addSeparator()
			else:
				target.addAction(action)
				
	def on_pick(self, event):
		# The event received here is of the type
		# matplotlib.backend_bases.PickEvent
		#
		# It carries lots of information, of which we're using
		# only a small amount here.
		# 
		box_points = event.artist.get_bbox().get_points()
		msg = "You've clicked on a bar with coords:\n %s" % box_points
		
		QMessageBox.information(self, "Click!", msg)
		
	def on_about(self):
		msg = '\n' + NAME + '\n\n' + AUTHOR + '\n' + HISTORY + '\n'

		QMessageBox.about(self, "About", msg.strip())
											
	def getData(self):
		
		_mDict = dict()
		
		log('Retrieving XML data from nbp.pl...', 'debug')
		try:
			fList = urllib.urlopen('http://www.nbp.pl/kursy/xml/dir.txt')	
			lines = fList.readlines()
			aLines = [ a for a in lines if a.startswith('a') ] # list of files, which starts with 'a'
	
			for line in aLines[len(aLines) - self.noOfFiles:]:
				line = line.strip()
				log('Retrieving XML data from http://www.nbp.pl/kursy/xml/' + line + '.xml', 'debug')
				xmlFile = urllib.urlopen('http://www.nbp.pl/kursy/xml/' + line + '.xml')	
				xmlData = xml.dom.minidom.parse(xmlFile)
	
				nodeList = xmlData.getElementsByTagName('numer_tabeli')
				number = nodeList[0].childNodes[0].nodeValue
				log('Table number: ' + number, 'debug')
	
				nodeList = xmlData.getElementsByTagName('data_publikacji')
				data = nodeList[0].childNodes[0].nodeValue
				log('Date of publication: ' + data ,'debug')
	
				#cNodes = xmlData.childNodes		
	
				for i in xmlData.getElementsByTagName('pozycja'):
					code = i.getElementsByTagName('kod_waluty')[0].childNodes[0].nodeValue
					name = i.getElementsByTagName('nazwa_waluty')[0].childNodes[0].nodeValue.encode("iso-8859-15", "replace")
					mtply = i.getElementsByTagName('przelicznik')[0].childNodes[0].nodeValue
					value = i.getElementsByTagName('kurs_sredni')[0].childNodes[0].nodeValue.replace(',', '.')
						
					try:
						_mDict[code].append(value)
					except KeyError:			 	
						_mDict[code] = []			
						_mDict[code].append(name)
						_mDict[code].append(mtply)
						_mDict[code].append(value)
												
			log(_mDict, 'debug')
		except Exception, err:
			log('Exception caught: ' + str(err))
			sys.exit(1)

		self.mDict = _mDict
	
	def getCash(self, cash):
		cash = str(cash)
		_name = self.mDict[cash][0]
		_mtply = self.mDict[cash][1]
		_values = self.mDict[cash][2:]
		
		return (_name, _mtply, _values)
		
class PropertitesDlg(QDialog):

	
	COLORS = { 	'BLUE':'b', 
				'GREEN':'g', 				
				'RED':'r',
				'CYAN':'c',
				'MAGENTA':'m',
				'YELLOW':'y',
				'BLACK':'k'}
	STYLES = {	'LINE':'',
				'CIRCLE':'o',
				'DIAMOND':'D',
				'HLINE':'_',
				'PLUS':'+',
				'PENTAGON':'p'}	
	
	def __init__(self, parent=None):
		super(PropertitesDlg, self).__init__(parent)
		
		#
		# Combo box for list of colors
		#
		colorLabel = QLabel("&Plot color:")
		self.colorComboBox = QComboBox()
		colorLabel.setBuddy(self.colorComboBox)
		self.colorComboBox.addItems(sorted(PropertitesDlg.COLORS.keys()))
		
		#
		# Combo box for list of line styles
		#
		styleLabel = QLabel("&Plot style:")
		self.styleComboBox = QComboBox()
		styleLabel.setBuddy(self.styleComboBox)
		self.styleComboBox.addItems(sorted(PropertitesDlg.STYLES.keys()))
				
		okButton = QPushButton('&OK')
		cancelButton = QPushButton('Cancel')
		
		buttonLayout = QHBoxLayout()
		buttonLayout.addStretch()
		buttonLayout.addWidget(okButton)
		buttonLayout.addWidget(cancelButton)
		
		#
		# Define layout
		#
		layout = QGridLayout()
		layout.addWidget(colorLabel, 0, 0)
		layout.addWidget(self.colorComboBox, 0, 1)
		layout.addWidget(styleLabel, 1, 0)
		layout.addWidget(self.styleComboBox, 1, 1)
		layout.addLayout(buttonLayout, 6, 0, 1, 3)
		self.setLayout(layout)
		
		self.connect(okButton, SIGNAL('clicked()'), self, SLOT("accept()"))
		self.connect(cancelButton, SIGNAL('clicked()'), self, SLOT("reject()"))		
		
		self.setWindowTitle("Properties")

	def getDir(self):		
		pathDBDirD = QFileDialog.getExistingDirectory(self, 'Open directory', '', QFileDialog.ShowDirsOnly)
		self.pathDBLineValue.setText(pathDBDirD)

def main():
	app = QApplication(sys.argv)
	s = Stock()		
	s.show()
	sys.exit(app.exec_())
	
if __name__ == "__main__":
	main()
		
	

