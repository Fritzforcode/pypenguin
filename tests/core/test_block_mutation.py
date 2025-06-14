from copy   import deepcopy
from json   import dumps
from pytest import fixture, raises

from pypenguin.important_consts import SHA256_SEC_MAIN_ARGUMENT_NAME
from pypenguin.utility          import (
    string_to_sha256,
    DeserializationError, ConversionError, ThanksError, 
    ValidationConfig, TypeValidationError, InvalidValueError
)

from pypenguin.core.block_interface import FirstToInterIF, InterToFirstIF
from pypenguin.core.block_mutation  import (
    FRMutation,
    FRCustomBlockArgumentMutation, FRCustomBlockMutation,
    FRCustomBlockCallMutation, FRStopScriptMutation,
    SRCustomBlockArgumentMutation, SRCustomBlockMutation,
    SRCustomBlockCallMutation, SRStopScriptMutation
)
from pypenguin.core.custom_block    import SRCustomBlockOpcode, SRCustomBlockOptype

from tests.core.constants import (
    ALL_FR_BLOCKS_CLEAN, ALL_IR_BLOCKS, ALL_SR_COMMENTS, SR_BLOCK_CUSTOM_OPCODE,
)


from tests.utility import execute_attr_validation_tests


@fixture
def fti_if():
    return FirstToInterIF(blocks=ALL_FR_BLOCKS_CLEAN, block_comments=ALL_SR_COMMENTS)

@fixture
def itf_if():
    return InterToFirstIF(blocks=ALL_IR_BLOCKS)

@fixture
def config():
    return ValidationConfig()

EXAMPLE_ARG_IDS = [
    string_to_sha256("a text arg", secondary=SHA256_SEC_MAIN_ARGUMENT_NAME), 
    string_to_sha256("a bool arg", secondary=SHA256_SEC_MAIN_ARGUMENT_NAME),
]
EXAMPLE_ARG_NAMES = ["a text arg", "a bool arg"]
EXAMPLE_ARG_DEFAULTS = ["", "false"]



def test_FRMutation_from_data_and_post_init():
    class DummyFRMutation(FRMutation):
        @classmethod
        def from_data(cls, data) -> "DummyFRMutation":
            return cls(
                tag_name = data["tagName" ],
                children = data["children"],
            )
        def to_second(self, ticfti_if): pass

    data = {
        "tagName": "mutation",
        "children": [],
    }
    frmutation = DummyFRMutation.from_data(data)
    assert isinstance(frmutation, DummyFRMutation)
    assert frmutation.tag_name == data["tagName"]
    assert frmutation.children == data["children"]

    with raises(ThanksError):
        DummyFRMutation.from_data({
            "tagName": "something else", # invalid
            "children": [],
        })
    
    with raises(ThanksError):
        DummyFRMutation.from_data({
            "tagName": "mutation",
            "children": {}, # invalid
        })



def test_FRCustomBlockArgumentMutation_from_data_and_to_second(fti_if: FirstToInterIF):
    colors = ["#FF6680", "#FF4D6A", "#FF3355"]
    data = {
        "tagName": "mutation", 
        "children": [], 
        "color": dumps(colors),
    }
    frmutation = FRCustomBlockArgumentMutation.from_data(data)
    assert frmutation.color == tuple(colors)
    
    frmutation.store_argument_name("my_arg")
    srmutation = frmutation.to_second(fti_if)
    assert isinstance(srmutation, SRCustomBlockArgumentMutation)
    assert srmutation.argument_name == "my_arg"
    assert srmutation.main_color == colors[0]
    assert srmutation.prototype_color == colors[1]
    assert srmutation.outline_color == colors[2]

def test_FRCustomBlockArgumentMutation_to_second_without_storing_argument(fti_if: FirstToInterIF):
    data = {
        "tagName": "mutation",
        "children": [],
        "color": dumps(["#111111", "#222222", "#333333"]),
    }
    frmutation = FRCustomBlockArgumentMutation.from_data(data)

    with raises(ConversionError):
        frmutation.to_second(fti_if)



