"""Reader and writer of Cantata++ test results.

Currently, this package is mainly oriented towards structural coverage
results.
"""

import math
import re



class StackableObject(object):
    """When tested for structural coverage, a source entity (could be a whole
    file, some functions, a single function or even some executable
    instructions) is seldom fully covered with a single test. So developers
    often need to gather different test results to achieve their goal, e.g.
    have a structural coverage rate of their code at 100%.

    PyCant helps developers in cumulating test results. For that, it defines
    a very useful interface, StackableObject. When compliant, two instances
    can be cumulated. Compliance is tested through the 'is_stackable'
    method, and the 'stack' method do cumulate one instance with the other.

    All test results are StackableObject, being it source file, function and
    even executable instructions.
    """

    def is_stackable(self, other):
        """SO.is_stackable() -> boolean

        True iff both instances are compatible with each other for
        accumulation.
        """
        raise NotImplementedError


    def stack(self, other):
        """SO.stack() -> None

        Acumulate in-place both instances without verifying their
        compatibility.
        """
        raise NotImplementedError



class AccessCounter(StackableObject):
    """Access counter. Can integrate a notion of saturation.

    If limit is negative, which is the default behaviour, the access
    counter does not saturate. Otherwise, it cannot go further than the
    limit value.

    Stacking AccessCounter may lower the saturation limit, never raise it.
    This way, AccessCounter can never go insaturated after being saturated.
    """

    __slots__ = [
        'count',
        'limit',
        ]


    def __init__(self, limit = -1):
        super(AccessCounter, self).__init__()

        self.count = 0
        self.limit = limit


    def __str__(self):
        if self.count == 0:
            return ">> NOT EXECUTED "
        elif self.limit < 0 \
                or self.count < self.limit:
            return "%16s" % self.count
        else:
            return ">=%s" % self.count


    def is_stackable(self, other):
        """AccessCounters are always stackable
        """
        return True


    def stack(self, other):
        # Restrict the upper limit if necessary
        if self.limit < 0 ^ other.limit < 0:
            self.limit = max(self.limit, other.limit)
        else:
            self.limit = min(self.limit, other.limit)

        # Determine what the count should be with the new upper limit
        cumulated_count = self.count + other.count
        if self.limit < 0:
            self.count = cumulated_count
        else:
            self.count = min(cumulated_count, self.limit)



class Instruction(StackableObject):
    """Executable code instruction.
    """

    __slots__ = [
        'access',
        'index',
        'kind',
        'parents',
        ]


    def __init__(self):
        super(Instruction, self).__init__()

        # Distance to the start of the Function (in line of code)
        self.index = None

        # Kind, as determined by Cantata++: cond, other, return, etc.
        self.kind = None

        # Execution counter
        self.access = None

        # Record of all .ctr files that have participated in current state
        self.parents = list()


    def is_stackable(self, other):
        """Two instructions are stackable when they are of the same kind and
        they are at the same distance from the beginning of the function
        they belong to.
        """
        return self.index == other.index \
            and self.kind == other.kind


    def stack(self, other):
        self.access.stack(other.access)
        if other.access.count > 0:
            self.parents.extend(other.parents)



