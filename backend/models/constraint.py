from datetime import date

from pydantic import BaseModel, model_validator


class DurationConstraint(BaseModel):
    # min_days = minimal days of stay in a destination.
    # max_days = maximal days of  stay in a destination.

    min_days: int
    max_days: int

    @model_validator(mode="before")
    @classmethod
    def check_days_order(cls, values):
        min_days = values.get("min_days")
        max_days = values.get("max_days")
        if min_days is not None and max_days is not None:
            if min_days > max_days:
                raise ValueError("min_dauys cannot be greater than max_days")
        return values


class DateConstraint(BaseModel):
    # min_date = minimal date choose of first possible first departure and first possible last arrivals
    # max_date =  maximal date choose of last possible first departure and last possible last arrivals

    min_date: date
    max_date: date

    @model_validator(mode="before")
    @classmethod
    def check_date_order(cls, values):
        min_date = values.get("min_date")
        max_date = values.get("max_date")
        if min_date is not None and max_date is not None:
            if min_date > max_date:
                raise ValueError("min_date cannot be greater than max_date")
        return values
