# Copyright 2012 John Sullivan
# Copyright 2012 Other contributers as noted in the CONTRIBUTERS file
#
# This file is part of Galah.
#
# Galah is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Galah is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Galah.  If not, see <http://www.gnu.org/licenses/>.

from inspect import getargspec
from copy import deepcopy
from bson import ObjectId
from bson.errors import InvalidId
from galah.db.models import *
import json
from collections import namedtuple
from mongoengine import ValidationError
from galah.sisyphus.api import send_task

from galah.base.config import load_config
config = load_config("web")

#: An anonymous admin user useful when accessing this module from the local
#: system.
admin_user = namedtuple("User", "account_type")("admin")

class UserError(Exception):
    def __init__(self, what):
        self.what = str(what)

    def __str__(self):
        return self.what

class PermissionError(UserError):
    def __init__(self, *args, **kwargs):
        UserError.__init__(self, *args, **kwargs)

class APICall(object):
    """Wraps an API call and handles basic permissions along with providing a
    simple interface to get meta data on the API call.
    
    """
    
    __slots__ = ("wrapped_function", "allowed", "argspec", "name")
    
    def __init__(self, wrapped_function, allowed = None):
        #: The raw function we are wrapping that performs the actual logic.
        self.wrapped_function = wrapped_function
        
        #: The account types that are allowed to call this function, if None 
        #: any account type may call this function.
        self.allowed = allowed
        
        #: Information about the arguments this API call accepts in the same
        #: format :func: inspect.getargspec returns.
        self.argspec = getargspec(wrapped_function)
        
        #: The name of the wrapped function.
        self.name = wrapped_function.func_name
        
    def __call__(self, current_user, *args, **kwargs):
        arg_spec = getargspec(self.wrapped_function)
        
        # If no validation is required this won't actually be a problem, however
        # it's certainly not something that you should be doing.
        if not hasattr(current_user, "account_type"):
            raise ValueError("current_user is not a valid user object.")
        
        # Check if the current user has permisson to perform this operation
        if self.allowed and current_user.account_type not in self.allowed:
            raise PermissionError(
                "Only %s users are allowed to call %s" %
                    (
                        " or ".join(self.allowed),
                        self.wrapped_function.func_name
                    )
            )
        
        # Only pass the current user to the function if the function wants it
        if len(self.argspec[0]) != 0 and self.argspec[0][0] == "current_user":
            return self.wrapped_function(current_user, *args, **kwargs)
        else: 
            return self.wrapped_function(*args, **kwargs)

from decorator import decorator

def _api_call(allowed = None):
    """Decorator that wraps a function with the :class: APICall class."""
    
    if isinstance(allowed, basestring):
        allowed = (allowed, )

    def inner(func):
        return APICall(func, allowed)

    return inner

## Some useful low level functions ##
def _get_user(email, current_user):
    if email == "me":
        return current_user

    try:
        return User.objects.get(email = email)
    except User.DoesNotExist:
        raise UserError("User %s does not exist." % email)

def _user_to_str(user):
    return "User [email = %s, account_type = %s]" % \
            (user.email, user.account_type)

def _get_assignment(query, current_user):
    # Check if class/assignment syntax was used.
    if "/" in query:
        parts = query.split("/", 1)

        if parts[0] == "mine":
            class_string = "classes you are enrolled in or assigned to"

            matches = list(Assignment.objects(
                for_class__in = current_user.classes,
                name__icontains = parts[1]
            ))
        else:
            the_class = _get_class(parts[0])

            class_string = _class_to_str(the_class)

            matches = list(Assignment.objects(
                for_class = the_class.id,
                name__icontains = parts[1]
            ))

        if not matches:
            raise UserError(
                "No assignments in %s matched your query of {name "
                "contains '%s'}." % (class_string, parts[1])
            )
        elif len(matches) == 1:
            return matches[0]
        else:
            raise UserError(
                "%d assignments in %s matched your query of {name "
                "contains '%s'}, however this API expects 1 assignment. Refine "
                "your query and try again.\n\t%s" % (
                    len(matches),
                    class_string,
                    parts[1],
                    "\n\t".join(_assignment_to_str(i) for i in matches)
                )
            )

    try:
        return Assignment.objects.get(id = ObjectId(query))
    except Assignment.DoesNotExist:
        raise UserError("Assignment with ID %s does not exist." % query)
    except InvalidId:
        raise UserError("Assignment ID %s is not a valid ID." % query)

