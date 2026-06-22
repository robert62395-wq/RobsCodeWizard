"""Help dialog content for the 11 advanced controls (v0.5.2)."""

HELP_TOPICS = {
    "code_set": (
        "Code Set Selector",
        "<p><b>Code Set</b> determines which catalog of survey codes the app uses to"
        " validate and translate descriptions.</p>"
        "<ul>"
        "<li><b>VDT</b>: Legacy code library, uses letters for line connects (B, E, BC, EC, CLS).</li>"
        "<li><b>ODOT</b>: Ohio DOT library, uses alphabetic (BL*, EL*, OC*, CL*) or numeric"
        " (1, 2, 3, 4) line connects.</li>"
        "</ul>"
        "<p>Switching the code set triggers re-validation of all loaded rows against the new"
        " catalog. Rows valid under VDT may flag as invalid under ODOT and vice versa.</p>"
    ),
    "linework_fix": (
        "Linework Fix Tool",
        "<p>Opens an overlay that helps you find and repair common linework grammar problems"
        " in your loaded file:</p>"
        "<ul>"
        "<li>Mixed numeric/alphabetic line connects in the same file</li>"
        "<li>Orphan line-connect commands with no preceding point code</li>"
        "<li>Unbalanced begin/end pairs (B without E, BC without EC)</li>"
        "</ul>"
        "<p>The overlay highlights problem rows on the Raw Data table; click a problem to jump to it.</p>"
    ),
    "translate_source_target": (
        "Translation Direction",
        "<p>The <b>Source</b> dialect is auto-detected from the Code Set selected on the Raw Data tab.</p>"
        "<p>The <b>Target</b> dialect is what your loaded data will be converted to.</p>"
        "<p>For most workflows the default (VDT&rarr;ODOT) is correct. Set Target=VDT only when"
        " converting ODOT-coded data back to VDT.</p>"
    ),
    "translate_button": (
        "Translate Loaded Rows",
        "<p>Rewrites the Description (D) column of every loaded row, converting:</p>"
        "<ul>"
        "<li>Point codes (via the translation map below)</li>"
        "<li>Line-connect commands (B&harr;BL*, E&harr;EL*, 1&harr;BL*, etc.)</li>"
        "<li>Size tokens are preserved (e.g., VTD 12 stays as VTD 12)</li>"
        "<li>Comments after / are preserved verbatim</li>"
        "</ul>"
        "<p><b>Never modified:</b> Point numbers, Northings, Eastings, Elevations.</p>"
    ),
    "translate_filter_used": (
        "Filter: Only codes in loaded file",
        "<p>When checked, the table shows only translation entries for codes that actually appear"
        " in your loaded data. This focuses you on the codes you need to review.</p>"
        "<p>Uncheck to see the entire catalog.</p>"
    ),
    "translate_bulk_accept": (
        "Accept All Best-Guess in View",
        "<p>Promotes every currently-visible <b>best-guess</b> entry to a <b>manual override</b>"
        " in one click. Use this after spot-checking a few entries to confirm the algorithm got"
        " most of them right.</p>"
        "<p>Bulk-accepted entries change from yellow to blue. You can still edit individual"
        " entries afterward. Click <b>Save Overrides</b> to persist.</p>"
    ),
    "translate_reseed": (
        "Reseed from Catalog",
        "<p><b>WARNING - destructive operation.</b></p>"
        "<p>This rebuilds the entire translation map from VDT_CODES.xlsx and ODOT_CODES.xlsx,"
        " discarding all manual overrides you have saved.</p>"
        "<p>Use this only when the catalog XLSX files have changed, or you want to start over.</p>"
    ),
    "export_use_numeric": (
        "Use Numeric Line Connect Codes",
        "<p>OpenRoads accepts both grammars for line connects:</p>"
        "<ul>"
        "<li><b>Numeric</b>: 1, 2, 3, 4 (compact, preferred by some field crews)</li>"
        "<li><b>Alphabetic</b>: BL*, EL*, OC*, CL* (more readable in CAD)</li>"
        "</ul>"
        "<p>Check this box to convert to numeric on export. Civil3D requires alphabetic.</p>"
    ),
    "point_offset": (
        "Apply Point Number Offset",
        "<p>Adds a constant integer to every Point number (P column).</p>"
        "<p><b>Collision detection:</b> Before applying, the app checks whether the offset would"
        " create duplicate point numbers. If yes, the operation is aborted.</p>"
        "<p><b>Never modified:</b> Northings, Eastings, Elevations, Descriptions.</p>"
        "<p><b>Undo:</b> Tools &rarr; Undo Last Offset to reverse.</p>"
    ),
    "elevation_offset": (
        "Apply Elevation Offset",
        "<p>Adds a constant value (in feet) to every Elevation (Z column).</p>"
        "<p><b>Skip-zero behavior:</b> Rows with Z=0 are intentionally skipped (zero often indicates"
        " an unset/unknown elevation, not a real datum).</p>"
        "<p><b>Common use:</b> NAVD88 to IGLD85 conversion for Ohio Lake Erie projects (offset = -0.55 ft).</p>"
        "<p><b>Never modified:</b> Point numbers, Northings, Eastings, Descriptions.</p>"
    ),
    "convert_line_connect": (
        "Convert Line Connect Codes",
        "<p>Converts line-connect commands between numeric (1/2/3/4) and alphabetic"
        " (BL*/EL*/OC*/CL*) grammars.</p>"
        "<p>This tool changes ONLY line-connect tokens; point codes (EP, DR, etc.) are untouched.</p>"
    ),
}