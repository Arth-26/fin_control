from typing import Annotated

from fastapi import Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from fin_control.database import get_session
from fin_control.models import User
from fin_control.schemas.base_schemas import FilterPage
from fin_control.security import get_request_user

T_Session = Annotated[AsyncSession, Depends(get_session)]
Request_User = Annotated[User, Depends(get_request_user)]
T_Filter_Page = Annotated[FilterPage, Query()]
