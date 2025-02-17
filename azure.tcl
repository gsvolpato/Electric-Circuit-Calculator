package require Tk 8.6

namespace eval ttk::theme::azure {
    variable version 1.0
    package provide ttk::theme::azure $version

    ttk::style theme create azure -parent default -settings {
        ttk::style configure . \
            -background black \
            -foreground white \
            -troughcolor black \
            -fieldbackground black \
            -selectbackground "#007fff" \
            -selectforeground white \
            -insertcolor white \
            -insertwidth 1
            
        ttk::style map . \
            -background [list disabled black active black] \
            -foreground [list disabled "#666666" active white] \
            -selectbackground [list !focus black] \
            -selectforeground [list !focus white]
            
        # Frame
        ttk::style configure TFrame -background black
        
        # Paned window
        ttk::style configure TPanedwindow -background black
    }
}

proc set_theme {mode} {
    if {$mode == "dark"} {
        ttk::style theme use azure
        option add *Background black
        option add *Foreground white
    }
} 