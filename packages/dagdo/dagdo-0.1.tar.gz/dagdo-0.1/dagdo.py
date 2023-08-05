#! /usr/bin/env python
"""
Parse a dagdo yaml file
"""

import os
import sys
import argparse
import datetime
import yaml


DESCRIPTION = """
Parse a dagdo yaml file and show the ready tasks in sorted order by their
constraint deadlines.  See --usage for a complete description of usage.
"""

VERBOSE_USAGE = """\
The dagdo tool shows the immediate steps on a critical path for a complex
set of interdependent tasks.

The dagdo yaml file is in the YAML format and consists of a sequence of
"task" mappings.  By default it lives in ~/.dagdo.yaml, but you can use
different files with the --file option.  Here's a quick example of the
file format:

- title: Buy groceries
  due: 2012-11-10

- title: Dentist appointment
  due: 2012-11-15

Tasks may depend on each other.  If task A depends on task B, then B is
called A's dependency and A is called B's dependent.  Here's an example
dagdo.yaml file with a dependency:

- @BG
  title: Buy groceries

- title: Cook dinner for guests
  due: 2012-12-12
  deps: [ *BG ]

In this example, the task of cooking dinner depends on buying groceries.

Tasks may have any number of dependencies or dependents but they're may
not be cycles (for example, A can't depend on B which also depends on A).
The relationship of tasks is technically called a Directed Acyclic Graph
or DAG for short, thus the name.

A task which has no dependencies is called ready.  A task which has
no dependents is called final.

Every final task must have a due date.  Any non-final task may optionally
have a due date.

Every task has a constraint deadline.  The constraint deadline for a final
task is its due date.  The constraint deadline for a non-final task is
the earliest constraint deadline of all of its dependents, or if it has
its own due date which is earlier than that, then that earlier due date
is the constraint deadline.

In the last example, the constraint deadline for buying groceries is
2012-12-12, because that is the earliest constraint deadline is from
the cooking task.

These relationships mean that if many tasks depend on a task T, then
the constraint deadline of T is the latest time T must be completed in
order to meet all the deadlines of all dependent tasks.  This is a
time-aware, critical path prioritization of tasks.

The output of the dagdo tool shows the ready tasks in a sorted order
with the earliest constraint deadline first.

Beware: If you run the script and see task A then task B, then you
complete task A and remove it from the file and rerun the script, you
may now see task C followed by task B.  Therefore, don't assume a single
output is a linear todo list.

The dagdo tool only reads the input file and never modifies it.  Also,
the input file only represents unfinished tasks without any history
of changes.  The author highly recommends tracking all dagdo.yaml
files with a revision control tool, which will keep a history of all of
your tasks.

Each task must have a "title" field.  A "due" field may be required
as described above.  The "deps" field contains dependency references
which should almost always use the yaml * syntax.  An optional "desc"
field stores longer details for a task, and the yaml | syntax is useful:

- title: buy airline tickets
  due: 2012-11-01
  desc: |
   mom's flight: acme airlines 42
   remember to use megacorp airline rewards points.
"""


def main(args = sys.argv[1:]):
    opts = parse_args(args)
    with file(opts.path) as f:
        tasks = load_dag(f)

    if has_failed():
        raise SystemExit('Exiting due to errors.')
    else:
        for task in sorted(tasks):
            print task


def parse_args(args):
    p = argparse.ArgumentParser(description=DESCRIPTION)
    p.add_argument('--file', '-f',
                   dest='path',
                   default=os.path.expanduser('~/.dagdo.yaml'),
                   help='The path to a dagdo file.')
    p.add_argument('--usage',
                   action='store_true',
                   dest='show_usage',
                   default=False,
                   help='Show detailed usage instructions.')

    opts = p.parse_args(args)

    if opts.show_usage:
        print VERBOSE_USAGE
        raise SystemExit(0)

    return opts


