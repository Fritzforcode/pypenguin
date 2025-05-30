from typing    import Any
from PIL       import Image
from xml.etree import ElementTree
from io        import BytesIO
from pydub     import AudioSegment
import wave

from pypenguin.utility import (
    grepr_dataclass, ValidationConfig, 
    AA_TYPE, AA_COORD_PAIR, AA_MIN,
    ThanksError
)

EMPTY_SVG_COSTUME_XML = "<svg version=\"1.1\" width=\"2\" height=\"2\" viewBox=\"-1 -1 2 2\" xmlns=\"http://www.w3.org/2000/svg\" xmlns:xlink=\"http://www.w3.org/1999/xlink\">\n  <!-- Exported by Scratch - http://scratch.mit.edu/ -->\n</svg>"
EMPTY_SVG_COSTUME_ROTATION_CENTER = (240, 180)


@grepr_dataclass(grepr_fields=["name", "asset_id", "data_format", "md5ext", "rotation_center_x", "rotation_center_y", "bitmap_resolution"])
class FRCostume:
    """
    The first representation for a costume. It is very close to the raw data in a project
    """
    
    name: str
    asset_id: str
    data_format: str
    md5ext: str
    rotation_center_x: int | float
    rotation_center_y: int | float
    bitmap_resolution: int | None

    @classmethod
    def from_data(cls, data: dict[str, Any]) -> "FRCostume":
        """
        Deserializes raw data into a FRSound
        
        Args:
            data: the raw data
        
        Returns:
            the FRSound
        """
        md5ext = data["md5ext"] if "md5ext" in data else f'{data["assetId"]}.{data["dataFormat"]}'
        return cls(
            name              = data["name"           ],
            asset_id          = data["assetId"        ],
            data_format       = data["dataFormat"     ],
            md5ext            = md5ext,
            rotation_center_x = data["rotationCenterX"],
            rotation_center_y = data["rotationCenterY"],
            bitmap_resolution = data.get("bitmapResolution", None),
        )

    def step(self, asset_files: dict[str, bytes]) -> "SRCostume": # TODO: update tests
        """
        Converts a FRComment into a SRComment
        
        Returns:
            the SRComment
        """
        rotation_center = (self.rotation_center_x, self.rotation_center_y)
        content_bytes = asset_files[self.md5ext]
        
        if   self.data_format == "svg":
            return SRVectorCostume(
                name              = self.name,
                file_extension    = self.data_format,
                rotation_center   = rotation_center,
                content           = ElementTree.fromstring(content_bytes.decode("utf-8")),
            )
        elif self.data_format in {"png", "jpg", "jpeg", "bmp", "gif"}:
            image = Image.open(BytesIO(content_bytes))
            image.load()  # Ensure it's fully loaded into memory
            return SRBitmapCostume(
                name              = self.name,
                file_extension    = self.data_format,
                rotation_center   = rotation_center,
                bitmap_resolution = 1 if self.bitmap_resolution is None else self.bitmap_resolution,
                content           = image,
            )
        else: raise ThanksError()

@grepr_dataclass(grepr_fields=["name", "asset_id", "data_format", "md5ext", "rate", "sample_count"])
class FRSound:
    """
    The first representation for a sound. It is very close to the raw data in a project
    """
    
    name: str
    asset_id: str
    data_format: str
    md5ext: str
    rate: int
    sample_count: int
    
    @classmethod
    def from_data(cls, data: dict[str, Any]) -> "FRSound":
        """
        Deserializes raw data into a FRSound
        
        Args:
            data: the raw data
        
        Returns:
            the FRSound
        """
        return cls(
            name         = data["name"       ],
            asset_id     = data["assetId"    ],
            data_format  = data["dataFormat" ],
            md5ext       = data["md5ext"     ],
            rate         = data["rate"       ],
            sample_count = data["sampleCount"],
        )

    def step(self, asset_files: dict[str, bytes]) -> "SRSound":
        """
        Converts a FRSound into a SRSound
        
        Returns:
            the SRSound
        """
        return SRSound(
            name           = self.name,
            file_extension = self.data_format,
            # Other attributes can be derived from the sound files
        )