class Function(StackableObject):
    """C-language function representation.
    """

    __slots__ = [
        'file',
        'name',
        'index',
        'instructions',
        'parameters',
        'parents',
        ]


    def __init__(self,
                 filename = None,
                 name = None,
                 parameters = None,
                 index = None):
        super(Function, self).__init__()

        # Record of all .ctr files that have participated in current state
        self.parents = list()

        # Strings identifying the Function: source filename, function name
        # and parameters list
        self.file = filename
        self.name = name
        self.parameters = parameters

        # Line index of the function in the source code, as defined by its
        # first parent.
        self.index = index

        # Ordered set of Instructions
        self.instructions = list()


    def __str__(self):
        result = ""
        nb_executed = 0
        nb_total = 0

        # Header
        header = "%s(%d):%s(%s)" % (self.file,
                                    self.index,
                                    self.name,
                                    self.parameters)
        i = 0
        while i + 79 <= len(header):
            j = header.rfind(" ", i, i + 80)
            if j == -1:
                result += header[i:i+79] + "\n"
                i += 79
            else:
                result += header[i:j] + "\n"
                if j == i + 79:
                    i = j
                else:
                    i = j + 1
        if i < len(header):
            result += header[i:] + "\n"

        result += "statement coverage details" \
            + " (with executed and un-executed cases)\n\n"

        # Instructions
        for index, instruction in enumerate(self.instructions):
            # Ending of the source filename, followed by the line number of the
            # instruction shall be 22 characters maximum
            file_line = "%s(%s):" % (self.file,
                                     self.index + instruction.index)
            file_line = file_line[-22:]
            file_line += " " * (22 - len(file_line))
            result += "%s      stmnt%4d " % (file_line,
                                             index + 1)
            if instruction.kind is None:
                result += " " * 13
            else:
                result += "(%s)%s" % (instruction.kind,
                                      " " * (11 - len(instruction.kind)))

            result += "%26s\n" % (str(instruction.access))

            # Gathering some information for the global status
            nb_total += 1
            if instruction.access.count > 0:
                nb_executed += 1

        # Global status
        result += "\n"
        suffix = '"' + self.name[-30:] + '"'
        suffix += " " * (32 - len(suffix))
        result += "%s%33s%12d\n" % (suffix,
                                    "executed",
                                    nb_executed)
        result += "%s%33s%12d\n" % (suffix,
                                    "un-executed",
                                    nb_total - nb_executed)

        if nb_executed < nb_total:
            rate = (1000 * nb_executed / nb_total) / 10.0
        else:
            rate = 100.0

        result += "%s%33s%11.1f%%\n" % (suffix,
                                        "statement coverage",
                                        rate)

        return result


    def is_stackable(self, other):
        """Two Functions are considered stackable if they share the same
        identifiers (name, etc.) and have the same structure. This means
        they shall have the same number of instructions, and they shall
        be stackable by pair.

        Please note that they don't have to share the same start index.
        """
        if self.file != other.file \
                or self.name != other.name \
                or self.parameters != other.parameters:
            return False

        if len(self.instructions) != len(other.instructions):
            return False

        for i in range(len(self.instructions)):
            if not self.instructions[i].is_stackable(other.instructions[i]):
                return False

        return True


    def stack(self, other):
        self.parents.extend(other.parents)
        for i in range(len(self.instructions)):
            self.instructions[i].stack(other.instructions[i])


    def coverage(self):
        """Executed Instructions ratio
        """
        result = 1.0

        nb_total = len(self.instructions)
        nb_executed = 0
        for instruction in self.instructions:
            if instruction.access.count > 0:
                nb_executed += 1

        if nb_executed < nb_total:
            result = float(nb_executed) / nb_total

        return result


    def nb_ok(self):
        """Count of executed Instructions (at least one access)
        """
        return len([i for i in self.instructions if i.access.count > 0])


    def nb_instructions(self):
        """Total number of Instructions
        """
        return len(self.instructions)


    def set_parent(self, parent):
        """Initialize 'parents' field for both Function and its embedded
        Instructions
        """
        self.parents[:] = [parent]

        for instruction in self.instructions:
            instruction.parents[:] = list()
            if instruction.access.count > 0:
                instruction.parents.append(parent)