def _assignment_to_str(assignment):
    return "Assignment [id = %s, name = %s]" % (assignment.id, assignment.name)

def _get_class(query, instructor = None):
    try:
        query_dict = {"id": ObjectId(query)}
        if instructor:
            query_dict["id__in"] = instructor.classes

        # Check if the user provided a valid ObjectId
        return Class.objects.get(**query_dict)
    except (Class.DoesNotExist, InvalidId):
        pass

    query_dict = {"name__icontains": query}
    if instructor:
        query_dict["id__in": instructor.classes]

    matches = list(Class.objects(**query_dict))
    
    if not matches:
        raise UserError("No classes matched your query of '%s'." % query)    
    elif len(matches) == 1:
        return matches[0]
    else:
        raise UserError(
            "%d classes match your query of '%s', however, this API expects 1 "
            "class. Refine your query and try again.\n\t%s" % (
                len(matches),
                query, 
                "\n\t".join(_class_to_str(i) for i in matches)
            )
        )

def _class_to_str(the_class):
    return "Class [id = %s, name = %s]" % (the_class.id, the_class.name)
        
import datetime
def _to_datetime(time):
    try:
        return datetime.datetime(time)
    except TypeError:
        pass
        
    try:
        return datetime.datetime.strptime(time, "%m/%d/%Y %H:%M:%S")
    except (OverflowError, ValueError):
        raise ValueError(
            "Could not convert %s into a time object." % repr(time)
        )

def _datetime_to_str(time):
    return datetime.datetime.strftime(time, "%m/%d/%Y %H:%M:%S")
        
## Below are the actual API calls ##
@_api_call()
def get_api_info():
    # TODO: This function should be memoized
    
    api_info = []
    for k, v in api_calls.items():
        api_info.append({"name": k})
        current = api_info[-1]
        
        # Loop through all the arguments the function takes in and add
        # information on each argument to the api_info
        current["args"] = []
        for i in xrange(len(v.argspec.args)):
            current["args"].append({"name": v.argspec.args[i]})
            
            if v.argspec.defaults:
                # The number of arguments without default values
                ndefaultless = len(v.argspec.args) - len(v.argspec.defaults)
                
                # If the current argument has a default value make note of it
                if ndefaultless <= i:
                    current["args"][-1].update({
                        "default_value": v.argspec.defaults[i - ndefaultless]
                    })
    
    return json.dumps(api_info, separators = (",", ":"))

@_api_call()
def whoami(current_user):
    if hasattr(current_user, "id"):
        return current_user.id
    else:
        return "Anonymous"

@_api_call()
def get_oauth2_keys():
    from galah.web import app
    import json

    google_api_keys = {
        "CLIENT_ID": app.config["GOOGLE_APICLIENT_ID"],
        "CLIENT_SECRET": app.config["GOOGLE_APICLIENT_SECRET"]
    }

    return json.dumps(google_api_keys, separators = (",", ":"))

from galah.base.crypto.passcrypt import serialize_seal, seal
from mongoengine import OperationError
@_api_call("admin")
def create_user(email, password = "", account_type = "student"):
    new_user = User(
        email = email, 
        account_type = account_type
    )

    if password:
        new_user.seal = serialize_seal(seal(password))
    
    try:
        new_user.save(force_insert = True)
    except OperationError:
        raise UserError("A user with that email already exists.")
    
    return "Success! %s created." % _user_to_str(new_user)