def load_dag(f):
    doc2dag = {} # Maps { id(docobj) -> Task }
    tasks = set() # Set of depended-upon-leaf-nodes

    for i, entry in enumerate(yaml.load(f)):
        (title, due, docdeps, desc) = parse_entry_fields(i, entry)
        nodedeps = set()
        for d in docdeps:
            try:
                nodedep = doc2dag[id(d)]
            except KeyError:
                fail(
                    ('Task entry %d %r refers to a task later in the file. ' +
                     'Dependencies must come first to prevent cycles.'),
                    i,
                    title)
                continue
            else:
                nodedeps.add(nodedep)

        if isinstance(due, str):
            due = parse_datetime(due)

        if not (due is None or isinstance(due, datetime.date)):
            fail('In task entry %d %r, could not parse "due" field as date: %r', i, title, due)

        node = Task(title, due, nodedeps, desc)
        doc2dag[id(entry)] = node

        if not node.has_dependencies():
            tasks.add(node)

    for task in tasks:
        task.check_deadlines()

    return tasks


def parse_entry_fields(i, entry):
    entry = entry.copy()
    title = entry.pop('title')
    due = entry.pop('due', None)
    deps = entry.pop('deps', [])
    desc = entry.pop('desc', None)
    if entry:
        fail('Unexpected keys in entry %d %r: %r', i, title, entry.keys())
    return (title, due, deps, desc)


def fail(tmpl, *args):
    fail.failed = True
    sys.stderr.write('Error: %s\n' % (tmpl % args,))

fail.failed = False

def has_failed():
    return fail.failed


class Task (object):
    def __init__(self, title, due, deps, desc):
        self.title = title
        self.due = due
        self.deps = deps
        self.rdeps = set()
        self.desc = desc

        for dep in deps:
            dep.rdeps.add(self)

    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__, self)

    def __str__(self):
        (due, rdep) = self.get_deadline_constraint()
        if due is None:
            # This should only ever be displayed when there are input file errors:
            return 'MISSING DEADLINE: %s' % (self.title,)
        else:
            because = '' if (rdep is self) else ' (because of %s)' % (rdep.title,)
            return '%s: %s%s' % (due, self.title, because)

    def __cmp__(self, other):
        assert isinstance(other, Task), `other`
        (mydue, _) = self.get_deadline_constraint()
        (theirdue, _) = other.get_deadline_constraint()
        return cmp_datetimes(mydue, theirdue)

    def has_dependencies(self):
        return len(self.deps) > 0

    def check_deadlines(self):
        if self.rdeps:
            for rdep in self.rdeps:
                rdep.check_deadlines()
        else:
            if self.due is None:
                fail('%r has no deadline.', self)

    def get_deadline_constraint(self):
        (due, because) = (self.due, self)
        for rdep in self.rdeps:
            (d, b) = rdep.get_deadline_constraint()
            assert d is not None, 'invariant failure; get_deadline_constraint & check_deadlines do not agree.'
            if due is None or d < due:
                (due, because) = (d, b)
        return (due, because)


ACCEPTED_DATE_TIME_FORMATS = [
    '%Y-%m-%d %H:%M',
    ]

def parse_datetime(s):
    # python yaml is picky about parsing date times.  For example,
    # in an iso8601 format missing the seconds will be returned as a string.
    # see: http://pyyaml.org/ticket/208

    for timefmt in ACCEPTED_DATE_TIME_FORMATS:
        try:
            return datetime.datetime.strptime(s, timefmt)
        except:
            continue
    fail('Could not parse date/time: %r', s)
    return None


def cmp_datetimes(a, b):
    # Ugh... even though: isinstance(datetime.datetime(0,0,0,0,0,0), datetime.date) they cannot be compared.

    def coerce(dt):
        if not isinstance(dt, datetime.datetime):
            dt = datetime.datetime(dt.year, dt.month, dt.day, 0, 0, 0)
        return dt

    return cmp(coerce(a), coerce(b))


if __name__ == '__main__':
    main()
