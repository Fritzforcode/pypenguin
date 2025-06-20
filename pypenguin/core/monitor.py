from typing import Any

from pypenguin.opcode_info.api  import OpcodeInfoAPI
from pypenguin.utility          import (
    grepr_dataclass, ValidationConfig,
    AA_TYPE, AA_TYPES, AA_DICT_OF_TYPE, AA_COORD_PAIR, AA_BOXED_COORD_PAIR, AA_EQUAL, AA_BIGGER_OR_EQUAL, 
    InvalidOpcodeError, MissingDropdownError, UnnecessaryDropdownError, ThanksError,
)
from pypenguin.important_consts import OPCODE_VAR_VALUE, OPCODE_LIST_VALUE, NEW_OPCODE_VAR_VALUE, NEW_OPCODE_LIST_VALUE

from pypenguin.core.context  import PartialContext, CompleteContext
from pypenguin.core.dropdown import SRDropdownValue
from pypenguin.core.enums    import SRVariableMonitorReadoutMode


# TODO: create global config
STAGE_WIDTH : int = 480
STAGE_HEIGHT: int = 360
LIST_MONITOR_DEFAULT_WIDTH  = 100
LIST_MONITOR_DEFAULT_HEIGHT = 120

@grepr_dataclass(grepr_fields=["id", "mode", "opcode", "params", "sprite_name", "value", "x", "y", "visible", "width", "height", "slider_min", "slider_max", "is_discrete"])
class FRMonitor:
    """
    The first representation for a monitor
    """

    # Core Properties
    id: str
    mode: str
    opcode: str
    params: dict[str, Any]
    sprite_name: str | None
    value: Any
    x: int | float
    y: int | float
    visible: bool
    
    # Properties which matter for some opcodes
    width: int | float
    height: int | float
    slider_min: int | float | None
    slider_max: int | float | None
    is_discrete: bool | None

    @classmethod
    def from_data(cls, data: dict[str, Any]) -> "FRMonitor":
        """
        Deserializes raw data into a FRMonitor
        
        Args:
            data: the raw data
        
        Returns:
            the FRMonitor
        """
        return cls(
            # Core Properties
            id          = data["id"        ], 
            mode        = data["mode"      ], 
            opcode      = data["opcode"    ], 
            params      = data["params"    ], 
            sprite_name = data["spriteName"], 
            value       = data["value"     ],
            x           = data["x"         ],
            y           = data["y"         ],
            visible     = data["visible"   ],
            
            # Properties for some opcodes
            width       = data["width" ],
            height      = data["height"],
            slider_min  = data.get("sliderMin" , None),
            slider_max  = data.get("sliderMax" , None),
            is_discrete = data.get("isDiscrete", None),
        )
    
    def __post_init__(self) -> None:
        """
        Ensure my assumptions about monitors were correct
        
        Returns:
            None
        """
        if not isinstance(self.params, dict):
            raise ThanksError()
        if self.opcode == OPCODE_VAR_VALUE:
            valid = self.mode in {"default", "large", "slider"}
        elif self.opcode == OPCODE_LIST_VALUE:
            valid = self.mode == "list"
        else:
            valid = self.mode == "default"
        if not valid:
            raise ThanksError()

    def to_second(self, info_api: OpcodeInfoAPI, sprite_names: list[str]) -> "SRMonitor | None":
        """
        Converts a FRMonitor into a SRMonitor
        
        Args:
            info_api: the opcode info api used to fetch information about opcodes
            sprite_names: a list of sprite names in the project, used to delete monitors of deleted sprites
        
        Returns:
            the SRMonitor
        """
        if (self.sprite_name is not None) and (self.sprite_name not in sprite_names):
            return None # Delete monitors of non-existing sprites: possibly not needed anymore
        
        opcode_info = info_api.get_info_by_old(self.opcode)
        
        new_dropdowns = {}
        for dropdown_id, dropdown_value in self.params.items():
            new_dropdown_id = opcode_info.get_new_dropdown_id(dropdown_id)
            dropdown_type   = opcode_info.get_dropdown_info_by_old(dropdown_id).type
            new_dropdown_value = dropdown_type.translate_old_to_new_value(dropdown_value)
            new_dropdowns[new_dropdown_id] = SRDropdownValue.from_tuple(new_dropdown_value)
        
        new_opcode = info_api.get_new_by_old(self.opcode)
        position   = (self.x - (STAGE_WIDTH//2), self.y - (STAGE_HEIGHT//2)) # this lets the center of stage be the origin        
        if   self.opcode == OPCODE_VAR_VALUE:
            return SRVariableMonitor(
                opcode              = new_opcode,
                dropdowns           = new_dropdowns,
                position            = position,
                is_visible          = self.visible,
                readout_mode        = SRVariableMonitorReadoutMode.from_code(self.mode),
                slider_min          = self.slider_min,
                slider_max          = self.slider_max,
                allow_only_integers = self.is_discrete,
            )
        elif self.opcode == OPCODE_LIST_VALUE:
            return SRListMonitor(
                opcode      = new_opcode,
                dropdowns   = new_dropdowns,
                position    = position,
                is_visible  = self.visible,
                size        = (
                    LIST_MONITOR_DEFAULT_WIDTH  if self.width  == 0 else self.width,
                    LIST_MONITOR_DEFAULT_HEIGHT if self.height == 0 else self.height,
                )
            )
        else:
            return SRMonitor(
                opcode      = new_opcode,
                dropdowns   = new_dropdowns,
                position    = position,
                is_visible  = self.visible,
            )

@grepr_dataclass(grepr_fields=["opcode", "dropdowns", "sprite", "position", "is_visible"])
class SRMonitor:
    """
    The second representation for a monitor. It is much more user friendly
    """
    
    opcode: str
    dropdowns: dict[str, SRDropdownValue]
    position: tuple[int | float, int | float] # Center of the Stage is the origin
    is_visible: bool
    
    def __post_init__(self) -> None:
        """
        Ensure that it is impossible to create a variable/list monitor without using the correct subclass

        Returns:
            None
        """
        if   self.opcode == NEW_OPCODE_VAR_VALUE:
            assert isinstance(self, SRVariableMonitor), f"Must be a SRVariableMonitor instance if opcode is {repr(NEW_OPCODE_VAR_VALUE)}"
        elif self.opcode == NEW_OPCODE_LIST_VALUE:
            assert isinstance(self, SRListMonitor), f"Must be a SRListMonitor instance if opcode is {repr(NEW_OPCODE_LIST_VALUE)}"
        else:
            assert not isinstance(self, (SRVariableMonitor, SRListMonitor)), f"Mustn't be a SRVariableMonitor or SRListMonitor if opcode is neither {repr(NEW_OPCODE_VAR_VALUE)} nor {repr(NEW_OPCODE_LIST_VALUE)}"
    
    def validate(self, path: list, config: ValidationConfig, info_api: OpcodeInfoAPI) -> None:
        """
        Ensure a SRMonitor is valid, raise ValidationError if not
        To validate the exact dropdown values you should additionally call the validate_dropdown_values method
        
        Args:
            path: the path from the project to itself. Used for better error messages
            config: Configuration for Validation Behaviour
            info_api: the opcode info api used to fetch information about opcodes
        
        Returns:
            None
        
        Raises:
            ValidationError: if the SRMonitor is invalid
            InvalidOpcodeError(ValidationError): if the opcode is not a defined opcode
            UnnecessaryDropdownError(ValidationError): if a key of dropdowns is not expected for the specific opcode
            MissingDropdownError(ValidationError): if an expected key of dropdowns for the specific opcode is missing
        """
        AA_TYPE(self, path, "opcode", str)
        AA_DICT_OF_TYPE(self, path, "dropdowns", key_t=str, value_t=SRDropdownValue)
        if config.raise_when_monitor_position_outside_stage:
            AA_BOXED_COORD_PAIR(self, path, "position", 
                min_x=-(STAGE_WIDTH //2), max_x=(STAGE_WIDTH //2), 
                min_y=-(STAGE_HEIGHT//2), max_y=(STAGE_HEIGHT//2),
            )
        else:
            AA_COORD_PAIR(self, path, "position")
        AA_TYPE(self, path, "is_visible", bool)
        
        cls_name = self.__class__.__name__
        opcode_info = info_api.get_info_by_new_safe(self.opcode)
        if (opcode_info is None) or (not opcode_info.can_have_monitor):
            raise InvalidOpcodeError(path, 
                f"opcode of {cls_name} must be a defined opcode. That block must be able to have monitors",
            )
        
        new_dropdown_ids = opcode_info.get_all_new_dropdown_ids()
        for new_dropdown_id, dropdown_value in self.dropdowns.items():
            dropdown_value.validate(path+["dropdowns", (new_dropdown_id,)], config)
            if new_dropdown_id not in new_dropdown_ids:
                raise UnnecessaryDropdownError(path, 
                    f"dropdowns of {cls_name} with opcode {repr(self.opcode)} includes unnecessary dropdown {repr(new_dropdown_id)}",
                )
        for new_dropdown_id in new_dropdown_ids:
            if new_dropdown_id not in self.dropdowns:
                raise MissingDropdownError(path, 
                    f"dropdowns of {cls_name} with opcode {repr(self.opcode)} is missing dropdown {repr(new_dropdown_id)}",
                )
    
    def validate_dropdown_values(self, 
        path: list, 
        config: ValidationConfig, 
        info_api: OpcodeInfoAPI, 
        context: PartialContext | CompleteContext,
     ) -> None:
        """
        Ensure the dropdown values of a SRMonitor are valid, raise ValidationError if not
        For validation of the monitor itself, call the validate method
        
        Args:
            path: the path from the project to itself. Used for better error messages
            config: Configuration for Validation Behaviour
            info_api: the opcode info api used to fetch information about opcodes
            context: Context about parts of the project. Used to validate dropdowns
        
        Returns:
            None
        
        Raises:
            ValidationError: if some of the dropdown values of the SRMonitor are invalid
        """
        opcode_info = info_api.get_info_by_new(self.opcode)
        for new_dropdown_id, dropdown in self.dropdowns.items():
            dropdown_type = opcode_info.get_dropdown_info_by_new(new_dropdown_id).type
            dropdown.validate_value(
                path          = path+["dropdowns", (new_dropdown_id,)],
                config        = config,
                dropdown_type = dropdown_type, 
                context       = context,
            )
    
    def to_first(self, info_api: OpcodeInfoAPI) -> FRMonitor:
        """
        Converts a SRMonitor into a FRMonitor
        
        Args:
            info_api: the opcode info api used to fetch information about opcodes
        
        
        Returns:
            the FRMonitor
        """
        return FRMonitor(
            id          = 0,
            mode        = 0,
            opcode      = 0,
            params      = 0,
            sprite_name = 0,
            value       = 0,
            x           = 0,
            y           = 0,
            visible     = 0,
            
            width       = 0,
            height      = 0,
            slider_min  = 0,
            slider_max  = 0,
            is_discrete = 0,
        )
        

@grepr_dataclass(grepr_fields=["readout_mode", "slider_min", "slider_max", "allow_only_integers"], parent_cls=SRMonitor)
class SRVariableMonitor(SRMonitor):
    """
    The second representation exclusively for variable monitors
    """
    
    readout_mode: SRVariableMonitorReadoutMode
    slider_min: int | float
    slider_max: int | float
    allow_only_integers: bool
    
    def validate(self, path: list, config: ValidationConfig, info_api: OpcodeInfoAPI):
        """
        Ensure a SRVariableMonitor is valid, raise ValidationError if not
        To validate the exact dropdown values you should additionally call the validate_dropdown_values method
        
        Args:
            path: the path from the project to itself. Used for better error messages
            config: Configuration for Validation Behaviour
            info_api: the opcode info api used to fetch information about opcodes
        
        Returns:
            None
        
        Raises:
            ValidationError: if the SRVariableMonitor is invalid
        """
        super().validate(path, config, info_api)
        AA_EQUAL(self, path, "opcode", NEW_OPCODE_VAR_VALUE)
        
        AA_TYPE(self, path, "readout_mode", SRVariableMonitorReadoutMode)
        AA_TYPE(self, path, "allow_only_integers", bool)
        if self.allow_only_integers:
            allowed_types = (int,)
            condition = "When allow_only_integers is True"
        else:
            allowed_types = (int, float)
            condition = "When allow_only_integers is False"
        AA_TYPES(self, path, "slider_min", allowed_types, condition=condition)
        AA_TYPES(self, path, "slider_max", allowed_types, condition=condition)

        AA_BIGGER_OR_EQUAL(self, path, "slider_max", "slider_min")

@grepr_dataclass(grepr_fields=["size"], parent_cls=SRMonitor)
class SRListMonitor(SRMonitor):
    """
    The second representation exclusively for list monitors
    """

    size: tuple[int | float, int | float]
    
    def validate(self, path: list, config: ValidationConfig, info_api: OpcodeInfoAPI):
        """
        Ensure a SRListMonitor is valid, raise ValidationError if not
        To validate the exact dropdown values you should additionally call the validate_dropdown_values method
        
        Args:
            path: the path from the project to itself. Used for better error messages
            config: Configuration for Validation Behaviour
            info_api: the opcode info api used to fetch information about opcodes
        
        Returns:
            None
        
        Raises:
            ValidationError: if the SRListMonitor is invalid
        """
        super().validate(path, config, info_api)
        AA_EQUAL(self, path, "opcode", NEW_OPCODE_LIST_VALUE)
        
        if config.raise_when_monitor_bigger_then_stage:
            max_x, max_y = STAGE_WIDTH, STAGE_HEIGHT
        else:
            max_x, max_y = None, None
        AA_BOXED_COORD_PAIR(self, path, "size", min_x=100, max_x=max_x, min_y=60, max_y=max_y)


__all__ = [
    "STAGE_WIDTH", "STAGE_HEIGHT", 
    "FRMonitor", "SRMonitor", "SRVariableMonitor", "SRListMonitor",
]

