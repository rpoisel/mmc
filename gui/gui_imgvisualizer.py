""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
" gui_imgvisualizer.py                                                       "
" author: Markus Mannel                                                      "
" date:   23.08.2011                                                         "
" brief:  Visualization of captured fragments                                "
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

# imports
from PySide.QtCore import *
from PySide.QtGui import *
# import logging
import logging
logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
        level=logging.DEBUG)


class CImgVisualizer(QGraphicsScene):
    """
    This class takes care of rendering the fragments retrieved from CFileCarver
    in a nice way
    """

    def __init__(self, ctx, pSize, pOffset, pFsType, parent=None):
        """
        @param ctx - CFileCarver containing fragment informations
        @param parent - Parent Widget container
        """
        super(CImgVisualizer, self).__init__(parent)
        #self.setSceneRect(0,0,500,500)
        self.setSceneRect(0, 0, self.parent().size().width(),
                self.parent().size().height())
        self.__mCtx = ctx
        self.__mScale = 1.0
        self.__mHeaderBrush = QBrush(Qt.red)
        self.__mNonHeaderBrush = QBrush(Qt.green)
        self.__mEmptyBrush = QBrush(Qt.green)
        self.__mHeaderPen = QPen(Qt.red)
        self.__mNonHeaderPen = QPen(Qt.green)
        self.__mSize = pSize
        self.__mOffset = pOffset
        self.__mFsType = pFsType
        # fragment under cursor, to draw
        self.__mHoverFragment = None
        # position to draw the tooltip at
        self.__mHoverPosition = None
        logging.info('Created CImgVisualizer')

    def mouseMoveEvent(self, pMouseEvent):
        """
        Overridden mouseMoveEvent
        @param pMouseEvent QMouseEvent
        """
        lPos = pMouseEvent.scenePos()
        self.updateHover(lPos)

    def updateHover(self, pPos):
        """
        @param pPos - position (mouse position) where to check
                      if a fragment is underneath
        """
        lSceneX, lSceneY, lSceneWidth, lSceneHeight = self.getOffsets()
        #calculate the fragment under cursor
        # w of 1 byte in pixels
        lWidth = lSceneWidth / float(self.__mSize)
        # current position in bytes
        lX = (pPos.x() - lSceneX) / lWidth
        if self.__mCtx.fragments is not None:
            for lFrag in self.__mCtx.fragments:
                if lX >= lFrag.mOffset and lX <= lFrag.mOffset + lFrag.mSize:
                    #logging.info('Paint tooltip')
                    self.__mHoverFragment = lFrag
                    self.__mHoverPosition = pPos
                    break
                else:
                    self.__mHoverFragment = None
                    self.__mHoverPosition = None
        self.update()

    def paintTooltip(self, pPainter, pRect):
        """
        @param pPainter QPainter used to draw
        @param pRect QRect not used - artifact of previous version
        """
        lSceneX, lSceneY, lSceneWidth, lSceneHeight = self.getOffsets()
        # if one pic is shown only, center the one at the mouse x
        # if two pics are shown, center both at the mouse x
        if not self.__mHoverFragment is None:
            if hasattr(self.__mHoverFragment, "mPicBegin"):
                lImgBegin = self.__mHoverFragment.mPicBegin
            else:
                lImgBegin = None
            if hasattr(self.__mHoverFragment, "mPicEnd"):
                lImgEnd = self.__mHoverFragment.mPicEnd
            else:
                lImgEnd = None
            lBeginX = self.__mHoverPosition.x()
            lEndX = self.__mHoverPosition.x()
            lY = self.__mHoverPosition.y()

            if not lImgBegin is None and len(lImgBegin) > 0:
                lImgBegin = QImage(lImgBegin)
            else:
                lImgBegin = None
            if not lImgEnd is None and len(lImgEnd) > 0:
                lImgEnd = QImage(lImgEnd)
            else:
                lImgEnd = None
            # adjust the pictures to center them around the mouse cursor
            # TODO: adjust to the right boundaries if the picture would
            # be drawn outside of lSceneX+lSceneWidth
            lTmpHeight = 0
            if not lImgBegin is None and lImgEnd is None:
                #logging.info("Adjust only begin pic")
                lBeginX = lBeginX - lImgBegin.width() / 2.0
                if lBeginX < lSceneX:
                    lBeginX = lSceneX + 1
                lTmpHeight = lImgBegin.height()
            elif lImgBegin is None and not lImgEnd is None:
                #logging.info("Adjust only end pic")
                lEndX = lEndX - lImgEnd.width() / 2.0
                if lEndX < lSceneX:
                    lEndX = lSceneX + 1
                lTmpHeight = lImgEnd.height()
            elif not lImgBegin is None and not lImgEnd is None:
                #logging.info("Adjust begin and end pic")
                lBeginX = lBeginX - lImgBegin.width()
                if lBeginX < lSceneX:
                    lBeginX = lSceneX + 1
                    lEndX = lSceneX + 1 + lImgBegin.width()
                lTmpHeight = lImgEnd.height()
                if lImgBegin.height() > lImgEnd.height():
                    lTmpHeight = lImgBegin.height()
            # adjust y position
            if lTmpHeight > lSceneHeight:
                lY = lSceneY + 1
            elif lY < lSceneY:
                lY = lSceneY + 1
            elif lY + lTmpHeight > lSceneHeight + lSceneY:
                lY = lSceneY + lSceneHeight - lTmpHeight

            if lImgBegin is not None and lImgEnd is not None:
                # adjust x position
                if lBeginX > (lSceneX + lSceneWidth -
                        lImgEnd.width() - lImgBegin.width()):
                    lBeginX = lSceneX + lSceneWidth - \
                            lImgEnd.width() - lImgBegin.width()
                pPainter.drawImage(lBeginX, lY, lImgBegin)
            if lImgEnd is not None:
                # adjust x position
                if lEndX > (lSceneX + lSceneWidth - lImgEnd.width()):
                    lEndX = lSceneX + lSceneWidth - lImgEnd.width()
                pPainter.drawImage(lEndX, lY, lImgEnd)

    def drawBackground(self, pPainter, pRect):
        """
        This method draws the fragments according to given offsets
        @param pPainter QPainter used to draw
        @param pRect not used - artifact from previous version
        """
        lSceneX, lSceneY, lSceneWidth, lSceneHeight = self.getOffsets()
        self.setSceneRect(lSceneX, lSceneY, lSceneWidth, lSceneHeight)
        #pPainter.fillRect(lSceneX, lSceneY, lSceneWidth, lSceneHeight,Qt.cyan)
        pPainter.drawRect(lSceneX, lSceneY, lSceneWidth, lSceneHeight)
        lStartX = 0
        lStartY = 0
        lEndX = self.parent().size().width() - lStartX
        lEndY = self.parent().size().height() - lStartY

        # self.parent().size().width() / float(self.__mSize)
        lWidth = lSceneWidth / float(self.__mSize)
        # self.parent().size().height()
        lHeight = lSceneHeight

        try:
            for lFrag in self.__mCtx.fragments:
                lColor = None
                if lFrag.mIsHeader:
                    lColor = QColor(255, 127, 127)
                else:
                    lColor = QColor(127, 127, 255)
                lFrameWidth = lWidth * lFrag.mSize
                pPainter.fillRect(lSceneX + (lFrag.mOffset * lWidth) + 1,
                        lSceneY + 1, lFrameWidth, lHeight - 1, lColor)
        except TypeError, pExc:
            # sometimes this callback is invoked when this object is not ready
            pass

    def drawForeground(self, pPainter, pRect):
        """
        This method draws the scale and the tooltips
        @param pPainter QPainter used to draw
        @param pRect QRect passed to
               CImgVisualizer#paintTooltip(object, object)
        """
        self.paintScale(pPainter)
        self.paintTooltip(pPainter, pRect)

    def paintScale(self, pPainter):
        """
        This method draws a scale at the bottom
        @param pPainter QPainter used to draw the scale
        """
        lSceneX, lSceneY, lSceneWidth, lSceneHeight = self.getOffsets()
        pPainter.drawText(lSceneX - 12, lSceneY + lSceneHeight + 12, str(0))
        lStrWidth = pPainter.fontMetrics().width(str(self.__mSize)) / 2.0
        pPainter.drawText(lSceneX + lSceneWidth - lStrWidth,
                lSceneY + lSceneHeight + 12, str(self.__mSize))
        if self.__mOffset > 0:
            pPainter.drawText(lSceneX + ((
                lSceneWidth / float(self.__mSize)) * self.__mOffset),
                lSceneY + lSceneHeight + 12, str(self.__mOffset))
            pPainter.drawLine(lSceneX + ((
                lSceneWidth / float(self.__mSize)) * self.__mOffset),
                lSceneY + lSceneHeight - 10,
            lSceneX + ((lSceneWidth / float(self.__mSize)) * self.__mOffset),
            lSceneY + lSceneHeight)

    def getOffsets(self):
        """
        Calculates offsets used to paint everything at the right position
        """
        #TODO: change fontsize to varying if something looks awkward
        lFontSize = 32
        lSceneX = self.parent().size().width() * float(0.1)
        #self.parent().size().height() + lFontSize
        lSceneY = lFontSize
        lSceneWidth = self.parent().size().width() - lSceneX
        lSceneHeight = self.parent().size().height() - lSceneY
        return (lSceneX, lSceneY, lSceneWidth, lSceneHeight)

#Test - better do not try it ; ) was just for quick evaluating
if __name__ == '__main__':
    import sys

    class MainWindow(QMainWindow):
        def __init__(self, parent=None):
            super(MainWindow, self).__init__()
            self.resize(800, 600)
            self.__mImageView = QGraphicsView(self)
            self.__mImageView.setSceneRect(0, 0, 800, 600)
            self.__mImgVisualizer = CImgVisualizer(self)
            self.__mImageView.setScene(self.__mImgVisualizer)

    app = QApplication(sys.argv)
    frame = MainWindow()
    frame.show()
    sys.exit(app.exec_())