def test_FRCustomBlockMutation_from_data_and_to_second(fti_if: FirstToInterIF):
    warp    = False
    returns = None
    edited  = True
    optype  = None
    colors  = ["#FF6680", "#FF4D6A", "#FF3355"]
    data    = {
        "tagName": "mutation", 
        "children": [], 
        "proccode": "do sth text %s and bool %b", 
        "argumentids": dumps(EXAMPLE_ARG_IDS), 
        "argumentnames": dumps(EXAMPLE_ARG_NAMES), 
        "argumentdefaults": dumps(EXAMPLE_ARG_DEFAULTS), 
        "warp": dumps(warp), 
        "returns": dumps(returns), 
        "edited": dumps(edited), 
        "optype": dumps(optype), 
        "color": dumps(colors),
    }
    frmutation = FRCustomBlockMutation.from_data(data)
    assert frmutation.proccode == data["proccode"]
    assert frmutation.argument_ids == EXAMPLE_ARG_IDS
    assert frmutation.argument_names == EXAMPLE_ARG_NAMES
    assert frmutation.argument_defaults == EXAMPLE_ARG_DEFAULTS 
    assert frmutation.warp == warp
    assert frmutation.returns == returns
    assert frmutation.edited == edited
    assert frmutation.optype == optype
    assert frmutation.color == tuple(colors)
    
    srmutation = frmutation.to_second(fti_if)
    assert isinstance(srmutation, SRCustomBlockMutation)
    custom_opcode = SRCustomBlockOpcode.from_proccode_argument_names(
        proccode=frmutation.proccode,
        argument_names=frmutation.argument_names,
    )
    assert srmutation.custom_opcode == custom_opcode
    assert srmutation.no_screen_refresh == frmutation.warp
    assert srmutation.optype == SRCustomBlockOptype.from_code(frmutation.optype)
    assert srmutation.main_color == frmutation.color[0]
    assert srmutation.prototype_color == frmutation.color[1]
    assert srmutation.outline_color == frmutation.color[2]



def test_FRCustomBlockCallMutation_from_data_and_to_second(fti_if: FirstToInterIF):
    warp = False
    returns = None
    edited = True
    optype = None
    colors = ["#FF6680", "#FF4D6A", "#FF3355"]
    data = {
        "tagName": "mutation", 
        "children": [], 
        "proccode": "do sth text %s and bool %b", 
        "argumentids": dumps(EXAMPLE_ARG_IDS), 
        "warp": dumps(warp), 
        "returns": dumps(returns), 
        "edited": dumps(edited), 
        "optype": dumps(optype), 
        "color": dumps(colors),
    }
    frmutation = FRCustomBlockCallMutation.from_data(data)
    assert frmutation.proccode == data["proccode"]
    assert frmutation.argument_ids == EXAMPLE_ARG_IDS
    assert frmutation.warp == warp
    assert frmutation.returns == returns
    assert frmutation.edited == edited
    assert frmutation.optype == optype
    assert frmutation.color == tuple(colors)
    
    srmutation = frmutation.to_second(fti_if)
    assert isinstance(srmutation, SRCustomBlockCallMutation)
    custom_opcode = SRCustomBlockOpcode.from_proccode_argument_names(
        proccode=frmutation.proccode,
        argument_names=EXAMPLE_ARG_NAMES,
    )
    assert srmutation.custom_opcode == custom_opcode



def test_FRCustomBlockMutation_from_data_warp():
    colors = ["#FF6680", "#FF4D6A", "#FF3355"]
    data = {
        "tagName": "mutation", 
        "children": [], 
        "proccode": "hi bye", 
        "argumentids": dumps([]), 
        "argumentnames": dumps([]), 
        "argumentdefaults": dumps([]), 
        "warp": ..., 
        "returns": dumps(None), 
        "edited": dumps(True), 
        "optype": dumps(None), 
        "color": dumps(colors),
    }
    
    FRCustomBlockMutation    .from_data(data | {"warp": dumps(True )})
    FRCustomBlockCallMutation.from_data(data | {"warp": dumps(False)})

    FRCustomBlockMutation    .from_data(data | {"warp": True })
    FRCustomBlockCallMutation.from_data(data | {"warp": False})

    with raises(DeserializationError):
        FRCustomBlockMutation    .from_data(data | {"warp": 123})
    with raises(DeserializationError):
        FRCustomBlockCallMutation.from_data(data | {"warp": []})
    


def test_FRStopScriptMutation_from_data_and_to_second(fti_if: FirstToInterIF):
    has_next = False
    data = {
        "tagName": "mutation",
        "children": [],
        "hasnext": dumps(has_next),
    }
    frmutation = FRStopScriptMutation.from_data(data)
    assert frmutation.has_next == has_next
    
    srmutation = frmutation.to_second(fti_if)
    assert isinstance(srmutation, SRStopScriptMutation)
    assert srmutation.is_ending_statement == (not frmutation.has_next)



def test_SRCustomBlockArgumentMutation_validate(config: ValidationConfig):
    srmutation = SRCustomBlockArgumentMutation(
        argument_name="my argument",
        main_color="#f8e43a",
        prototype_color="#c38d12",
        outline_color="#e9d563",
    )
    srmutation.validate(path=[], config=config)
    
    execute_attr_validation_tests(
        obj=srmutation,
        attr_tests=[
            ("argument_name", 5, TypeValidationError),
            ("main_color", {}, TypeValidationError),
            ("main_color", "", InvalidValueError),
            ("prototype_color", [], TypeValidationError),
            ("prototype_color", "#abc", InvalidValueError),
            ("outline_color", (), TypeValidationError),
            ("outline_color", "255", InvalidValueError),
        ],
        validate_func=SRCustomBlockArgumentMutation.validate,
        func_args=[[], config],
    )


