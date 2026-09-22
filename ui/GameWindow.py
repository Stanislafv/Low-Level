from __future__ import annotations

from PyQt6 import QtWidgets
from PyQt6.QtGui import QBrush, QColor, QPainter, QIcon, QPixmap
from PyQt6.QtCore import Qt, QRectF, QTimer
from PyQt6.QtWidgets import QWidget, QGraphicsScene, QGraphicsView, QListWidget, QListWidgetItem, QGraphicsRectItem

from PyQt6.QtOpenGLWidgets import QOpenGLWidget

from PyQt6 import QtCore

from base.functions import save, get_texture
from base.font import Font
from base.cursors import Cursor
from base.MusicPlayer import MusicPlayer
from base.folders import folder, block_config

from composites.Block import Block
from composites.Entity import Entity, entities

from ui.PauseMenu import PauseMenu

import terminal, time, applib, math

from base.composites import composites

from world.SectorManager import SectorManager

from components.Clickable import Clickable
from components.Updatable import Updatable
from components.Removable import Removable
from components.Placable import Placable
from components.Storable import Storable

from world.WorldManager import WorldManager
from world.WorldLoader import WorldLoader
from world.World import World

from ui.ResourcePanel import ResourcePanel

from typing import TYPE_CHECKING, Literal
if TYPE_CHECKING:
    from composites.StorageBlock import StorageBlock
    from ui.MainWindow import MainWindow

round = math.floor