@_api_call("admin")
def reset_password(current_user, email, new_password = ""):
    the_user = _get_user(email, current_user)

    if new_password:
        the_user.seal = serialize_seal(seal(new_password))
    else:
        the_user.seal = None

    the_user.save()

    return "Success! Password for %s succesfully reset." \
                % _user_to_str(the_user)

@_api_call("admin")
def modify_user(current_user, email, account_type):
    the_user = _get_user(email, current_user)

    old_user_string = _user_to_str(the_user)

    the_user.account_type = account_type

    try:
        the_user.save()
    except ValidationError:
        raise UserError("%s is not a valid account type." % account_type)

    return "Success! %s has been retyped as a %s" \
                % (old_user_string, account_type)

@_api_call(("admin", "teacher"))
def find_user(current_user, email_contains = "", account_type = "",
              enrolled_in = "", max_results = "20"):
    max_results = int(max_results)

    query = {}
    query_description = []

    if email_contains:
        query["email__icontains"] = email_contains
        query_description.append("email contains '%s'" % email_contains)

    if account_type:
        query["account_type"] = account_type
        query_description.append("account type is '%s'" % account_type)

    if enrolled_in:
        the_class = _get_class(enrolled_in)
        query["classes"] = the_class.id
        query_description.append("enrolled in %s" %
                _class_to_str(the_class))

    matches = list(User.objects(**query)[:max_results + 1])

    # Check if there are more than max_results results
    plus = ""
    if len(matches) > max_results:
        matches.pop()
        plus = "+"

    if query_description:
        query_description = ",".join(query_description)
    else:
        query_description = "any"

    result_string = "\n\t".join(_user_to_str(i) for i in matches)

    return "%d%s user(s) found matching query {%s}.\n\t%s" % \
            (len(matches), plus, query_description, result_string)

@_api_call(("admin", "teacher"))
def user_info(current_user, email):
    user = _get_user(email, current_user)

    enrolled_in = Class.objects(id__in = user.classes)

    class_list = "\n\t".join(_class_to_str(i) for i in enrolled_in)

    if not enrolled_in:
        return "%s is not enrolled in any classes." % _user_to_str(user)
    else:
        return "%s is enrolled in:\n\t%s" % (_user_to_str(user), class_list)

@_api_call("admin")
def delete_user(current_user, email):    
    to_delete = _get_user(email, current_user)

    to_delete.delete()
        
    return "Success! %s deleted." % _user_to_str(to_delete)
    
@_api_call(("admin", "teacher"))
def find_class(current_user, name_contains = "", enrollee = ""):
    if not enrollee and current_user.account_type != "admin":
        query = {"id__in": current_user.classes}
        instructor_string = "You are"
    elif enrollee == "any" or current_user.account_type == "admin":
        query = {}
        instructor_string = "Anyone is"
    else:
        the_instructor = _get_user(enrollee, current_user)
        query = {"id__in": the_instructor.classes}
        instructor_string = _user_to_str(the_instructor) + " is"
        
    if name_contains:
        query["name__icontains"] = name_contains

    matches = list(Class.objects(**query))

    result_string = "\n\t".join(_class_to_str(i) for i in matches)

    return "%s teaching %d class(es) with '%s' in their name.\n\t%s" % \
            (instructor_string, len(matches), name_contains, result_string)

@_api_call(("admin", "teacher"))
def enroll_student(current_user, email, enroll_in):
    user = _get_user(email, current_user)

    if current_user.account_type != "admin" and \
            user.account_type == "teacher":
        raise PermissionError("Only admins can assign teachers to classes.")
    
    the_class = _get_class(enroll_in)

    if the_class.id in user.classes:
        raise UserError("%s is already enrolled in %s." %
            (_user_to_str(user), _class_to_str(the_class))
        )
            
    user.classes.append(the_class.id)
    user.save()
    
    return "Success! %s enrolled in %s." % (
        _user_to_str(user), _class_to_str(the_class)
    )

