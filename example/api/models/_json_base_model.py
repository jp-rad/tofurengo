from pydantic import BaseModel, model_validator


class JsonBaseModel(BaseModel):
    @model_validator(mode="before")
    @classmethod
    def validate_json(cls, value):
        if isinstance(value, str):
            return cls.model_validate_json(value)
        return value