class TestResult(StackableObject):
    """Retained content of a Cantata++ test result file - '.ctr' suffix.

    Currently it is limited to test cases'names and functions structural
    coverage results.

    TestResult contains only one Function instance by (file, name)
    """

    __slots__ = [
        '_functions',
        'test_cases',
        ]


    def __init__(self):
        super(TestResult, self).__init__()

        # Indexed set of Functions. Two Functions with the same index are
        # likely to be stacked
        self._functions = dict()

        # Name of the test cases
        self.test_cases = set()


    def __iter__(self):
        """Iterator over the Functions hosted by current TestResult.
        """
        for function in self._functions.values():
            yield function


    def __len__(self):
        """Number of functions hosted by current TestResult.
        """
        return len(self._functions)


    def _key(self, function):
        """Hash function on Function to index them.
        """
        return function.file + "|" + function.name


    def is_stackable_function(self, function):
        """True iff the function can integrate the current TestResult. This
        either means that there is currently no other Function instance to
        conflict with in the TestResult, or that there is one on which the
        function can be stacked.
        """
        key = self._key(function)
        if key not in self._functions:
            return True
        else:
            return self._functions[key].is_stackable(function)


    def stack_function(self, function):
        """Integrate proposed function to the current TestResult. Compatibility
        is not checked.
        """
        key = self._key(function)
        if key in self._functions:
            self._functions[key].stack(function)
        else:
            self._functions[key] = function


    def is_stackable(self, other):
        """True iff all Functions from the other TestResult can be stacked on
        the current one.
        """
        for function in other:
            if not self.is_stackable_function(function):
                return False
        return True


    def stack(self, other):
        for function in other:
            key = self._key(function)
            if key in self._functions:
                self._functions[key].stack(function)
            else:
                self._functions[key] = function


    def stack_and_filter(self, other):
        """TR.stack_and_filter(other) -> TR

        Stack Functions from other TestResult if they can. All the remaining
        ones are returned.
        """
        result = TestResult()

        for function in other:
            key = self._key(function)
            if key in self._functions:
                reference = self._functions[key]
                if reference.is_stackable(function):
                    reference.stack(function)
                else:
                    result.stack_function(function)
            else:
                self._functions[key] = function

        return result


    def filenames(self):
        """P.filenames() -> iterator over the source files of P.
        """
        visited = set()
        for function in self._functions.values():
            if function.file not in visited:
                visited.add(function.file)
                yield function.file


    def split_by_filename(self):
        """P.split_by_filename() -> iterator over the TestResult.

        Functions which belongs to the same source file are grouped
        altogether.
        """
        # Distribute functions among TestResults. Each TestResult gathers only
        # Function that belongs to the same source file
        partition = dict()
        for function in self._functions.values():
            if function.file not in partition:
                partition[function.file] = TestResult()
            partition[function.file].stack_function(function)

        # Iteration
        for part in partition.values():
            yield part


    def has(self, mask):
        """P.has(...) -> Boolean
        True iff current TestResult hosts at least one Function that matches a
        given mask.
        See find() for further precisions on mask.
        """
        return len(list(self.find(mask))) > 0


    def find(self, mask):
        """P.find(...) -> an iterator over the Functions of P that matches
        a given mask.

        The mask allows filtering thanks to four of the Function data members:
         - Function.file
         - Function.name
         - Function.parameters
         - Function.index
        Filtering is active only when field is set (i.e. not None).

        Following example shows how to select from "project" Functions named
        "get_tata" wherever they are defined in "toto.c", whatever their
        parameters:

          mask = Function(filename = "toto.c", function = "get_tata")
          for function in project.find(mask):
             ...
        """
        # First, we determine all Functions in the TestResult that match the
        # mask by recursively filtering among the four members taken into
        # account.
        candidates = list()

        # Try to quicken the search by using the "_key" hash
        if mask.file is not None \
                and mask.name is not None:
            key = self._key(mask)
            if key in self._functions:
                candidates.append(self._functions[key])
            else:
                raise StopIteration
        else:
            # by default, all functions are candidate
            candidates.extend(self._functions.values())

            for member in "file", "name":
                stem = getattr(mask, member)
                if stem is not None:
                    candidates = filter(lambda f: getattr(f, member) == stem,
                                        candidates)

        # Filter with parameters'list and function index
        for member in "parameters", "index":
            stem = getattr(mask, member)
            if stem is not None:
                candidates = filter(lambda f: getattr(f, member) == stem,
                                    candidates)

        # Iteration by itself
        for candidate in candidates:
            yield candidate


    def remove(self, function):
        """Remove the Function from the TestResult.

        KeyError is raised if Function is not member of the TestResult.
        """
        key = self._key(function)
        candidate = self._functions[key]
        if candidate is function:
            self._functions.pop(key)
        else:
            raise KeyError


    def discard(self, function):
        """Remove the Function from the TestResult.

        If the Function is not member of the TestResult, do nothing.
        """
        try:
            self.remove(function)
        except KeyError:
            pass