@_api_call("admin")
def assign_teacher(current_user, email, assign_to):
    return enroll_student(current_user, email, assign_to)

@_api_call(("admin", "teacher"))
def drop_student(current_user, email, drop_from):    
    if current_user.account_type == "admin":
        the_class = _get_class(drop_from)
    else:
        the_class = _get_class(drop_from, current_user)

    user = _get_user(email, current_user)
        
    if the_class.id not in user.classes:
        raise UserError("%s is not enrolled in %s." %
            (_user_to_str(user), _class_to_str(the_class))
        )
    
    user.classes.remove(the_class.id)
    user.save()
    
    return "Success! Dropped %s from %s." % (
        _user_to_str(user), _class_to_str(the_class)
    )

@_api_call(("admin", "teacher"))
def unassign_teacher(current_user, email, drop_from):
    return drop_student(current_user, email, drop_from)

@_api_call(("admin", "teacher"))
def class_info(for_class):
    the_class = _get_class(for_class)

    assignments = Assignment.objects(for_class = the_class.id)
    if assignments:
        assignments_string = "\n\t".join(
            _assignment_to_str(i) for i in assignments
        )
    else:
        assignments_string = "(No assignments)"

    return _class_to_str(the_class) + " has assignments:\n\t" + \
            assignments_string

@_api_call("admin")
def create_class(name):
    new_class = Class(name = name)
    new_class.save()
    
    return "Success! %s created." % _class_to_str(new_class)

@_api_call("admin")
def modify_class(the_class, name):
    if not name:
        raise UserError("name cannot be empty.")

    the_class = _get_class(the_class)

    old_class_string = _class_to_str(the_class)

    the_class.name = name

    the_class.save()

    return "Success! %s has been renamed to '%s'" % (old_class_string, name)

@_api_call("admin")
def delete_class(to_delete):
    the_class = _get_class(to_delete)
        
    # Get all of the assignments for the class
    assignments = \
        [str(i.id) for i in Assignment.objects(for_class = the_class.id)]
    
    send_task(
        config["SISYPHUS_ADDRESS"],
        "delete_assignments",
        assignments,
        str(the_class.id)
    )

    return (
        "%s has been queued for deletion. Please allow a few minutes for the "
        "task to complete." % _class_to_str(the_class)
    )

@_api_call(("admin", "teacher"))
def create_assignment(current_user, name, due, for_class, due_cutoff = "",
                      hide_until = ""):
    # The attributes of the assignmnet we're creating
    atts = {"name": name}

    atts["due"] = _to_datetime(due)

    if due_cutoff:
        atts["due_cutoff"] = _to_datetime(due_cutoff)

    if hide_until:
        atts["hide_until"] = _to_datetime(hide_until)

    the_class = _get_class(for_class)

    if current_user.account_type != "admin" and \
            the_class.id not in current_user.classes:
        raise PermissionError(
            "You cannot create an assignment for a class you are not teaching."
        )

    atts["for_class"] = the_class.id

    print atts
    new_assignment = Assignment(**atts)
    new_assignment.save()
    
    return "Success! %s created." % _assignment_to_str(new_assignment)

@_api_call(("admin", "teacher"))
def assignment_info(current_user, id):
    assignment = _get_assignment(id, current_user)

    attribute_strings = []
    for k, v in assignment._data.items():
        if k and v:
            if type(v) is datetime.datetime:
                v = _datetime_to_str(v)

            attribute_strings.append("%s = %s" % (k, v))

    attributes = "\n\t".join(attribute_strings)

    return "Properties of %s:\n\t%s" \
                % (_assignment_to_str(assignment), attributes)

