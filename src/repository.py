import abc
import model as model


# class AbstractTransactionRepository(abc.ABC):
#     def add(self, transaction: model.Transaction):
#         raise NotImplementedError

#     def get(self, transaction_id: int) -> model.Transaction:
#         raise NotImplementedError


# class SqlAlchemyTransactionRepository(AbstractTransactionRepository):

#     def __init__(self, session):
#         self.session = session

#     def add(self, transaction: model.Transaction):
#         self.session.add(transaction)

#     def get(self, transaction_id: int) -> model.Transaction:
#         return self.session.query(model.Transaction).filter_by(id=transaction_id).first()

#     def list(self):
#         return self.session.query(model.Transaction).all()


# class AbstractUserRepository(abc.ABC):

#     def add(self, user: model.User):
#         self.session.add(user)

#     def get(self, user_id: int) -> model.Transaction:
#         raise NotImplementedError


# class SqlAlchemyUserRepository(AbstractUserRepository):

#     def __init__(self, session):
#         self.session = session

#     def add(self, user: model.User):
#         self.session.add(user)

#     def get(self, user_id: int) -> model.User:
#         return self.session.query(model.User).filter_by(id=user_id).first()

#     def list(self):
#         return self.session.query(model.User).all()


# now add abstractaccount sqlalchemyaccount
class AbstractAccountRepository(abc.ABC):
    def add(self, account: model.Account):
        self.session.add(account)

    def get(self, account_id: int) -> model.Account:
        return self.session.query(model.Account).filter_by(id=account_id).first()


class SqlAlchemyAccountRepository(AbstractAccountRepository):
    def __init__(self, session):
        self.session = session

    def add(self, account: model.Account):
        self.session.add(account)

    def get(self, account_id: int) -> model.User:
        return self.session.query(model.User).filter_by(id=account_id).first()

    def list(self):
        return self.session.query(model.User).all()
