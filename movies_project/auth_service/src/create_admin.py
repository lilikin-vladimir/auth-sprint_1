import logging

from sqlalchemy import create_engine
import typer

from fastapi.encoders import jsonable_encoder
from sqlalchemy.future import select

from sqlalchemy.orm import sessionmaker


from core.config import config
from models.users import User
from models.roles import UserRole, Role
from schemas.users import UserSignUp


def main():
    try:
        logging.info('Creating Admin...')
        url = f'postgresql://' \
              f'{config.db_user}:{config.db_password}@'\
              f'{config.db_host}:{config.db_port}/'\
              f'{config.db_name}'
        engine = create_engine(url, echo=config.db_echo_engine)

        session_maker = sessionmaker(bind=engine)
        session = session_maker()

        user_data = UserSignUp(email=config.admin_email,
                               password=config.admin_password,
                               first_name='admin',
                               last_name='admin',)

        admin = session.execute(
            select(Role).
            filter(Role.title == 'admin')
        )
        if not admin.scalars().first():
            data = [User(**jsonable_encoder(user_data)),
                    Role('admin', 7)]
            for data_row in data:
                session.add(data_row)
                session.commit()
                session.refresh(data_row)

            user_role = UserRole(user_id=data[0].id,
                                 role_id=data[1].id)
            session.add(user_role)
            session.commit()
            session.refresh(user_role)
            logging.info('Admin created successfully.')
        else:
            logging.info('Admin already exists. Nothing to do.')
    except ConnectionRefusedError:
        logging.error("Нет подключения к БД")


if __name__ == '__main__':
    typer.run(main)
