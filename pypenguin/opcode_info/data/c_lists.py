from pypenguin.utility import DualKeyDict

from pypenguin.opcode_info.api import OpcodeInfoGroup, OpcodeInfo, OpcodeType, InputInfo, InputType, DropdownInfo, DropdownType, MenuInfo


lists = OpcodeInfoGroup(name="lists", opcode_info=DualKeyDict({
    ("data_addtolist", "add (ITEM) to [LIST]"): OpcodeInfo(
        opcode_type=OpcodeType.STATEMENT,
        inputs=DualKeyDict({
            ("ITEM", "ITEM"): InputInfo(InputType.TEXT),
        }),
        dropdowns=DualKeyDict({
            ("LIST", "LIST"): DropdownInfo(DropdownType.LIST),
        }),
    ),
    ("data_deleteoflist", "delete (INDEX) of [LIST]"): OpcodeInfo(
        opcode_type=OpcodeType.STATEMENT,
        inputs=DualKeyDict({
            ("INDEX", "INDEX"): InputInfo(InputType.INTEGER),
        }),
        dropdowns=DualKeyDict({
            ("LIST", "LIST"): DropdownInfo(DropdownType.LIST),
        }),
    ),
    ("data_deletealloflist", "delete all of [LIST]"): OpcodeInfo(
        opcode_type=OpcodeType.STATEMENT,
        dropdowns=DualKeyDict({
            ("LIST", "LIST"): DropdownInfo(DropdownType.LIST),
        }),
    ),
    ("data_shiftlist", "shift [LIST] by (INDEX)"): OpcodeInfo(
        opcode_type=OpcodeType.STATEMENT,
        inputs=DualKeyDict({
            ("INDEX", "INDEX"): InputInfo(InputType.INTEGER),
        }),
        dropdowns=DualKeyDict({
            ("LIST", "LIST"): DropdownInfo(DropdownType.LIST),
        }),
    ),
    ("data_insertatlist", "insert (ITEM) at (INDEX) of [LIST]"): OpcodeInfo(
        opcode_type=OpcodeType.STATEMENT,
        inputs=DualKeyDict({
            ("ITEM", "ITEM"): InputInfo(InputType.TEXT),
            ("INDEX", "INDEX"): InputInfo(InputType.INTEGER),
        }),
        dropdowns=DualKeyDict({
            ("LIST", "LIST"): DropdownInfo(DropdownType.LIST),
        }),
    ),
    ("data_replaceitemoflist", "replace item (INDEX) of [LIST] with (ITEM)"): OpcodeInfo(
        opcode_type=OpcodeType.STATEMENT,
        inputs=DualKeyDict({
            ("INDEX", "INDEX"): InputInfo(InputType.INTEGER),
            ("ITEM", "ITEM"): InputInfo(InputType.TEXT),
        }),
        dropdowns=DualKeyDict({
            ("LIST", "LIST"): DropdownInfo(DropdownType.LIST),
        }),
    ),
    ("data_listforeachitem", "For each item [VARIABLE] in [LIST] {BODY}"): OpcodeInfo(
        opcode_type=OpcodeType.STATEMENT,
        inputs=DualKeyDict({
            ("SUBSTACK", "BODY"): InputInfo(InputType.SCRIPT),
        }),
        dropdowns=DualKeyDict({
            ("VARIABLE", "VARIABLE"): DropdownInfo(DropdownType.VARIABLE),
            ("LIST", "LIST"): DropdownInfo(DropdownType.LIST),
        }),
    ),
    ("data_listforeachnum", "For each item # [VARIABLE] in [LIST] {BODY}"): OpcodeInfo(
        opcode_type=OpcodeType.STATEMENT,
        inputs=DualKeyDict({
            ("SUBSTACK", "BODY"): InputInfo(InputType.SCRIPT),
        }),
        dropdowns=DualKeyDict({
            ("VARIABLE", "VARIABLE"): DropdownInfo(DropdownType.VARIABLE),
            ("LIST", "LIST"): DropdownInfo(DropdownType.LIST),
        }),
    ),
    ("data_itemoflist", "item (INDEX) of [LIST]"): OpcodeInfo(
        opcode_type=OpcodeType.STRING_REPORTER,
        inputs=DualKeyDict({
            ("INDEX", "INDEX"): InputInfo(InputType.INTEGER),
        }),
        dropdowns=DualKeyDict({
            ("LIST", "LIST"): DropdownInfo(DropdownType.LIST),
        }),
    ),
    ("data_itemnumoflist", "item # of (ITEM) in [LIST]"): OpcodeInfo(
        opcode_type=OpcodeType.STRING_REPORTER,
        inputs=DualKeyDict({
            ("ITEM", "ITEM"): InputInfo(InputType.TEXT),
        }),
        dropdowns=DualKeyDict({
            ("LIST", "LIST"): DropdownInfo(DropdownType.LIST),
        }),
    ),
    ("data_amountinlist", "amount of (VALUE) of [LIST]"): OpcodeInfo(
        opcode_type=OpcodeType.STRING_REPORTER,
        inputs=DualKeyDict({
            ("VALUE", "VALUE"): InputInfo(InputType.TEXT),
        }),
        dropdowns=DualKeyDict({
            ("LIST", "LIST"): DropdownInfo(DropdownType.LIST),
        }),
    ),
    ("data_lengthoflist", "length of [LIST]"): OpcodeInfo(
        opcode_type=OpcodeType.STRING_REPORTER,
        dropdowns=DualKeyDict({
            ("LIST", "LIST"): DropdownInfo(DropdownType.LIST),
        }),
    ),
    ("data_listcontainsitem", "[LIST] contains (ITEM) ?"): OpcodeInfo(
        opcode_type=OpcodeType.BOOLEAN_REPORTER,
        inputs=DualKeyDict({
            ("ITEM", "ITEM"): InputInfo(InputType.TEXT),
        }),
        dropdowns=DualKeyDict({
            ("LIST", "LIST"): DropdownInfo(DropdownType.LIST),
        }),
    ),
    ("data_itemexistslist", "item (INDEX) exists in [LIST] ?"): OpcodeInfo(
        opcode_type=OpcodeType.BOOLEAN_REPORTER,
        inputs=DualKeyDict({
            ("INDEX", "INDEX"): InputInfo(InputType.INTEGER),
        }),
        dropdowns=DualKeyDict({
            ("LIST", "LIST"): DropdownInfo(DropdownType.LIST),
        }),
    ),
    ("data_listisempty", "is [LIST] empty?"): OpcodeInfo(
        opcode_type=OpcodeType.BOOLEAN_REPORTER,
        dropdowns=DualKeyDict({
            ("LIST", "LIST"): DropdownInfo(DropdownType.LIST),
        }),
    ),
    ("data_reverselist", "reverse [LIST]"): OpcodeInfo(
        opcode_type=OpcodeType.STATEMENT,
        dropdowns=DualKeyDict({
            ("LIST", "LIST"): DropdownInfo(DropdownType.LIST),
        }),
    ),
    ("data_arraylist", "set [LIST] to array (VALUE)"): OpcodeInfo(
        opcode_type=OpcodeType.STATEMENT,
        inputs=DualKeyDict({
            ("VALUE", "VALUE"): InputInfo(InputType.TEXT),
        }),
        dropdowns=DualKeyDict({
            ("LIST", "LIST"): DropdownInfo(DropdownType.LIST),
        }),
    ),
    ("data_listarray", "get list [LIST] as an array"): OpcodeInfo(
        opcode_type=OpcodeType.STRING_REPORTER,
        dropdowns=DualKeyDict({
            ("LIST", "LIST"): DropdownInfo(DropdownType.LIST),
        }),
    ),
    ("data_showlist", "show list [LIST]"): OpcodeInfo(
        opcode_type=OpcodeType.STATEMENT,
        dropdowns=DualKeyDict({
            ("LIST", "LIST"): DropdownInfo(DropdownType.LIST),
        }),
    ),
    ("data_hidelist", "hide list [LIST]"): OpcodeInfo(
        opcode_type=OpcodeType.STATEMENT,
        dropdowns=DualKeyDict({
            ("LIST", "LIST"): DropdownInfo(DropdownType.LIST),
        }),
    ),
}))