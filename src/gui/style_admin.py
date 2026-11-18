"""
This module contains the StyleAdmin class, which manages the styling of the HDL-FSM-Editor application.
"""

from tkinter import ttk


class StyleAdmin:
    """Manage the styling of the HDL-FSM-Editor application."""

    def __init__(self, root) -> None:
        """Initialize the style admin for the application."""
        self.font_name = "DejaVu Sans Mono"
        self.style = ttk.Style(root)
        self.style.theme_use("default")
        # self.style.theme_use("clam")
        # style.theme_use('winnative')
        # style.theme_use('alt')
        # style.theme_use('classic')
        # style.theme_use('vista')
        # style.theme_use('xpnative')
        self.style.configure("Window.TFrame", foreground="black", background="PaleTurquoise2")
        self.style.configure("Window.TLabel", foreground="black", background="PaleTurquoise2")
        self.style.configure("WindowSelected.TFrame", foreground="black", background="PaleTurquoise3")
        self.style.configure("WindowSelected.TLabel", foreground="black", background="PaleTurquoise3")

        # Configure the custom style for the TEntry widget:
        self.style.element_create("plain.field", "from", "clam")
        self.style.layout(
            "My.TEntry",
            [
                (
                    "Entry.plain.field",
                    {
                        "children": [
                            ("Entry.padding", {"children": [("Entry.textarea", {"sticky": "nswe"})], "sticky": "nswe"})
                        ],
                        # "border": "10",
                        "sticky": "nswe",
                    },
                )
            ],
        )

        self.normal_theme = {
            "My.TMenubutton": {
                "configure": {"foreground": "black", "background": "light gray"},
                "map": {"foreground": [("active", "black")], "background": [("active", "gray95")]},
            },
            "My.TButton": {
                "configure": {"foreground": "black", "background": "light gray"},
                "map": {"foreground": [("active", "black")], "background": [("active", "gray95")]},
            },
            "My.TFrame": {"configure": {"background": "light gray"}},
            "My2.TFrame": {"configure": {"background": "light gray"}},
            "My.TLabel": {
                "configure": {"foreground": "black", "background": "light gray"},
                "map": {
                    "foreground": [("active", "black"), ("disabled", "gray50")],
                    "background": [("active", "light gray"), ("disabled", "light gray")],
                },
            },
            "MyUnderlined.TLabel": {
                "configure": {
                    "foreground": "black",
                    "background": "light gray",
                    "font": ("TkDefaultFont", 9, "underline"),
                }
            },
            "My.TEntry": {
                "configure": {
                    "foreground": "black",
                    "fieldbackground": "white",
                    "bordercolor": "gray70",  # outer border color
                    "lightcolor": "white",  # inner border color
                    "selectforeground": "white",
                    "selectbackground": "#4A6984",
                },
                "map": {
                    "fieldbackground": [("focus", "white")],  # ("selected", "#4A6984")],
                    "bordercolor": [("focus", "SteelBlue4")],
                    "lightcolor": [("focus", "SteelBlue4")],
                },
            },
            "InvalidRegex.TEntry": {"configure": {"fieldbackground": "#ffcccc"}},
            "My.TCombobox": {
                "configure": {
                    "foreground": "black",  # text color
                    "fieldbackground": "white",  # text background
                    "background": "light gray",  # triangle box background
                    "arrowcolor": "black",  # triangle arrow color
                },
                "map": {
                    "foreground": [("readonly", "black"), ("active", "black")],  # text color drop down list
                    "fieldbackground": [("readonly", "white"), ("active", "white")],  # text background
                    "background": [("readonly", "light gray"), ("active", "light gray")],  # triangle box background
                    "arrowcolor": [("readonly", "black"), ("active", "black")],
                },
            },
            "My.TCheckbutton": {
                "configure": {"foreground": "black", "background": "light gray"},
                "map": {
                    "background": [("active", "light gray")],
                    "indicatorcolor": [("selected", "#4A6984"), ("!selected", "white")],
                },
            },
            "My.TRadiobutton": {
                "configure": {"foreground": "black", "background": "light gray"},
                "map": {
                    "background": [("active", "light gray")],
                    "indicatorcolor": [("selected", "#4A6984"), ("!selected", "white")],
                },
            },
            "My.TNotebook": {"configure": {"background": "light gray"}},
            "My.TNotebook.Tab": {
                "configure": {"foreground": "black", "background": "light gray"},
                "map": {"foreground": [("active", "black")], "background": [("active", "gray95")]},
            },
            "My.TPanedwindow": {"configure": {"background": "gray75"}},  # color of the sash bar between the windows
            "Sash": {
                "configure": {
                    "sashthickness": 2,
                }
            },
            "My.Vertical.TScrollbar": {
                "configure": {
                    "background": "light gray",  # slider and buttons
                    "troughcolor": "light gray",  # trough (area under slider)
                    "arrowcolor": "black",
                },
                "map": {
                    "background": [
                        ("pressed", "gray90"),
                        ("active", "gray90"),
                        # state when scrolling is not possible: ("disabled", "red"),
                    ],
                    "arrowcolor": [("pressed", "black"), ("active", "black")],
                },
            },
            "My.Horizontal.TScrollbar": {
                "configure": {
                    "background": "light gray",  # slider and buttons
                    "troughcolor": "light gray",  # trough (area under slider)
                    "arrowcolor": "black",
                },
                "map": {
                    "background": [
                        ("pressed", "gray90"),
                        ("active", "gray90"),
                        # state when scrolling is not possible: ("disabled", "red"),
                    ],
                    "arrowcolor": [("pressed", "black"), ("active", "black")],
                },
            },
            # Control tab:
            "Path.TButton": {"configure": {"foreground": "black", "background": "light gray"}},
            # Diagram tab:
            "SkyBlue1.TButton": {
                "configure": {"foreground": "black", "background": "SkyBlue1"},
                "map": {
                    "foreground": [("active", "black")],
                    "background": [("active", "deep sky blue")],
                },
            },
            "DeepSkyBlue.TButton": {
                "configure": {"foreground": "black", "background": "deep sky blue"},
                "map": {
                    "foreground": [("active", "black")],
                    "background": [("active", "dodger blue")],
                },
            },
            "Orchid1.TButton": {
                "configure": {"foreground": "black", "background": "orchid1"},
                "map": {
                    "foreground": [("active", "black")],
                    "background": [("active", "orchid2")],
                },
            },
            "IndianRed1.TButton": {
                "configure": {"foreground": "black", "background": "IndianRed1"},
                "map": {
                    "font": [],
                    "foreground": [("active", "black"), ("disabled", "grey65")],
                    "background": [("active", "IndianRed2"), ("disabled", "grey85")],
                },
            },
            "Cyan.TButton": {
                "configure": {"foreground": "black", "background": "cyan2"},
                "map": {
                    "font": [],
                    "foreground": [("active", "black"), ("disabled", "grey65")],
                    "background": [("active", "cyan"), ("disabled", "grey85")],
                },
            },
            "PaleGreen.TButton": {
                "configure": {"foreground": "black", "background": "PaleGreen2"},
                "map": {
                    "font": [],
                    "foreground": [("active", "black"), ("disabled", "grey65")],
                    "background": [("active", "PaleGreen"), ("disabled", "grey85")],
                },
            },
            "LightGray.TButton": {
                "configure": {"foreground": "black", "background": "light gray"},
                "map": {
                    "font": [],
                    "foreground": [("active", "black"), ("disabled", "grey65")],
                    "background": [("active", "grey85"), ("disabled", "grey85")],
                },
            },
            "LemonChiffon.TButton": {
                "configure": {"foreground": "black", "background": "lemon chiffon"},
                "map": {
                    "foreground": [("active", "black")],
                    "font": [],
                    "background": [("active", "khaki")],
                },
            },
            "My.Treeview": {
                "configure": {
                    "background": "white",  # element background
                    "foreground": "black",  # element foreground
                    "fieldbackground": "white",  # empty part
                },
                "map": {
                    "background": [("selected", "#3498db")],
                    "foreground": [("selected", "#ffffff")],
                },
            },
            "My.Treeview.Heading": {
                "configure": {
                    "background": "light gray",
                    "foreground": "black",  # text color
                    "padding": 3,
                },
                "map": {
                    "background": [("active", "light gray")]  # no hover effect needed
                },
            },
        }

        self.dark_theme = {
            "My.TMenubutton": {
                "configure": {"foreground": "light gray", "background": "black"},
                "map": {"foreground": [("active", "white")], "background": [("active", "black")]},
            },
            "My.TButton": {
                "configure": {"foreground": "light gray", "background": "black"},
                "map": {"foreground": [("active", "white")], "background": [("active", "black")]},
            },
            "My.TFrame": {"configure": {"background": "black"}},
            "My2.TFrame": {"configure": {"background": "gray20"}},
            "My.TLabel": {
                "configure": {"foreground": "light gray", "background": "black"},
                "map": {
                    "foreground": [("active", "light gray"), ("disabled", "gray35")],
                    "background": [("active", "black"), ("disabled", "black")],
                },
            },
            "MyUnderlined.TLabel": {
                "configure": {
                    "foreground": "light gray",
                    "background": "black",
                    "font": ("TkDefaultFont", 9, "underline"),
                },
            },
            "My.TEntry": {
                "configure": {
                    "foreground": "white",
                    "fieldbackground": "black",  # "gray60",
                    "bordercolor": "gray70",  # outer border color
                    "lightcolor": "black",  # "gray50",  # inner border color
                    "selectforeground": "black",
                    "selectbackground": "white",
                },
                "map": {
                    "fieldbackground": [("focus", "gray40")],
                    "bordercolor": [("focus", "gray90")],
                    "lightcolor": [("focus", "black")],
                },
            },
            "My.TCombobox": {
                "configure": {
                    "foreground": "white",  # text color
                    "fieldbackground": "black",  # text background
                    "background": "black",  # triangle box background
                    "arrowcolor": "white",  # triangle arrow color
                },
                "map": {
                    "foreground": [("readonly", "white"), ("active", "white")],  # text color drop down list
                    "fieldbackground": [("readonly", "black"), ("active", "black")],  # text background
                    "background": [("readonly", "black"), ("active", "black")],  # triangle box background
                    "arrowcolor": [("readonly", "light gray"), ("active", "light gray")],
                },
            },
            "My.TCheckbutton": {
                "configure": {"foreground": "light gray", "background": "black"},
                "map": {
                    "background": [("active", "black")],
                    "indicatorcolor": [("selected", "white"), ("!selected", "black")],
                },
            },
            "My.TRadiobutton": {
                "configure": {"foreground": "light gray", "background": "black"},
                "map": {
                    "background": [("active", "black")],
                    "indicatorcolor": [("selected", "white"), ("!selected", "black")],
                },
            },
            "My.TNotebook": {"configure": {"background": "black"}},
            "My.TNotebook.Tab": {
                "configure": {"foreground": "light gray", "background": "black"},
                "map": {"foreground": [("active", "white")], "background": [("active", "black")]},
            },
            "My.TPanedwindow": {"configure": {"background": "gray20"}},  # color of the sash bar between the windows
            "My.Vertical.TScrollbar": {
                "configure": {
                    "background": "gray30",  # slider and buttons
                    "troughcolor": "black",  # trough (area under slider)
                    "arrowcolor": "white",
                },
                "map": {
                    "background": [
                        ("pressed", "gray40"),
                        ("active", "gray40"),
                    ],
                    "arrowcolor": [("pressed", "white"), ("active", "white")],
                },
            },
            "My.Horizontal.TScrollbar": {
                "configure": {
                    "background": "gray30",  # slider and buttons
                    "troughcolor": "black",  # trough (area under slider)
                    "arrowcolor": "white",
                },
                "map": {
                    "background": [
                        ("pressed", "gray40"),
                        ("active", "gray40"),
                    ],
                    "arrowcolor": [("pressed", "white"), ("active", "white")],
                },
            },
            # Control tab:
            "Path.TButton": {"configure": {"foreground": "black", "background": "light gray"}},
            # Diagram tab:
            "SkyBlue1.TButton": {
                "configure": {"foreground": "SkyBlue1", "background": "black"},
                "map": {
                    "foreground": [("active", "deep sky blue")],
                    "background": [("active", "black")],
                },
            },
            "DeepSkyBlue.TButton": {
                "configure": {"foreground": "deep sky blue", "background": "black"},
                "map": {
                    "foreground": [("active", "dodger blue")],
                    "background": [("active", "black")],
                },
            },
            "Orchid1.TButton": {
                "configure": {"foreground": "orchid1", "background": "black"},
                "map": {
                    "foreground": [("active", "orchid2")],
                    "background": [("active", "black")],
                },
            },
            "IndianRed1.TButton": {
                "configure": {"foreground": "IndianRed1", "background": "black"},
                "map": {
                    "font": [("disabled", ("TkDefaultFont", 8, "italic"))],
                    "foreground": [("active", "red"), ("disabled", "IndianRed1")],
                    "background": [("active", "black"), ("disabled", "black")],
                },
            },
            "Cyan.TButton": {
                "configure": {"foreground": "cyan2", "background": "black"},
                "map": {
                    "font": [("disabled", ("TkDefaultFont", 8, "italic"))],
                    "foreground": [("active", "cyan"), ("disabled", "cyan2")],
                    "background": [("active", "black"), ("disabled", "black")],
                },
            },
            "PaleGreen.TButton": {
                "configure": {"foreground": "PaleGreen2", "background": "black"},
                "map": {
                    "font": [("disabled", ("TkDefaultFont", 8, "italic"))],
                    "foreground": [("active", "PaleGreen"), ("disabled", "PaleGreen2")],
                    "background": [("active", "black"), ("disabled", "black")],
                },
            },
            "LightGray.TButton": {
                "configure": {"foreground": "gray90", "background": "black"},
                "map": {
                    "font": [("disabled", ("TkDefaultFont", 8, "italic"))],
                    "foreground": [("active", "white"), ("disabled", "gray90")],
                    "background": [("active", "black"), ("disabled", "black")],
                },
            },
            "Redo.TButton": {
                "configure": {"foreground": "gray90", "background": "black"},
                "map": {
                    "font": [("disabled", ("TkDefaultFont", 8, "italic"))],
                    "foreground": [("active", "white"), ("disabled", "gray90")],
                    "background": [("active", "black"), ("disabled", "black")],
                },
            },
            "LemonChiffon.TButton": {
                "configure": {"foreground": "lemon chiffon", "background": "black"},
                "map": {
                    "foreground": [("active", "yellow")],
                    "background": [("active", "black")],
                },
            },
            "My.Treeview": {
                "configure": {
                    "background": "gray20",  # element background
                    "foreground": "light gray",  # element foreground
                    "fieldbackground": "gray20",  # empty part
                },
                "map": {
                    "background": [("selected", "white")],
                    "foreground": [("selected", "black")],
                },
            },
            "My.Treeview.Heading": {
                "configure": {
                    "background": "black",
                    "foreground": "light gray",  # text color
                    "padding": 3,
                },
                "map": {
                    "background": [("active", "black")]  # no hover effect needed
                },
            },
        }
        self.switch_style("Normal Mode")

    def switch_style(self, mode) -> None:
        """Switch the styling mode for the application."""
        if mode == "Dark Mode":
            self.style.theme_settings("default", self.dark_theme)
        else:
            self.style.theme_settings("default", self.normal_theme)
