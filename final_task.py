
from collections import defaultdict, UserDict
from datetime import datetime, timedelta
import pickle

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return str(self.value)


class Name(Field):
    def __init__(self, name=None):
        if name is None:
            raise ValueError
        super().__init__(name)


class Phone(Field):
    def __init__(self, value):
        super().__init__(value) 
        self.__value = None
        self.value = value

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        if len(value) == 10 and value.isdigit():
            self.__value = value
        else:
            raise ValueError('Invalid phone number')


class Birthday(Field):
    def __init__(self, value):
        try:
            datetime.strptime(value, "%d.%m.%Y")  
            super().__init__(value)  
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = list()
        self.birthday = None

    def add_phone(self, phone_number): 
        if self.find_phone(phone_number):
            return
        self.phones.append(Phone(phone_number))

    def remove_phone(self, phone_number): 
        phone_number = self.find_phone(phone_number)
        if phone_number:
            self.phones.remove(phone_number)
            return
        raise ValueError("Phone number not found!")
    
    def edit_phone(self, old_phone_number, new_phone_number):
        phone_number = self.find_phone(old_phone_number)
        if phone_number:
            phone_number.value = new_phone_number
            return
        raise ValueError("Phone number not found!")

    def find_phone(self, phone_number): 
        for p in self.phones:
            if p.value == phone_number:
                return p

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)
    
    def __str__(self):
        return f'Record(Name: {self.name} Phones: {self.phones} Birthday: {self.birthday})'
    
    def __repr__(self):
        return f'Record(Name: {self.name} Phones: {self.phones} Birthday: {self.birthday})'

    
class AddressBook(UserDict):
    def add_record(self, record: Record): 
        name = record.name.value
        self.data.update({name: record}) 

    def find(self, name):
        return self.get(name)

    def delete(self, name):
        del self[name]

    def find_next_weekday(self, weekday: int):  
        days_ahead = weekday - self.data()  
        if days_ahead <= 0:  
            days_ahead += 7  
        return self.data() + timedelta(days=days_ahead)  

    def get_upcoming_birthdays(self):                                                               
        days = 7
        today_date = datetime.today().date()
        upcoming_birthdays = []
        for el in self.data.values():
            birthday_this_year = datetime.strptime(el.birthday.value, "%d.%m.%Y").date().replace(year=today_date.year)
            if birthday_this_year < today_date:
                birthday_this_year = birthday_this_year.replace(year=today_date.year + 1)           
            elif 0 <= (birthday_this_year - today_date).days <= days:
                if birthday_this_year.weekday() >= 5:
                    birthday_this_year.find_next_weekday(birthday_this_year, 0)
                congratulation_date = birthday_this_year.strftime("%d.%m.%Y")            
                upcoming_birthdays.append({'Name': el.name, "Congratulation Date": congratulation_date})
        return upcoming_birthdays


def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return "There is no such name in my contacts."
        except ValueError:
            return "Give a name and a ten-digit phone number, please"
        except IndexError:
            return "Give me a contact name please"
    return wrapper

def input_error_birthday(func):                                                                            
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:                                                                          
            return "Wrong Input format! Please, enter Name and use date format: DD.MM.YYYY."
    return inner

def show_command():
    return ("1. add [name] [phone]: Add new contact with name and phone, or add an additional phone or an existing contact.\n"
          "2. change [name] [old phone] [new phone]: Change the phone number for the specified contac.\n"
          "3. phone [name]: Show the phone number for the specified contact.\n"
          "4. all: Show all contacts in the address book.\n"
          "5. add-birthday [name] [дата народження]: Add birthday for the specified contact.\n"
          "6. show-birthday [name]: Show birthday for the specified contact.\n"
          "7. birthdays: Show birthdays that will happen in the next week.\n"
          "8. hello: Take a greeting from the bot\n"
          "9. close or exit: close the programm.")


@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message


@input_error
def change_contact(args, book: AddressBook):
    name, old_phone_number, new_phone_number, *_ = args
    record = book.find(name)
    if record:
        phone = record.find_phone(old_phone_number) 
        if phone:
            record.edit_phone(old_phone_number, new_phone_number) 
            message = "Phone number was changed."
        else:
            message = "Phone was not found."
            pass
    elif record is None:
        message = "Contact is missing."
    return message


@input_error
def show_phones(args, book: AddressBook):
    name, *_ = args
    record = book.find(name)
    if record:
        return record.phones
    else:
        return "Contact is missing."


@input_error_birthday
def add_birthday(args, book: AddressBook):
    name, birthday, *_ = args
    record = book.find(name)
    if record:
        record.add_birthday(birthday)
        return "Birthday was added."
    else:
        return "Contact is mising."


@input_error_birthday
def show_birthday(args, book: AddressBook):
    name, *_ = args
    record = book.find(name)
    if record:
        return record.birthday
    else:
        return "Contact is missing"


def birthdays(book: AddressBook):
    return book.get_upcoming_birthdays()


def parse_input(user_input):
    command, *args = user_input.split()
    command = command.strip().lower()
    return command, *args


def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()


def main():
    book = load_data()
    print("Welcome to the assistant bot! To view all available commands type 'show-command'")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)
        
        if command in ["close", "exit"]:
            save_data(book)
            print("Good bye!")
            break
        elif command == "show-command":
            print(show_command())
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phones(args, book))
        elif command == "all":
            print(f'All contacts: {book}')
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(book))
        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()