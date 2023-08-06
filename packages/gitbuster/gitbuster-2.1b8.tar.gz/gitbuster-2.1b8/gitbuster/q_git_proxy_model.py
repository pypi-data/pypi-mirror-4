# main_window.py
# Copyright (C) 2010 Julien Miotte <miotte.julien@gmail.com>
#
# This module is part of gitbuster and is released under the GPLv3
# License: http://www.gnu.org/licenses/gpl-3.0.txt

from PyQt4.QtGui import QSortFilterProxyModel


class QGitProxyModel(QSortFilterProxyModel):

    def __init__(self, parent):
        QSortFilterProxyModel.__init__(self, parent)

    def filterAcceptsRow(self, row, sourceParent):
        #model = self.sourceModel()
        #index = model.createIndex(row, 0, sourceParent)
        #print "hu"
        #if model.is_inserted_commit(index) and model.is_deleted(index):
        #    return False

        return True
