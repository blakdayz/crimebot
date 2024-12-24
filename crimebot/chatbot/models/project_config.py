from pydantic import BaseModel, field_validator


class ProjectConfig(BaseModel):
    name: str
    template: str

    @field_validator("template")
    def validate_template(cls, v):
        if not v.startswith("https://github.com/") or "templates/" not in v:
            raise ValueError("Template must be a GitHub URL containing 'templates/'")
        return v
