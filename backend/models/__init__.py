# models/__init__.py
#
# Import all ORM models here so that SQLAlchemy's Base.metadata
# has them registered before create_all() is called in init_db.py.
#
# Without these imports, Base.metadata.create_all() would not know
# about the Mentor, Parent, and Booking tables, even if the classes exist.

from models.mentor import Mentor  # noqa: F401
from models.parent import Parent  # noqa: F401
from models.course import Course  # noqa: F401
from models.booking import Booking  # noqa: F401
