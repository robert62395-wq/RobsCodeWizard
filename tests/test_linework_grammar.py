from app.services.linework_grammar import VDT_GRAMMAR, ODOT_GRAMMAR, GRAMMARS


def test_vdt_constants():
    g = VDT_GRAMMAR
    assert g.begin_line == "B" and g.end_line == "E"
    assert g.begin_curve == "BC" and g.end_curve == "EC"
    assert g.compound_curve == "CC" and g.reverse_curve == "RC"
    assert g.close_shape == "CLS" and g.curve_toggle is None


def test_odot_constants():
    g = ODOT_GRAMMAR
    assert g.begin_line == "BL*" and g.end_line == "EL*"
    assert g.close_shape == "CL*" and g.curve_toggle == "OC*"
    assert g.begin_curve is None and g.end_curve is None


def test_all_commands():
    assert VDT_GRAMMAR.all_commands == frozenset({"B","E","BC","EC","CC","RC","CLS"})
    assert ODOT_GRAMMAR.all_commands == frozenset({"BL*","EL*","CL*","OC*"})


def test_is_command():
    assert VDT_GRAMMAR.is_command("B") and VDT_GRAMMAR.is_command("b")
    assert not VDT_GRAMMAR.is_command("BL*")
    assert ODOT_GRAMMAR.is_command("BL*") and ODOT_GRAMMAR.is_command("bl*")
    assert not ODOT_GRAMMAR.is_command("B")


def test_is_begin_end():
    assert VDT_GRAMMAR.is_begin("B") and VDT_GRAMMAR.is_end("E")
    assert VDT_GRAMMAR.is_begin("BC") and VDT_GRAMMAR.is_end("EC")
    assert ODOT_GRAMMAR.is_begin("BL*") and ODOT_GRAMMAR.is_end("EL*")
