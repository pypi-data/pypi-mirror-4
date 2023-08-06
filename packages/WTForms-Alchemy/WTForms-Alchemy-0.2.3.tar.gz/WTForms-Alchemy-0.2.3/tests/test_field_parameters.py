from datetime import date
import sqlalchemy as sa
from wtforms_alchemy import DateRange
from wtforms.validators import NumberRange
from tests import ModelFormTestCase


class TestFieldParameters(ModelFormTestCase):
    def test_assigns_labels_from_column_info(self):
        self.init(info={'label': 'Test Column'})
        self.assert_label('test_column', 'Test Column')

    def test_assigns_description_from_column_info(self):
        self.init(info={'description': 'Description'})
        self.assert_description('test_column', 'Description')

    def test_does_not_add_default_value_if_default_is_callable(self):
        self.init(default=lambda: "test")
        self.assert_default('test_column', None)

    def test_assigns_scalar_defaults(self):
        self.init(default=u"test")
        self.assert_default('test_column', "test")

    def test_min_and_max_info_attributes_generate_number_range_validator(self):
        self.init(type_=sa.Integer, info={'min': 1, 'max': 100})
        validator = self.get_validator('test_column', NumberRange)
        assert validator.min == 1
        assert validator.max == 100

    def test_min_and_max_info_attributes_generate_date_range_validator(self):
        self.init(
            type_=sa.Date,
            info={'min': date(1990, 1, 1), 'max': date(2000, 1, 1)}
        )
        validator = self.get_validator('test_column', DateRange)
        assert validator.min == date(1990, 1, 1)
        assert validator.max == date(2000, 1, 1)
