from collections import defaultdict
import inspect
import os
import re
import sys
import types
import typing as T



def create_unique_name(cls, name):
    return f"__{cls.__name__}__{name}"


def arg_names(func):
    """
    Return the argument names used in the definition of the function.
    """
    names = list(inspect.getfullargspec(func).args)[:]  # pylint: disable=no-member
    return names


def strip_multiline_strings(text):
    chunks = text.split('"""')
    inside = False
    output = []
    for chunk in chunks:
        if not inside:
            output.append(chunk)
        inside = not inside
    return "".join(output)


def member_comments(class_obj: type, classes_to_ignore: T.Set[type]) -> T.Dict[str, T.List[str]]:
    """
    Print the entire class, reducing the inheritance.
    Note this will lose comments that are written outside of method defs.
    """

    # Track comments for each member.
    members = {}

    # Keep a buffer of comments to emit when we find a member in the source.
    pending_comments = []

    # Walk down the inheritance "method-resolution-order"
    for cls in class_obj.mro():
        if cls == object:
            break
        if cls in classes_to_ignore:
            continue

        # Get the definition source for this class, without multi-line strings
        raw_source = "".join(inspect.getsourcelines(cls)[0])
        sourcelines = strip_multiline_strings(raw_source).splitlines()

        # Look at each line of the source, skipping the class def
        for line in sourcelines[1:]:

            # skip empty lines and weird stuff
            if line.strip() and not line.startswith("    "):
                print("skipping weird stuff")
                print(line.rstrip())
                continue

            # buffer comments for later
            if line.startswith("    #"):
                pending_comments.append(line.rstrip())
                continue

            if line.startswith("    def") or line.startswith("    @property"):
                # clear the comments and ignore method
                pending_comments = []
                continue

            # Parse potential member definitions
            if len(line) > 4 and line[4] != " ":
                words = [word.strip() for word in line.split()]
                name = words[0]
                if name in members:
                    raise KeyError(line)  # XXX
                    # Skip members we've already defined, and drop comments.
                    pending_comments = []
                    continue

                # Group the buffered comments into a single string.
                if pending_comments:
                    leading_comment = "\n".join(pending_comments)
                else:
                    leading_comment = None

                # Attempt to grab a trailing comment from this line
                if "#" in line:
                    _, comment = line.split("#", 1)
                    trailing_comment = "#" + comment
                else:
                    trailing_comment = None

                # Save the comments for this member
                members[create_unique_name(cls, name)] = (leading_comment, trailing_comment)

                # Clear the comments
                pending_comments = []
    return members


PY2_SUPER_PATTERN = re.compile("(.*)super\((.*), self\)\.(.*)")


def member_history(cls, output_parent_classes=tuple(), new_name=None):
    lines = []
    if new_name is None:
        new_name = f"{cls.__name__}Flat"

    # Go through all the objects
    ancestors = cls.mro()

    if not output_parent_classes:
        parents = ["object"]
    else:
        parents = [p.__name__ for p in output_parent_classes]

    classes_to_ignore = set()
    for parent in output_parent_classes:
        for ancestor in parent.mro():
            classes_to_ignore.add(ancestor)

    comments = member_comments(cls, classes_to_ignore)

    lines.append(f"class {new_name}({', '.join(p for p in parents)}):")
    # Then iterate over members of just the top class
    for member_type in ("attr", "property", "method"):
        for name, member in inspect.getmembers(cls):
            if name.startswith("__"):
                continue
            try:
                inspect.getsourcelines(member)
                if member_type != "method":
                    continue
            except:
                if member_type == "method":
                    continue
                # we are either attr or property
                if isinstance(member, property):
                    if member_type != "property":
                        continue
                elif member_type == "property":
                    continue

            # gross
            if member_type == "attr":
                lines.append("")

            latest = None
            previous = None
            set_any = False
            owner = None  # wtf was this?
            for ancestor in reversed(ancestors):
                # if this ancestor changed the value
                try:
                    anc_value = getattr(ancestor, name)
                except AttributeError:
                    continue
                if latest is None or anc_value != latest:
                    if latest is not None and set_any:
                        print(f"{name} changed from {latest} to {anc_value} in {ancestor.__name__}")
                    set_any = False
                    latest = anc_value
                    previous = owner
                    owner = ancestor
                    unique_name = create_unique_name(ancestor, name)
                    if owner in classes_to_ignore:
                        pass
                    elif member_type == "method":
                        codelines, num = inspect.getsourcelines(anc_value)
                        args = arg_names(anc_value)
                        lines.append("")
                        lines.append(f"    def {unique_name}({', '.join(args)}):")
                        for line in codelines[1:]:
                            line = line.rstrip()
                            m = PY2_SUPER_PATTERN.search(line)
                            if m:
                                super_cls_arg = m.group(2)
                                assert super_cls_arg == ancestor.__name__

                                lines.append("        # begin super() call")

                                # remove the super() function and determine the correct member manually.
                                line = m.group(1) + f"self.__{previous.__name__}__" + m.group(3)
                                lines.append(line)

                                lines.append("        # end super() call")
                            else:
                                lines.append(line)
                        # TODO(matt): get the args
                    elif member_type == "attr":
                        leading_comment, trailing_comment = comments.get(unique_name, (None, None))
                        if leading_comment:
                            for line in leading_comment.split('\n'):
                                lines.append(line)
                        define_line = f"    {unique_name} = {repr(anc_value)}"
                        if trailing_comment:
                            define_line += "  " + trailing_comment
                        lines.append(define_line)
                    elif member_type == "property":
                        codelines, num = inspect.getsourcelines(anc_value.fget)
                        lines.append("")
                        lines.append("    @property")
                        lines.append(f"    def {unique_name}(self):")  # TODO(matt): support args
                        # drop the property line and the method siguration, since we already printed those.
                        # TODO(matt); this is brittle. Stacked properties will probs break it.
                        for line in codelines[2:]:
                            line = line.rstrip()
                            m = PY2_SUPER_PATTERN.search(line)
                            if m:
                                super_cls_arg = m.group(2)
                                assert super_cls_arg == ancestor.__name__

                                # TODO(matt): don't assume indention
                                lines.append("        # Super call")

                                # remove the super() function and determine the correct member manually.
                                line = m.group(1) + f"self.__{previous.__name__}__" + m.group(3)
                                lines.append(line)

                                # Add a blank line
                                lines.append("")
                            else:
                                lines.append(line)
                        continue
                    else:
                        raise TypeError(member_type)

            # then assign the non-unique name to the latest value.
            if latest is not None:
                if owner in classes_to_ignore:
                    continue
                elif member_type == "attr":
                    lines.append(f"    {name} = __{owner.__name__}__{name}")
                elif member_type == "property":
                    lines.append("")
                    lines.append("    @property")
                    lines.append(f"    def {name}(self):")
                    lines.append(f"        return self.{create_unique_name(owner, name)}")
                elif member_type == "method":
                    args = arg_names(latest)
                    no_self_args = args[1:]
                    lines.append("")
                    lines.append(f"    def {name}({', '.join(args)}):")
                    lines.append(
                        f"        return self.{create_unique_name(owner, name)}({', '.join(no_self_args)})"
                    )
                else:
                    raise TypeError(member_type)
    return "\n".join(lines)