class GameWindow(QWidget):
    def __init__(self, window:MainWindow, loader=WorldLoader):
        super().__init__()

        self.setWindowTitle("Low-Level")

        self.main_window:MainWindow = window
        
        self.scene:QGraphicsScene = QGraphicsScene()
        self.scene.setSceneRect(QRectF(0, 0, 8192, 8192))

        self.resource_panel = ResourcePanel(self)
        self.resource_panel.show()
        self.resource_panel.setAutoFillBackground(True)

        self.manager = WorldManager(self.scene, self.update_tool_panel, loader=loader, resource_panel=self.resource_panel)

        self.manager.current = World()
        assert self.manager.current is not None
        
        background_brush = QBrush(QColor(30, 30, 30))
        self.scene.setBackgroundBrush(background_brush)

        self.view = QGraphicsView(self.scene, self)
        self.view.setViewport(QOpenGLWidget())
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.view.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.BoundingRectViewportUpdate)

        self.view.setCacheMode(QGraphicsView.CacheModeFlag.CacheBackground)
        self.view.setOptimizationFlag(QGraphicsView.OptimizationFlag.DontSavePainterState, True)
        self.view.setOptimizationFlag(QGraphicsView.OptimizationFlag.DontAdjustForAntialiasing, True)

        self.view.setCursor(Cursor.Cursor)
        
        self.keys_pressed:set[int] = set()

        self.scale:int = 1

        self.view.wheelEvent = self.wheelEvent # type: ignore

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(16)

        self.view.setMouseTracking(True)

        central = QtWidgets.QHBoxLayout()

        central.addWidget(self.view)

        self.tool_panel = QListWidget()
        self.tool_panel.setIconSize(QtCore.QSize(64, 64))
        self.tool_panel.setGridSize(QtCore.QSize(96, 196))
        self.tool_panel.setViewMode(QListWidget.ViewMode.IconMode)
        self.tool_panel.setFlow(QListWidget.Flow.TopToBottom) 
        self.tool_panel.setWrapping(False)
        self.tool_panel.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.tool_panel.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.tool_panel.setDragEnabled(False)
        self.tool_panel.setFont(Font.Bold)
        self.tool_panel.setFixedWidth(200)
        self.tool_panel.setCursor(Cursor.Hand)

        self.last_time = time.time()

        if not self.manager.current.devmode:
            self.tool_names = {}
            for clt in [block_config, entities]:
                for name, value in clt.items():
                    if not value.get("relief", False) and not value.get("ignore_on_editor", False):
                        self.tool_names[name] = value
        else:
            self.tool_names = block_config
            self.tool_names.update(entities)

        self.tool_panel.setCurrentRow(0)

        self.update_tool_panel()

        self.target_scale:float = 1

        self.tool_panel.currentItemChanged.connect(self.on_tool_changed)

        central.addWidget(self.tool_panel)

        self.setLayout(central)

        self.overlay:QGraphicsRectItem|None = None

        self.vx = 0
        self.vy = 0
        self.max_speed = 10
        self.acceleration = 4

        self.pause_menu = PauseMenu(self)
        self.menu_active = None

    def update_tool_panel(self):
        if not hasattr(self, "tool_panel"):
            return
        
        self.tool_panel.clear()
        
        coef = folder.config.get("craft_coef", 1)

        for name, i in self.tool_names.items():
                    if not self.manager.current.devmode:
                        if name not in self.manager.current.opened:
                            continue
                    
                    pixmap = get_texture(name)
                    icon = QIcon(pixmap)
          
                    cost:dict = i.get("cost")
                    exc = ""
                    if cost is not None:
                        for namef, value in cost.items():
                            exc += f"\n{namef} x{int(value*coef)}"
        
                    item = QListWidgetItem(icon, f"{name.replace("_", " ").title()}{exc}")
                    item.setData(Qt.ItemDataRole.UserRole, name)
                    item.setToolTip(f"{name.replace("_", " ").title()}{exc}")

                    self.tool_panel.addItem(item)

    def _create_overlay(self):
        self.overlay = QGraphicsRectItem(0, 0, self.manager.current.sizeX*32, self.manager.current.sizeY*32)
        self.overlay.setBrush(QColor(0, 0, 0, 180))
        self.overlay.setZValue(100)  
        self.scene.addItem(self.overlay)
        self.overlay.hide()

    def blur(self):
        if self.overlay is None:
            self._create_overlay()
        self.overlay.setOpacity(0.95)
        self.overlay.show()

    def unblur(self):
        if self.overlay is not None:
            self.overlay.hide()

    @save
    def closeEvent(self, event):
        MusicPlayer.play("click_2")
        if self.manager.current_name is not None:
            self.manager.save(self.manager.current_name)
        self.pause_menu.Back()
        self.main_window.MenuWindow.show()
        return event.accept()
    
    @save
    def on_tool_changed(self, current, f):
        if current is not None:
            self.view.setFocus()
            MusicPlayer.play("click_1")
            self.manager.current.placing_block = current.data(Qt.ItemDataRole.UserRole)

    @save
    def mousePressEvent(self, event):
        if self.menu_active is not None:
            return
        
        scene_pos = self.view.mapToScene(event.pos())
        x, y = round(scene_pos.x()/32), round(scene_pos.y()/32)

        if event.button() == Qt.MouseButton.LeftButton:
            self.manager.current.click("left", x, y)
      
        elif event.button() == Qt.MouseButton.RightButton:
            self.manager.current.click("right", x, y)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            MusicPlayer.play("click_2")
            if self.menu_active is not None:
                self.menu_active.Back()
            else:
                self.pause_menu.Show()

        self.keys_pressed.add(event.nativeScanCode())
    
    def keyReleaseEvent(self, event):
        self.keys_pressed.discard(event.nativeScanCode())

    @save
    def update(self):
            self.now = time.time()
            dt = self.now - self.last_time 
            self.last_time = self.now

            self.update_cam(dt)
            self.manager.current.update(dt)

    def update_cam(self, dt):          
            if abs(self.target_scale - self.scale) > 0.01:
                old_scale = self.scale
                self.scale = self.scale + (self.target_scale - self.scale) * 6.0 * dt

                factor = self.scale / old_scale
                self.view.scale(factor, factor)

            dx:float = 0
            dy:float = 0

            if self.menu_active is None:
                if 17 in self.keys_pressed:
                    dy -= 1
                if 31 in self.keys_pressed:
                    dy += 1
                if 30 in self.keys_pressed:   
                    dx -= 1
                if 32 in self.keys_pressed:   
                    dx += 1

                if dx != 0 and dy != 0:
                    dx *= 0.7071
                    dy *= 0.7071

            target_vx = dx * self.max_speed
            target_vy = dy * self.max_speed
            
            self.vx += (target_vx - self.vx) * self.acceleration * dt
            self.vy += (target_vy - self.vy) * self.acceleration * dt
            
            if abs(self.vx) > 0.1 or abs(self.vy) > 0.1:
                current_x = self.view.horizontalScrollBar().value() # type: ignore
                current_y = self.view.verticalScrollBar().value() # type: ignore
                
                self.view.horizontalScrollBar().setValue(current_x + int(self.vx * dt * 60)) # type: ignore 
                self.view.verticalScrollBar().setValue(current_y + int(self.vy * dt * 60)) # type: ignore

    def wheelEvent(self, event):
        if self.menu_active is not None:
            return
        if event.angleDelta().y() > 0:
            self.target_scale *= 1.15
        else:
            self.target_scale /= 1.15
        
        self.target_scale = max(0.4, min(2.0, self.target_scale))

    def __repr__(self):
        return f"GameWindow(sizeX: {self.sizeX}, sizeY: {self.sizeY})"

    def show(self):
        self.main_window.widget.setCurrentIndex(1)
