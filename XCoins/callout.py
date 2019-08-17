# -*- coding: utf-8 -*-

from PySide2.QtCore import QPoint, QPointF, QRect, QRectF, Qt
from PySide2.QtGui import QColor, QFont, QFontMetrics, QPainterPath
from PySide2.QtWidgets import QGraphicsItem


class Callout(QGraphicsItem):
    """
        This class code was taken from \
        https://code.qt.io/cgit/qt/qtcharts.git/tree/examples/charts/callout/callout.cpp?h=5.13
    """

    def __init__(self, chart):
        QGraphicsItem.__init__(self, chart)

        self.chart = chart
        self.rect = QRectF()
        self.anchor = QPointF()
        self.text_rect = QRectF()
        self.text = ""
        self.font = QFont()

    def boundingRect(self):
        anchor = self.mapFromParent(self.chart.mapToPosition(self.anchor))

        rect = QRectF()

        rect.setLeft(min(self.rect.left(), anchor.x()))
        rect.setRight(max(self.rect.right(), anchor.x()))
        rect.setTop(min(self.rect.top(), anchor.y()))
        rect.setBottom(max(self.rect.bottom(), anchor.y()))

        return rect

    def paint(self, painter, option, widget):
        path = QPainterPath()

        path.addRoundedRect(self.rect, 5, 5)

        painter.setBrush(QColor(255, 255, 255))
        painter.drawPath(path)
        painter.drawText(self.text_rect, self.text)

    def set_anchor(self, point):
        self.anchor = point

    def updateGeometry(self):
        self.prepareGeometryChange()

        self.setPos(self.chart.mapToPosition(self.anchor) + QPoint(10, -50))

    def set_text(self, text):
        self.text = text

        metrics = QFontMetrics(self.font)

        self.text_rect = metrics.boundingRect(QRect(0, 0, 150, 150), Qt.AlignLeft, self.text)

        self.text_rect.translate(5, 5)

        self.prepareGeometryChange()

        self.rect = QRectF(self.text_rect.adjusted(-5.0, -5.0, 5.0, 5.0))
