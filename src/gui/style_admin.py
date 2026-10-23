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
            "My.TLabel": {"configure": {"foreground": "black", "background": "light gray"}},
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
                "map": {
                    "foreground": [("readonly", "black")],  # text color when readonly
                    "background": [("readonly", "light gray")],  # arrow field background color when readonly
                    "fieldbackground": [("readonly", "light gray")],  # field background color when readonly
                    "arrowcolor": [("readonly", "black")],  # arrow color when readonly
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
            "My.TPanedwindow": {
                "configure": {"background": "gray75"},
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
                    "font": [],
                    "foreground": [("active", "black")],
                    "background": [("active", "khaki")],
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
            "My.TLabel": {"configure": {"foreground": "light gray", "background": "black"}},
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
                "map": {
                    "foreground": [("readonly", "light gray")],  # text color when readonly
                    "background": [("readonly", "black")],  # arrow field background color when readonly
                    "fieldbackground": [("readonly", "black")],  # field background color when readonly
                    "arrowcolor": [("readonly", "light gray")],  # arrow color when readonly
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
            "My.TPanedwindow": {"configure": {"background": "gray20"}},
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
            "LemonChiffon.TButton": {
                "configure": {"foreground": "lemon chiffon", "background": "black"},
                "map": {
                    "foreground": [("active", "yellow")],
                    "background": [("active", "black")],
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
