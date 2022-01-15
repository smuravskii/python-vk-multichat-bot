from peewee import *

database = SqliteDatabase('database.db')


class BaseModel(Model):
    id = PrimaryKeyField(unique=True)

    class Meta:
        database = database


class User(BaseModel):
    vk_id = IntegerField(null=False)
    username = CharField(null=False)
    in_chat = BlobField(null=False, default=False)
    is_admin = BlobField(null=False, default=False)
    is_banned = BlobField(null=False, default=False)
    ls_with = IntegerField(null=False, default=0)


class Massage(BaseModel):
    text = CharField(null=False)
    user_id = CharField(null=False)


class DB:
    @staticmethod
    def create_user_nick(vk_id: int, username: str) -> bool:
        try:
            User.get_or_create(vk_id=vk_id, username=username)
            return True
        except Exception as e:
            print(e)
            return False

    @staticmethod
    def add_massage(text: str, user_id: int) -> bool:
        try:
            Massage.get_or_create(text=text, user_id=user_id)
            return True
        except Exception as e:
            print(e)
            return False

    @staticmethod
    def get_all_massages():
        try:
            query = Massage.select()
            return query.execute()
        except Exception as e:
            print(e)
            return False

    @staticmethod
    def get_massages_by_id(_id):
        try:
            query = Massage.select().where(Massage.user_id == _id)
            return query.execute()
        except Exception as e:
            print(e)
            return False

    @staticmethod
    def get_online_users():
        try:
            query = User.select().where(User.in_chat == True)
            return query.execute()
        except Exception as e:
            print(e)
            return False

    @staticmethod
    def user_direct_massaging(_id: int, ls_id: int) -> bool:
        try:
            query = User.update(ls_with=ls_id).where(User.id == _id)
            query.execute()
            return True
        except Exception as e:
            print(e)
            return False

    @staticmethod
    def update_user_nick(vk_id: int, username: str) -> bool:
        try:
            query = User.update(username=username).where(User.vk_id == vk_id)
            query.execute()
            return True
        except Exception as e:
            print(e)
            return False

    @staticmethod
    def set_in_chat(vk_id: int, status: bool) -> bool:
        try:
            query = User.update(in_chat=status).where(User.vk_id == vk_id)
            query.execute()
            return True
        except Exception as e:
            print(e)
            return False

    @staticmethod
    def set_ban(_id: int, status: bool) -> bool:
        try:
            query = User.update(is_banned=status).where(User.id == _id)
            query.execute()
            return True
        except Exception as e:
            print(e)
            return False

    @staticmethod
    def get_user_by_vk_id(vk_id: int):
        try:
            return User.get(User.vk_id == vk_id)
        except Exception as e:
            return False

    @staticmethod
    def get_user_by_id(_id: int):
        try:
            return User.get(User.id == _id)
        except Exception as e:
            return False

    @staticmethod
    def get_users_for_msg(_id: int):
        try:
            query = User.select().where(User.id != _id, User.in_chat == True)
            query.execute()

            users_ids = []
            for i in query:
                users_ids.append(i.vk_id)

            return users_ids
        except Exception as e:
            print(e)
            return False


def main():
    database.create_tables([User, Massage])
    User.create(vk_id=1, username='Admin')


if __name__ == '__main__':
    main()