@grepr_dataclass(grepr_fields=["name", "file_extension", "rotation_center"], init=False)
class SRCostume:
    """
    The second representation for a costume. It is more user friendly then the first representation.
    **Please use the subclasses SRVectorCostume and SRBitmapCostume for actual data**
    """

    name: str
    file_extension: str
    rotation_center: tuple[int | float, int | float]

    def __init__(self, name: str, file_extension: str, rotation_center: tuple[int | float, int | float]) -> None:
        """
        Create a SRInputValue. 
        **Please use the subclasses SRVectorCostume and SRBitmapCostume for concrete data. This method will raise a NotImplementedError.**

        Returns:
            None

        Raises:
            NotImplementedError: always
        """
        raise NotImplementedError("Please use the subclasses SRVectorCostume and SRBitmapCostume for concrete data")
    
    def validate(self, path: list, config: ValidationConfig) -> None:
        """
        Ensure a SRCostume is valid, raise ValidationError if not
        
        Args:
            path: the path from the project to itself. Used for better error messages
            config: Configuration for Validation Behaviour
        
        Returns:
            None
        
        Raises:
            ValidationError: if the SRCostume is invalid
        """
        AA_TYPE(self, path, "name", str)
        AA_TYPE(self, path, "file_extension", str)
        AA_COORD_PAIR(self, path, "rotation_center")

@grepr_dataclass(grepr_fields=["content"], parent_cls=SRCostume)
class SRVectorCostume(SRCostume):
    """
    The second representation for a vector(SVG) costume. It is more user friendly then the first representation
    """
    
    content: ElementTree.Element
        
    @classmethod
    def create_empty(cls, name: str = "empty") -> "SRCostume":
        return cls(
            name            = name,
            file_extension  = "svg",
            rotation_center = EMPTY_SVG_COSTUME_ROTATION_CENTER,
            content         = ElementTree.fromstring(EMPTY_SVG_COSTUME_XML),
        )
    
    def validate(self, path: list, config: ValidationConfig) -> None:
        """
        Ensure a SRVectorCostume is valid, raise ValidationError if not
        
        Args:
            path: the path from the project to itself. Used for better error messages
            config: Configuration for Validation Behaviour
        
        Returns:
            None
        
        Raises:
            ValidationError: if the SRVectorCostume is invalid
        """
        super().validate(path, config)
        
        AA_TYPE(self, path, "content", ElementTree.Element)

@grepr_dataclass(grepr_fields=["content", "bitmap_resolution"], parent_cls=SRCostume)
class SRBitmapCostume(SRCostume):
    """
    The second representation for a bitmap(usually PNG) costume. It is more user friendly then the first representation
    """
    
    content: Image.Image
    bitmap_resolution: int
    
    def validate(self, path: list, config: ValidationConfig) -> None:
        """
        Ensure a SRBitmapCostume is valid, raise ValidationError if not
        
        Args:
            path: the path from the project to itself. Used for better error messages
            config: Configuration for Validation Behaviour
        
        Returns:
            None
        
        Raises:
            ValidationError: if the SRBitmapCostume is invalid
        """
        super().validate(path, config)
        
        AA_TYPE(self, path, "content", Image.Image)
        AA_TYPE(self, path, "bitmap_resolution", int)
        AA_MIN(self, path, "bitmap_resolution", min=1)


@grepr_dataclass(grepr_fields=["name", "file_extension"])
class SRSound:
    """
    The second representation for a sound. It is more user friendly then the first representation
    """

    name: str
    file_extension: str
    
    def validate(self, path: list, config: ValidationConfig) -> None:
        """
        Ensure a SRSound is valid, raise ValidationError if not
        
        Args:
            path: the path from the project to itself. Used for better error messages
            config: Configuration for Validation Behaviour
        
        Returns:
            None
        
        Raises:
            ValidationError: if the SRSound is invalid
        """
        AA_TYPE(self, path, "name", str)
        AA_TYPE(self, path, "file_extension", str)
 

__all__ = ["FRCostume", "SRVectorCostume", "SRBitmapCostume", "FRSound", "SRCostume", "SRSound"]