def test_SRCustomBlockArgumentMutation_to_first(itf_if: InterToFirstIF):
    srmutation = SRCustomBlockArgumentMutation(
        argument_name="my argument",
        main_color="#f8e43a",
        prototype_color="#c38d12",
        outline_color="#e9d563",
    )
    assert srmutation.to_first(itf_if) == FRCustomBlockArgumentMutation(
        tag_name="mutation",
        children=[],
        color=("#f8e43a", "#c38d12", "#e9d563"),
    )



def test_SRCustomBlockMutation_validate(config: ValidationConfig):
    srmutation = SRCustomBlockMutation(
        custom_opcode=SRCustomBlockOpcode(segments=("hi",)),
        no_screen_refresh=True,
        optype=SRCustomBlockOptype.STRING_REPORTER,
        main_color="#f8e43a",
        prototype_color="#c38d12",
        outline_color="#e9d563",
    )

    srmutation.validate(path=[], config=config)
    
    execute_attr_validation_tests(
        obj=srmutation,
        attr_tests=[
            ("custom_opcode", "some custom opcode", TypeValidationError),
            ("no_screen_refresh", None, TypeValidationError),
            ("main_color", {}, TypeValidationError),
            ("main_color", "", InvalidValueError),
            ("prototype_color", [], TypeValidationError),
            ("prototype_color", "#abc", InvalidValueError),
            ("outline_color", (), TypeValidationError),
            ("outline_color", "255", InvalidValueError),
        ],
        validate_func=SRCustomBlockMutation.validate,
        func_args=[[], config],
    )


def test_SRCustomBlockMutation_to_first(itf_if: InterToFirstIF):
    srmutation = SRCustomBlockMutation(
        custom_opcode=SR_BLOCK_CUSTOM_OPCODE,
        no_screen_refresh=True,
        optype=SRCustomBlockOptype.STRING_REPORTER,
        main_color="#f8e43a",
        prototype_color="#c38d12",
        outline_color="#e9d563",
    )
    assert srmutation.to_first(itf_if) == FRCustomBlockMutation(
        tag_name="mutation", 
        children=[], 
        proccode="do sth text %s and bool %b", 
        argument_ids=EXAMPLE_ARG_IDS, 
        argument_names=EXAMPLE_ARG_NAMES, 
        argument_defaults=EXAMPLE_ARG_DEFAULTS, 
        warp=True, 
        returns=True, 
        edited=True, 
        optype="string", 
        color=("#f8e43a", "#c38d12", "#e9d563"),
    )
    srmutation.optype = SRCustomBlockOptype.ENDING_STATEMENT
    assert srmutation.to_first(itf_if).returns is None


  
def test_SRCustomBlockCallMutation_validate(config: ValidationConfig):
    srmutation = SRCustomBlockCallMutation(
        custom_opcode=SRCustomBlockOpcode(segments=("hi",)),
    )

    srmutation.validate(path=[], config=config)
    
    execute_attr_validation_tests(
        obj=srmutation,
        attr_tests=[
            ("custom_opcode", "some custom opcode", TypeValidationError),
        ],
        validate_func=SRCustomBlockCallMutation.validate,
        func_args=[[], config],
    )


def test_SRCustomBlockMutationCall_to_first(itf_if: InterToFirstIF):
    srmutation = SRCustomBlockCallMutation(
        custom_opcode=SR_BLOCK_CUSTOM_OPCODE,
    )
    assert srmutation.to_first(itf_if) == FRCustomBlockCallMutation(
        tag_name="mutation", 
        children=[], 
        proccode="do sth text %s and bool %b", 
        argument_ids=EXAMPLE_ARG_IDS, 
        warp=False, 
        returns=True, 
        edited=True, 
        optype="number", 
        color=("#FF6680", "#FF4D6A", "#FF3355"),
    )
    
    class DummyIF(InterToFirstIF):
        def get_sr_cb_mutation(self, custom_opcode: SRCustomBlockOpcode) -> "SRCustomBlockMutation":
            srmutation = super().get_sr_cb_mutation(custom_opcode)
            srmutation_copy = deepcopy(srmutation)
            srmutation_copy.optype = SRCustomBlockOptype.ENDING_STATEMENT
            return srmutation_copy
    dummy_if = DummyIF(blocks=ALL_IR_BLOCKS)
    assert srmutation.to_first(dummy_if).returns is None



def test_SRStopScriptMutation_validate(config: ValidationConfig):
    srmutation = SRStopScriptMutation(
        is_ending_statement=True,
    )

    srmutation.validate(path=[], config=config)

    execute_attr_validation_tests(
        obj=srmutation,
        attr_tests=[
            ("is_ending_statement", {...}, TypeValidationError),
        ],
        validate_func=SRStopScriptMutation.validate,
        func_args=[[], config],
    )
    

def test_SRStopScriptMutation_to_first(itf_if: InterToFirstIF):
    srmutation = SRStopScriptMutation(
        is_ending_statement=False,
    )
    assert srmutation.to_first(itf_if) == FRStopScriptMutation(
        tag_name="mutation",
        children=[],
        has_next=True,
    )


