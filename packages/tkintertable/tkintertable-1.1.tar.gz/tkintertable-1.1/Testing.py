#!/usr/bin/env python
"""
    Created Oct 2008
    Table Testing module
    Copyright (C) Damien Farrell

    This program is free software; you can redistribute it and/or
    modify it under the terms of the GNU General Public License
    as published by the Free Software Foundation; either version 2
    of the License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, write to the Free Software
    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""

import random, string
from Tkinter import *
from Tables import TableCanvas
from TableModels import TableModel

"""Testing general functionality of tables"""

class App:
    def __init__(self, master):
        self.main = Frame(master)
        self.main.pack(fill=BOTH,expand=1)
        master.geometry('600x400+200+100')

def createRandomStrings(l,n):
    """create list of l random strings, each of length n"""
    names = []
    for i in range(l):
        val = ''.join(random.choice(string.ascii_lowercase) for x in range(n))
        names.append(val)
    return names

def createData(rows=20, cols=5):
    """Creare random dict for test data"""

    data = {}
    names = createRandomStrings(rows,16)
    colnames = createRandomStrings(cols,5)
    for n in names:
        data[n]={}
        data[n]['label'] = n
    for c in range(0,cols):
        colname=colnames[c]
        vals = [round(random.normalvariate(100,50),2) for i in range(0,len(names))]
        vals = sorted(vals)
        i=0
        for n in names:
            data[n][colname] = vals[i]
            i+=1
    return data

def GUITest(root):
    """Setup a table and populate it with data"""

    app = App(root)
    master = app.main
    model = TableModel()
    data = createData(40)
    #import after model created
    #print data
    model.importDict(data)
    from newtable import LargeTable
    table = TableCanvas(master, model,
                        cellwidth=60, cellbackgr='#e3f698',
                        thefont=('Arial',12),rowheight=18, rowheaderwidth=30,
                        rowselectedcolor='yellow', editable=True)
    table.createTableFrame()
    #remove cols
    model.deleteColumns([0])
    model.deleteRows(range(0,2))
    table.redrawTable()
    #add rows and cols
    table.addRow(1,label='aaazzz')
    table.addRow(label='bbb')
    table.addRow(**{'label':'www'})
    table.addColumn('col6')
    model.data[1]['col6']='TEST'
    table.redrawTable()
    #change col labels
    model.columnlabels['col6'] = 'new label'
    #set and get selections
    table.setSelectedRow(2)
    table.setSelectedCol(1)
    table.setSelectedCells(1,80,2,4)
    #print table.getSelectionValues()
    #table.plot_Selected(graphtype='XY')
    #save data
    model.save('test.table')
    #load new data
    table.load('test.table')
    print 'GUI tests done'
    #root.after(2000, root.quit)
    return

def main():
    root = Tk()
    GUITest(root)
    root.mainloop()
    #loadSaveTest()

if __name__ == '__main__':
    main()
