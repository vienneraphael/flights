from pydantic import BaseModel, model_validator


class DurationConstraint(BaseModel):
    min_days: int
    max_days: int

    @model_validator(mode="before")
    @classmethod
    def check_days_order(cls, values):
        return values


class DateConstraint(BaseModel):
    pass
