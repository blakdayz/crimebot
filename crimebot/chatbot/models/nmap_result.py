from pydantic import BaseModel, field_validator


class NmapScanIn(BaseModel):
    target: str

    @field_validator("target")
    def validate_target(cls, v):
        if not v:
            raise ValueError("Target cannot be empty")
        return v