@_api_call(("admin", "teacher"))
def modify_assignment(current_user, id, name = "", due = "", for_class = "",
                      due_cutoff = "", hide_until = ""):
    assignment = _get_assignment(id, current_user)

    # Save the string representation of the original assignment show we can show
    # it to the user later.
    old_assignment_string = _assignment_to_str(assignment)

    if current_user.account_type != "admin" and \
            assignment.for_class not in current_user.classes:
        raise PermissionError(
            "You can only modify assignments for classes you teach."
        )

    change_log = []

    if name:
        change_log.append(
            "Name changed from '%s' to '%s'." % (assignment.name, name)
        )

        assignment.name = name

    if due:
        due_date = _to_datetime(due)

        change_log.append(
            "Due date changed from '%s' to '%s'."
                % (_datetime_to_str(assignment.due), _datetime_to_str(due_date))
        )

        assignment.due = due_date

    if due_cutoff:
        if due_cutoff.lower() == "none":
            cutoff_date = None
        else:
            cutoff_date = _to_datetime(due_cutoff)

        change_log.append(
            "Cutoff date changed from '%s' to '%s'."
                % (
                    _datetime_to_str(assignment.due_cutoff),
                    _datetime_to_str(cutoff_date)
                )
        )

        assignment.due_cutoff = cutoff_date

    if hide_until:    
        if hide_until.lower() == "none":
            hide_until = datetime.datetime.min
        else:
            hide_until = _to_datetime(hide_until)

        change_log.append(
            "Hide-until date changed from '%s' to '%s'."
                % (str(assignment.hide_until), str(hide_until))
        )

        assignment.hide_until = hide_until

    if for_class:
        old_class = Class.objects.get(id = ObjectId(assignment.for_class))
        new_class = _get_class(for_class)

        change_log.append(
            "Class changed from %s to %s."
                % (_class_to_str(old_class), _class_to_str(new_class))
        )

        assignment.for_class = new_class.id

        if current_user.account_type != "admin" and \
                assignment.for_class not in current_user.classes:
            raise PermissionError(
                "You cannot reassign an assignment to a class you're not "
                "teaching."
            )

    assignment.save()

    if change_log:
        change_log_string = "\n\t".join(change_log)
    else:
        change_log_string = "(No changes)"

    return "Success! The following changes were applied to %s.\n\t%s" \
                % (old_assignment_string, change_log_string)

@_api_call(("admin", "teacher"))
def delete_assignment(current_user, id):
    to_delete = _get_assignment(id, current_user)

    if current_user.account_type != "admin" and \
            to_delete.for_class not in current_user.classes:
        raise PermissionError(
            "You cannot delete an assignment for a class you're not teaching."
        )

    send_task(
        config["SISYPHUS_ADDRESS"],
        "delete_assignments",
        [str(to_delete.id)],
        ""
    )
    
    return (
        "%s has been queued for deletion. Please allow a few minutes for the "
        "task to complete." % _assignment_to_str(to_delete)
    )

@_api_call(("admin", "teacher"))
def get_archive(current_user, assignment, email = ""):
    # tar_tasks imports galahweb because it wants access to the logger, to
    # prevent a circular dependency we won't load the module until we need it.
    the_assignment = _get_assignment(assignment, current_user)

    if current_user.account_type != "admin" and \
            the_assignment.for_class not in current_user.classes:
        raise PermissionError(
            "You can only modify assignments for classes you teach."
        )

    # Create the task ID here rather than inside sisyphus so that we can tell
    # the user how to find the archive once its done.
    task_id = ObjectId()

    # We will not perform the work of archiving right now but will instead pass
    # if off to the heavy lifter to do it for us.
    send_task(
        config["SISYPHUS_ADDRESS"],
        "tar_bulk_submissions",
        str(task_id),
        current_user.email,
        str(the_assignment.id),
        email
    )
    
    return (
        "Your archive is being created.",
        {
            "X-Download": "archives/" + str(task_id),
            "X-Download-DefaultName": "submissions.tar.gz"
        }
    )

from types import FunctionType
api_calls = dict((k, v) for k, v in globals().items() if isinstance(v, APICall))

if __name__ == "__main__":
    import json
    print get_api_info("current_user")
