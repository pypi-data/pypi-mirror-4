from validate_email import validate_email


class PeopleDatabase(object):

    """Simple database of people (names) to email addresses."""

    # Internal keys
    EMAIL = 'email'
    COMMENT = 'comment'

    def __init__(self):
        self.people = {}  # {name: {email: ..., comment: ...}}

    def add_person(self, person, email_address=None, comment=None):
        if email_address is not None and not validate_email(email_address):
            raise ValueError('Invalid email address')
        self.people[person] = {self.EMAIL: email_address, self.COMMENT: comment}

    def has_person(self, name):
        return name in self.people

    def get_email_address(self, person):
        return self.people[person][self.EMAIL]

    def get_comment(self, person):
        return self.people[person][self.COMMENT]

    def set_email_address(self, person, email_address):
        if person not in self.people:
            raise KeyError('Person does not exist')
        if email_address is not None and not validate_email(email_address):
            raise ValueError('Invalid email address')
        self.people[person][self.EMAIL] = email_address

    def set_comment(self, person, comment):
        if person not in self.people:
            raise KeyError('Person does not exist')
        self.people[person][self.COMMENT] = comment

    def delete_person(self, person):
        if person not in self.people:
            raise KeyError('Person does not exist')
        del self.people[person]

    def reset(self):
        self.people.clear()


# Database instance.
people_database = PeopleDatabase()
