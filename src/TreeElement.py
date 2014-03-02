from os.path import join

from gi.repository import Gtk

import Config


# TODO Update arrow when can not be collapsed
class TreeElement(Gtk.Box):

    """

    A Widget that always shows its primary widget and can show or hide
    its child TreeElements

    """

    def __init__(self, widget=None):
        """Create TreeElement object

        Args:
            widget (Gtk.Widget): If present, TreeElement will be created
            containing it as primary widget.

        """
        # Check args
        if widget is not None and not isinstance(widget, Gtk.Widget):
            raise TypeError("Type of widget should "
                            "be Gtk.Widget, not {}".format(type(widget)))

        # Initialise self
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)
        self._useArrow = True
        self._parent = None
        self._depth = 0

        # Create UI
        builder = Gtk.Builder()
        builder.add_from_file(join(Config.DESIGN_DIR, "TreeElement.glade"))
        self._primaryArea = builder.get_object("primaryArea")
        self._childrenRevealer = builder.get_object("childrenRevealer")
        self._arrowHolder = builder.get_object("arrowHolder")
        self._arrow = builder.get_object("arrow")
        self._primaryContentHolder = builder.get_object("primaryContentHolder")
        self._childrenHolder = builder.get_object("childrenHolder")

        self.add(self._primaryArea)
        self.add(self._childrenRevealer)

        # Add primary widget is present
        self._primaryWidget = widget
        if self._primaryWidget:
            self._primaryContentHolder.add(self._primaryWidget)

        # Connect signals
        handlers = {"toggle": self.toggle,
                    "primaryHolderActivate": self._on_primary_holder_activate}
        builder.connect_signals(handlers)

        self.show_all()


    def is_toggled_on(self):
        """Return if TreeElement is showing its child elements"""
        return self._childrenRevealer.get_reveal_child()


    def toggle(self, eventBox, _=None):
        """Toggle TreeElement"""
        arrowToggle = eventBox.get_child() == self._arrow and self._useArrow
        widgetToggle = (eventBox.get_child() != self._arrow
                        and not self._useArrow)
        if widgetToggle or arrowToggle:
            if self.is_toggled_on():
                self.toggle_off()
            else:
                self.toggle_on()


    def toggle_on(self):
        """Show child elements"""
        self._childrenRevealer.set_reveal_child(True)
        self._arrow.set(Gtk.ArrowType.DOWN, Gtk.ShadowType.NONE)


    def toggle_off(self):
        """Hide child elements"""
        self._childrenRevealer.set_reveal_child(False)
        self._arrow.set(Gtk.ArrowType.RIGHT, Gtk.ShadowType.NONE)


    def get_widget(self):
        """Return primary widget that is always shown"""
        return self._primaryContentHolder.get_child()


    def set_widget(self, widget):
        """Set primary widget that is always shown

        Args:
            widget (Gtk.Widget) : Widget to set as primary widget

        """
        if isinstance(widget, Gtk.Widget):
            oldWidget = self.get_widget()
            if oldWidget:
                self._primaryContentHolder.remove(oldWidget)
            self._primaryContentHolder.add(widget)
        else:
            raise TypeError("Type of widget should "
                            "be Gtk.Widget, not {}".format(type(widget)))


    def use_toggle_arrow(self, useArrow):
        """Set if an arrow is used to toggle_off

        If set to true, a small arrow at the left of the widget is
        used to toggle element. Otherwise, it can be toggled by clicking
        on it.

        """
        if useArrow == self._useArrow:
            # Nothing to do
            return
        elif useArrow:
            self._arrowHolder.add(self._arrow)
        else:
            self._arrowHolder.remove(self._arrow)
        self._useArrow = useArrow


    def add_child_element(self, childElement):
        """Add child to TreeElement

        Args:
            childElement (TreeElement): element to add

        """
        if isinstance(childElement, TreeElement):
            self._childrenHolder.add(childElement)
            childElement._parent = self
            self._fix_indentation()
        else:
            type_ = type(childElement)
            raise TypeError("Type of childElement should "
                            "be TreeElement, not {}".format(type_))


    def remove_child_element(self, childElement):
        """Remove child from TreeElement

        Args:
            childElement (TreeElement): element to remove

        """
        if childElement in self._childrenHolder.get_children():
            self._childrenHolder.remove(childElement)
        else:
            raise ValueError("{} not in child elements".format(childElement))


    def get_child_elements(self):
        """Return the list of child TreeElements"""
        return self._childrenHolder.get_children()


    def get_parent(self):
        """Return the parent TreeElement

        This may return None if no parent is present.

        """
        return self._parent


    def activate(self):
        """Activate primary content holder

        This function is called when the user clicks the primary content
        area and _useArrow is set to True. If _useArrow is set to False,
        this action will toggle the element instead. This method does
        nothing and should to be overridden by subclasses.

        """
        pass


    def activate_secondary(self):
        """Activate primary content holder

        This function is called when the user right clicks the primary content
        This method does nothing and should to be overriden by subclasses.

        """
        pass


    def get_all_children(self):
        """Return a list of self and children and their children and so on"""
        allChildren = [self]
        for child in self.get_child_elements():
            allChildren += child.get_all_children()
        return allChildren


    def _on_primary_holder_activate(self, eventBox, event):
        if event.button == 3:  # Right Click
            self.activate_secondary()
        elif event.button == 1:  # Left click
            if self._useArrow:
                self.activate()
            else:
                self.toggle(eventBox)


    def _has_visible_children(self):
        return self.is_toggled_on() and self.get_child_elements()


    def _fix_indentation(self):
        # This is used to recalculate indentation after add,
        # so that elements can be added in any order/replaced
        if self._parent:
            self._depth = self._parent._depth + 1
            leftMargin = self._depth * 6  # 6px indentation per level
            self._arrowHolder.set_margin_left(leftMargin)
        for childElement in self.get_child_elements():
            childElement._fix_indentation()