class Reader(object):
    """Utility class to load content of a '.ctr' file provide a binary
    representation of it as a TestResult.
    """

    def __init__(self):
        self._load_result = None

        self._lines = list()
        self._contexts = list()

        self._lineset_cache = None
        self._lineset_start = 0
        self._lineset_last = 0

        # Pre-compiled regular expressions for efficency
        self.re_count = re.compile("(>=)?(\d+)\Z")
        self.re_header = re.compile("(\w+\.\w+)\((\d+)\):(\w+)\(([^)]*)\)")
        self.re_instr = re.compile("\((\d+)\)")
        self.re_paren_num = re.compile("\(\d+\):")
        self.re_typed_instr = re.compile("\((\d+)\).*(\(([a-z-]+)\))")


    def load(self, filename):
        """I.load(...) -> TestResult

        Analyses '.ctr' file to build up a TestResult instance.
        If file access is difficult, IOError may be raised.
        """
        self._load_result = TestResult()

        # Complete load of the text file before further analysis
        stream = open(filename, "r")
        for line in stream:
            self._lines.append(line.rstrip())
        self._push_context(0, len(self._lines) - 1)

        # Textual analysis
        state = 0
        for index, line in enumerate(self._lines):
            if state == 0:
                # Test cases'names are collected
                if line.find("Start Test:") != -1 \
                        and line.find("Coverage Analysis") == -1:
                    test_case = line.split()[3]
                    self._load_result.test_cases.add(test_case)

                # Identifying structural coverage results is much more
                # complicated, and requires a finite state automaton
                if self.re_paren_num.search(self._lineset(index)):
                    state = 1
                    i_0 = index
            elif state == 1:
                if line.startswith("entry point coverage "):
                    state = 2
                elif line.find(": statement coverage") != -1:
                    state = 3
                elif line.find(" statement coverage") != -1:
                    self._push_context(i_0, index)
                    function = self._load_function()
                    function.set_parent(filename)
                    self._load_result.stack_function(function)
                    self._pop_context()
                    state = 0
            elif state == 2:
                if line.find(" entry point coverage") != -1:
                    state = 0
            elif state == 3:
                if line.startswith("-----"):
                    state = 0

        return self._load_result


    def _load_function(self):
        """Current context text is analysed to produce a Function.
        """
        result = Function()

        #######
        # HEADER
        #######

        # Isolation
        header = ""
        i = self._line_min()
        while self._lines[i + 1] != "":
            header += self._lines[i]
            if len(self._lines[i]) < 79:
                header += " "
            i += 1

        # Analysis
        match = self.re_header.match(header)
        result.file = match.group(1)
        result.index = int(match.group(2))
        result.name = match.group(3)
        result.parameters = match.group(4)

        #########
        # MEASURES
        #########

        # Structural coverage result
        i += 2
        while self._lines[i] != "":
            self._push_context(i, i)
            instruction = self._load_instruction()
            instruction.index -= result.index
            result.instructions.append(instruction)
            self._pop_context()
            i += 1

        return result


    def _load_instruction(self):
        """Current context text is analysed to produce an Instruction
        """
        result = Instruction()

        line = self._lines[self._line_min()]
        match = self.re_typed_instr.search(line)
        if match:
            result.index = int(match.group(1))
            result.kind = match.group(3)
        else:
            match = self.re_instr.search(line)
            result.index = int(match.group(1))

        result.access = AccessCounter()
        if not line.endswith(">> NOT EXECUTED"):
            match = self.re_count.search(line)
            if match.group(1) is not None:
                result.access.limit = int(match.group(2))
            result.access.count = int(match.group(2))

        return result


    def _push_context(self, line_min, line_max):
        """Reduce text analysis scope to the proposed interval.
        """
        self._contexts.append((line_min, line_max))


    def _pop_context(self):
        """Go back to the previous text analysis scope.
        """
        self._contexts.pop()


    def _line_min(self):
        """First line index of the current analysis context
        """
        return self._contexts[-1][0]


    def _line_max(self):
        """Last line index of the current analysis context
        """
        return self._contexts[-1][1]


    def _lineset(self, index):
        """A lineset is the maximal set of adjacent lines that contains the one
        at the corresponding index, without including any so-called "separator
        line"

        If index designates a separator line, results is empty.
        """
        if index < self._lineset_start \
                or index >= self._lineset_last:
            self._lineset_cache = ""
            if not self._is_separator(index):
                self._lineset_start = index
                while self._lineset_start > self._line_min() \
                        and not self._is_separator(self._lineset_start - 1):
                    self._lineset_start -= 1
                self._lineset_last = index
                while self._lineset_last <= self._line_max() \
                        and not self._is_separator(self._lineset_last):
                    self._lineset_last += 1

                for i in range(self._lineset_start, self._lineset_last):
                    self._lineset_cache += self._lines[i]

        return self._lineset_cache


    def _is_separator(self, index):
        """True iff line at proposed index is a "separator line".
        Separator line can either be a blank line or a line that contains
        only hyphens.
        """
        return len(self._lines[index].replace("-", "")) == 0



class Writer(object):
    """Utility class to dump a TestResult according to the '.ctr' file format.
    """

    def dump(self, stream, test_result):
        """Write in the stream the structural coverage results and complete it
        with the global status of the whole set of Functions.
        """
        stats = list()

        for function in sorted(list(test_result.__iter__()),
                               key = lambda f: f.name):
            stream.write(str(function))
            stream.write("\n")

            stats.append((function.coverage(), len(function.instructions)))

        # Global status of the whole set of functions
        status = \
            """Summary by     EXECUTED     Overall                Statistics
Coverage type  INFEASIBLES  (wavg)     avg /    min /    max /    dev /   num
-----------------------------------------------------------------------------
statement              0   %5.1f%%   %5.1f%% / %5.1f%% / %5.1f%% / %5.1f%% / %5d
-----------------------------------------------------------------------------
"""
        minimum = 1.0
        maximum = 0.0
        mean = 0.0
        weighted_mean = 0.0
        nb_instruction = 0
        for ratio, length in stats:
            mean += ratio
            weighted_mean += ratio * length
            nb_instruction += length
            if ratio < minimum:
                minimum = ratio
            if ratio > maximum:
                maximum = ratio
        if nb_instruction > 0:
            weighted_mean /= nb_instruction

        deviation = 0.0
        nb_function = len(stats)
        if nb_function > 1:
            mean /= nb_function
            for ratio, length in stats:
                deviation += (ratio - mean)**2
            deviation = math.sqrt(deviation / float(nb_function - 1))

        stream.write(status % (int(1000.0 * weighted_mean) / 10.0,
                            int(1000.0 * mean) / 10.0,
                            int(1000.0 * minimum) / 10.0,
                            int(1000.0 * maximum) / 10.0,
                            int(1000.0 * deviation) / 10.0,
                            nb_function))
