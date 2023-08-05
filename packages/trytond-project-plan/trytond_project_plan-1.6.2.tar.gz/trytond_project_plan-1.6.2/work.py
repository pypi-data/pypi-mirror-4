#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.

from trytond.model import ModelView, ModelSQL, fields
from trytond.wizard import Wizard
from trytond.pyson import Eval, Not, Equal
from collections import deque, defaultdict
from heapq import heappop, heappush
import datetime

def intfloor(x):
    return int(round(x, 4))


class Work(ModelSQL, ModelView):
    _name = 'project.work'

    predecessors = fields.Many2Many('project.predecessor_successor',
            'successor', 'predecessor', 'Predecessors',
            domain=[
                ('parent', '=', Eval('parent')),
                ('id', '!=', Eval('active_id')),
            ])
    successors = fields.Many2Many('project.predecessor_successor',
            'predecessor', 'successor', 'Successors',
            domain=[
                ('parent', '=', Eval('parent')),
                ('id', '!=', Eval('active_id')),
            ])
    leveling_delay = fields.Float("Leveling Delay")
    back_leveling_delay = fields.Float("Leveling Delay")
    allocations = fields.One2Many('project.allocation', 'work', 'Allocations',
            states={
                'invisible': Not(Equal(Eval('type'), 'task')),
            }, depends=['type'])
    duration = fields.Function(fields.Float('Duration'), 'get_function_fields')
    early_start_time = fields.DateTime("Early Start Time", readonly=True)
    late_start_time = fields.DateTime("Late Start Time", readonly=True)
    early_finish_time = fields.DateTime("Early Finish Time", readonly=True)
    late_finish_time = fields.DateTime("Late Finish Time", readonly=True)
    actual_start_time = fields.DateTime("Actual Start Time")
    actual_finish_time = fields.DateTime("Actual Finish Time")
    constraint_start_time = fields.DateTime("Constraint Start Time")
    constraint_finish_time = fields.DateTime("Constraint  Finish Time")
    early_start_date = fields.Function(fields.Date('Early Start'),
            'get_function_fields')
    late_start_date = fields.Function(fields.Date('Late Start'),
            'get_function_fields')
    early_finish_date = fields.Function(fields.Date('Early Finish'),
            'get_function_fields')
    late_finish_date = fields.Function(fields.Date('Late Finish'),
            'get_function_fields')
    actual_start_date = fields.Function(fields.Date('Actual Start'),
            'get_function_fields', setter='set_function_fields')
    actual_finish_date = fields.Function(fields.Date('Actual Finish'),
            'get_function_fields', setter='set_function_fields')
    constraint_start_date = fields.Function(fields.Date('Constraint Start',
        depends=['type']), 'get_function_fields',
        setter='set_function_fields')
    constraint_finish_date = fields.Function(fields.Date('Constraint Finish',
        depends=['type']), 'get_function_fields',
        setter='set_function_fields')
    requests = fields.Function(fields.One2Many('res.request', None,
        'Requests'), 'get_function_fields', setter='set_function_fields')

    def __init__(self):
        super(Work, self).__init__()
        self._constraints += [
            ('check_recursion', 'recursive_dependency'),
            ]
        self._error_messages.update({
                'recursive_dependency': 'You can not create recursive '
                        'dependencies!',
                })

    def check_recursion(self,cursor,  user, ids, parent='parent'):
        return super(Work, self).check_recursion(cursor, user, ids,
                parent='successors')

    def get_function_fields(self, cursor, user, ids, names, context=None):
        '''
        Function to compute function fields

        :param cursor: the database cursor
        :param user: the user id
        :param ids: the ids of the works
        :param names: the list of field name to compute
        :param args: optional argument
        :param context: the context
        :return: a dictionary with all field names as key and
            a dictionary as value with id as key
        '''
        req_ref_obj = self.pool.get('res.request.reference')

        res = {}

        if 'requests' in names:
            requests = dict((i, []) for i in ids)

            for i in range(0, len(ids), cursor.IN_MAX):
                sub_ids = ids[i:i + cursor.IN_MAX]

                req_ref_ids = req_ref_obj.search(cursor, user, [
                        ('reference', 'in', [
                                'project.work,%s' % i for i in sub_ids
                                ]
                         ),
                        ], context=context)
                req_refs = req_ref_obj.browse(cursor, user, req_ref_ids,
                        context=context)
                for req_ref in req_refs:
                    _, work_id = req_ref.reference.split(',')
                    requests[int(work_id)].append(req_ref.request.id)

            res['requests'] = requests

        if 'duration' in names:
            all_ids = self.search(cursor, user, [
                    ('parent', 'child_of', ids),
                    ('active', '=', True)], context=context) + ids
            all_ids = list(set(all_ids))

            works = self.browse(cursor, user, all_ids, context=context)
            all_works = set(works)

            durations = {}
            id2work = {}
            leafs = set()
            for work in works:
                id2work[work.id] = work
                if not work.children:
                    leafs.add(work.id)

                total_allocation = 0
                if not work.allocations:
                    durations[work.id] = work.effort
                    continue
                for allocation in work.allocations:
                    total_allocation += allocation.percentage
                durations[work.id] = work.effort / (total_allocation / 100.0)

            while leafs:
                for work_id in leafs:
                    work = id2work[work_id]
                    all_works.remove(work)
                    if not work.active:
                        continue
                    if work.parent and work.parent.id in durations:
                        durations[work.parent.id] += durations[work_id]
                next_leafs = set(w.id for w in all_works)
                for work in all_works:
                    if not work.parent:
                        continue
                    if work.parent.id in next_leafs and work.parent in works:
                        next_leafs.remove(work.parent.id)
                leafs = next_leafs
            res['duration'] = durations


        fun_fields = ('early_start_date', 'early_finish_date',
                      'late_start_date', 'late_finish_date',
                      'actual_start_date', 'actual_finish_date',
                      'constraint_start_date', 'constraint_finish_date')
        db_fields = ('early_start_time', 'early_finish_time',
                  'late_start_time', 'late_finish_time',
                  'actual_start_time', 'actual_finish_time',
                  'constraint_start_time', 'constraint_finish_time')

        works = None
        for fun_field, db_field in zip(fun_fields, db_fields):
            if fun_field in names:
                values = {}
                if works is None:
                    works = self.browse(cursor, user, ids, context=context)
                for work in works:
                    values[work.id] = work[db_field] \
                        and work[db_field].date() or None
                res[fun_field] = values

        return res

    def set_function_fields(self, cursor, user, ids, name, value,
            context=None):
        request_obj = self.pool.get('res.request')
        req_ref_obj = self.pool.get('res.request.reference')

        if name == 'requests':
            works = self.browse(cursor, user, ids, context=context)
            currents = dict((req.id, req) for work in works for req in
                    work.requests)
            if not value:
                return
            for v in value:
                to_unlink = []
                to_link = []
                operator = v[0]

                target_ids = len(v) > 1 and v[1] or []
                if operator == 'set':
                    to_link.extend((i for i in target_ids
                        if i not in currents))
                    to_unlink.extend((i for i in currents
                        if i not in target_ids))
                elif operator == 'add':
                    to_link.extend((i for i in target_ids if i not in
                        currents))
                elif operator == 'unlink':
                    to_unlink.extend((i for i in target_ids if i in currents))
                elif operator == 'unlink_all':
                    to_unlink.extend(currents)
                elif operator == 'delete':
                    request_obj.delete(cursor, user, to_delete,
                            context=context)
                else:
                    raise Exception('Operation not supported')

                req_ref_ids = []
                for i in to_unlink:
                    request = currents[i]
                    for ref in request.references:
                        if int(ref.reference.split(',')[1]) in ids:
                            req_ref_ids.append(ref.id)
                req_ref_obj.delete(cursor, user, req_ref_ids,
                        context=context)

                for i in to_link:
                    for record_id in ids:
                        req_ref_obj.create(cursor, user, {
                                'request': i,
                                'reference': 'project.work,%s' % record_id,
                                }, context=context)
            return

        fun_fields = ('actual_start_date', 'actual_finish_date',
                      'constraint_start_date', 'constraint_finish_date')
        db_fields = ('actual_start_time', 'actual_finish_time',
                     'constraint_start_time', 'constraint_finish_time')
        for fun_field, db_field in zip(fun_fields, db_fields):
            if fun_field == name:
                self.write(cursor, user, ids, {
                        db_field: value \
                                and datetime.datetime.combine(value,
                                    datetime.time()) \
                                or False,
                        }, context=context)
                break

    def add_minutes(self, cursor, user, company, date, minutes, context=None):
        minutes = int(round(minutes))
        minutes = date.minute + minutes

        hours = minutes // 60
        if hours:
            date = self.add_hours(cursor, user, company, date, hours,
                    context=context)

        minutes = minutes % 60

        date = datetime.datetime(
            date.year,
            date.month,
            date.day,
            date.hour,
            minutes,
            date.second)

        return date

    def add_hours(self, cursor, user, company, date, hours, context=None):
        day_per_week = company.hours_per_work_week / company.hours_per_work_day

        while hours:
            if hours !=  intfloor(hours):
                minutes = (hours - intfloor(hours)) * 60
                date = self.add_minutes(cursor, user, company, date, minutes,
                        context=context)
            hours = intfloor(hours)

            hours = date.hour + hours
            days = hours // company.hours_per_work_day
            if days:
                date = self.add_days(cursor, user, company, date, days,
                        context=context)

            hours = hours % company.hours_per_work_day

            date = datetime.datetime(
                date.year,
                date.month,
                date.day,
                intfloor(hours),
                date.minute,
                date.second)

            hours = hours - intfloor(hours)

        return date

    def add_days(self, cursor, user, company, date, days, context=None):
        day_per_week = company.hours_per_work_week / company.hours_per_work_day

        while days:
            if days !=  intfloor(days):
                hours = (days - intfloor(days)) * company.hours_per_work_day
                date = self.add_hours(cursor, user, company, date, hours,
                        context=context)
            days = intfloor(days)

            days = date.weekday() + days

            weeks = days // day_per_week
            days = days % day_per_week

            if weeks:
                date = self.add_weeks(cursor, user, company, date, weeks,
                        context=context)

            date += datetime.timedelta(days= -date.weekday() + intfloor(days))

            days = days - intfloor(days)

        return date

    def add_weeks(self, cursor, user, company, date, weeks, context=None):
        day_per_week = company.hours_per_work_week / company.hours_per_work_day

        if weeks !=  intfloor(weeks):
            days = (weeks - intfloor(weeks)) * day_per_week
            if days:
                date = self.add_days(cursor, user, company, date, days,
                        context=context)

        date += datetime.timedelta(days= 7 * intfloor(weeks))

        return date

    def compute_dates(self, cursor, user, work_id, context=None):
        active_work = self.browse(cursor, user, work_id, context=context)
        values = {}
        get_early_finish = lambda work: values.get(work, {}).get(
            'early_finish_time', work['early_finish_time'])
        get_late_start = lambda work: values.get(work, {}).get(
            'late_start_time', work['late_start_time'])
        maxdate = lambda x,y: x and y and max(x,y) or x or y
        mindate = lambda x,y: x and y and min(x,y) or x or y


        # propagate constraint_start_time
        constraint_start = reduce(maxdate, (pred.early_finish_time \
                for pred in active_work.predecessors), None)

        if constraint_start is None and active_work.parent:
            constraint_start = active_work.parent.early_start_time

        constraint_start = maxdate(constraint_start,
                                   active_work.constraint_start_time)

        works = deque([(active_work, constraint_start)])
        work2children = {}
        parent = None

        while works or parent:
            if parent:
                work = parent
                parent = None

                # Compute early_finish
                if work.children:
                    early_finish_time = reduce(
                        maxdate, map(get_early_finish, work.children), None)
                else:
                    early_finish_time = None
                    if values[work]['early_start_time']:
                        early_finish_time = self.add_hours(cursor, user,
                                work.company, values[work]['early_start_time'],
                                work.duration, context=context)
                values[work]['early_finish_time'] = early_finish_time

                # Propagate constraint_start on successors
                for w in work.successors:
                    works.append((w, early_finish_time))

                if not work.parent:
                    continue

                # housecleaning work2children
                if work.parent not in work2children:
                    work2children[work.parent] = set()
                work2children[work.parent].update(work.successors)

                if work in work2children[work.parent]:
                    work2children[work.parent].remove(work)

                # if no sibling continue to walk up the tree
                if not work2children.get(work.parent):
                    if not work.parent in values:
                        values[work.parent] = {}
                    parent = work.parent

                continue

            work, constraint_start = works.popleft()
            # take constraint define on the work into account
            constraint_start = maxdate(constraint_start,
                                       work.constraint_start_time)

            if constraint_start:
                early_start = self.add_hours(cursor, user,
                        work.company, constraint_start, work.leveling_delay,
                        context=context)
            else:
                early_start = None

            # update values
            if not work in values:
                values[work] = {}
            values[work]['early_start_time'] = early_start

            # Loop on children if they exist
            if work.children and work not in work2children:
                work2children[work] = set(work.children)
                # Propagate constraint_start on children
                for w in work.children:
                    if w.predecessors:
                        continue
                    works.append((w, early_start))
            else:
                parent = work

        # propagate constraint_finish_time
        constraint_finish = reduce(mindate, (succ.late_start_time \
                for succ in active_work.successors), None)

        if constraint_finish is None and active_work.parent:
            constraint_finish = active_work.parent.late_finish_time

        constraint_finish = mindate(constraint_finish,
                                    active_work.constraint_finish_time)

        works = deque([(active_work, constraint_finish)])
        work2children = {}
        parent = None

        while works or parent:
            if parent:
                work = parent
                parent = None

                # Compute late_start
                if work.children:
                    reduce(mindate, map(get_late_start, work.children), None)
                else:
                    late_start_time = None
                    if values[work]['late_finish_time']:
                        late_start_time = self.add_hours(cursor, user,
                                work.company, values[work]['late_finish_time'],
                                -work.duration, context=context)
                values[work]['late_start_time'] = late_start_time

                # Propagate constraint_finish on predecessors
                for w in work.predecessors:
                    works.append((w, late_start_time))

                if not work.parent:
                    continue

                # housecleaning work2children
                if work.parent not in work2children:
                    work2children[work.parent] = set()
                work2children[work.parent].update(work.predecessors)

                if work in work2children[work.parent]:
                    work2children[work.parent].remove(work)

                # if no sibling continue to walk up the tree
                if not work2children.get(work.parent):
                    if not work.parent in values:
                        values[work.parent] = {}
                    parent = work.parent

                continue

            work, constraint_finish = works.popleft()
            # take constraint define on the work into account
            constraint_finish = mindate(constraint_finish,
                                        work.constraint_finish_time)

            if constraint_finish:
                late_finish = self.add_hours(cursor, user, work.company,
                        constraint_finish, -work.back_leveling_delay,
                        context=context)
            else:
                late_finish = None

            # update values
            if not work in values:
                values[work] = {}
            values[work]['late_finish_time'] = late_finish

            # Loop on children if they exist
            if work.children and work not in work2children:
                work2children[work] = set(work.children)
                # Propagate constraint_start on children
                for w in work.children:
                    if w.successors:
                        continue
                    works.append((w, late_finish))
            else:
                parent = work

        # write values
        write_fields = ('early_start_time', 'early_finish_time',
                        'late_start_time', 'late_finish_time')
        for work, val in values.iteritems():
            write_cond = False
            for field in write_fields:
                if field in val and work[field] != val[field]:
                    write_cond = True
                    break

            if write_cond:
                self.write(cursor, user, work.id, val, context=context)

    def reset_leveling(self, cursor, user, work_id, context=None):
        get_key = lambda w: (set(p.id for p in w.predecessors),
                             set(s.id for s in w.successors))

        work = self.browse(cursor, user, work_id, context=context)
        parent_id = work.parent and work.parent.id or False
        sibling_ids = self.search(cursor, user, [
                ('parent', '=', parent_id)
                ], context=context)
        siblings = self.browse(cursor, user, sibling_ids,
                context=context)
        to_clean = []

        ref_key = get_key(work)
        for sibling in siblings:
            if sibling.leveling_delay == sibling.back_leveling_delay == 0:
                continue
            if get_key(sibling) == ref_key:
                to_clean.append(sibling.id)

        if to_clean:
            self.write(cursor, user, to_clean, {
                    'leveling_delay': 0,
                    'back_leveling_delay': 0,
                    }, context=context)

    def create_leveling(self, cursor, user, work_id, context=None):
        # define some helper functions
        get_key = lambda w: (set(p.id for p in w.predecessors),
                             set(s.id for s in w.successors))
        over_alloc = lambda current_alloc, work: \
            reduce(lambda res, alloc: res or current_alloc[alloc.employee.id] + \
                       alloc.percentage > 100,
                   work.allocations,
                   False)
        def sum_allocs(current_alloc, work):
            res = defaultdict(float)
            for alloc in work.allocations:
                empl = alloc.employee.id
                res[empl] = current_alloc[empl] + alloc.percentage
            return res

        def compute_delays(siblings):
            # time_line is a list [[end_delay, allocations], ...], this
            # mean that allocations is valid between the preceding end_delay
            # (or 0 if it doesn't exist) and the current end_delay.
            timeline = []
            for sibling in siblings:
                delay = 0
                ignored = []
                overloaded = []
                item = None

                while timeline:
                    # item is [end_delay, allocations]
                    item = heappop(timeline)
                    if over_alloc(item[1], sibling):
                        ignored.extend(overloaded)
                        ignored.append(item)
                        delay = item[0]
                        continue
                    elif item[1] >= delay + sibling.duration:
                        overloaded.append(item)
                    else:
                        #Succes!
                        break

                heappush(timeline,
                         [delay + sibling.duration,
                          sum_allocs(defaultdict(float), sibling),
                          sibling.id])

                for i in ignored:
                    heappush(timeline, i)
                for i in overloaded:
                    i[1] = sum_allocs(i[1], sibling)
                    heappush(timeline, i)

                yield sibling, delay

        work = self.browse(cursor, user, work_id, context=context)
        parent_id = work.parent and work.parent.id or False
        sibling_ids = self.search(cursor, user, [
                ('parent', '=', parent_id)
                ], context=context)

        refkey = get_key(work)
        siblings = [s for s in self.browse(cursor, user, sibling_ids,
                context=context) if get_key(s) == refkey]

        for sibling, delay in compute_delays(siblings):
            self.write(cursor, user, sibling.id, {
                    'leveling_delay': delay,
                    }, context=context)

        siblings.reverse()
        for sibling, delay in compute_delays(siblings):
            self.write(cursor, user, sibling.id, {
                    'back_leveling_delay': delay,
                    }, context=context)

        if parent_id:
            self.compute_dates(cursor, user, parent_id, context=context)

    def write(self, cursor, user, ids, values, context=None):
        res = super(Work, self).write(cursor, user, ids, values,
                context=context)
        if isinstance(ids, (int, long)):
            ids = [ids]

        if 'effort' in values:
            for work_id in ids:
                self.reset_leveling(cursor, user, work_id,
                                   context=context)
        fields = ('constraint_start_time', 'constraint_finish_time',
                  'effort')
        if reduce(lambda x, y : x or y in values, fields, False):
            for work_id in ids:
                self.compute_dates(cursor, user, work_id,
                                   context=context)
        return res

    def create(self, cursor, user, values, context=None):
        work_id = super(Work, self).create(cursor, user, values,
                context=context)
        self.reset_leveling(cursor, user, work_id, context=context)
        self.compute_dates(cursor, user, work_id, context=context)
        return work_id

    def delete(self, cursor, user, ids, context=None):
        if isinstance(ids, (int, long)):
            ids = [ids]
        works = self.browse(cursor, user, ids, context=context)
        to_update = set()
        for work in works:
            if work.parent and work.parent.id not in ids:
                to_update.add(work.parent.id)
                to_update.update(c.id for c in work.parent.children \
                                     if c.id not in ids)
        res = super(Work, self).delete(cursor, user, ids, context=context)

        for work_id in to_update:
            self.reset_leveling(cursor, user, work_id, context=context)
            self.compute_dates(cursor, user, work_id, context=context)

        return res
Work()



class PredecessorSuccessor(ModelSQL):
    'Predecessor - Successor'
    _name = 'project.predecessor_successor'
    _description = __doc__

    predecessor = fields.Many2One('project.work', 'Predecessor',
            ondelete='CASCADE', required=True, select=1)
    successor = fields.Many2One('project.work', 'Successor',
            ondelete='CASCADE', required=True, select=1)

    def write(self, cursor, user, ids, values, context=None):
        work_obj = self.pool.get('project.work')
        res = super(PredecessorSuccessor, self).write(cursor, user, ids, values,
                context=context)

        for work_id in values.itervalues():
            work_obj.reset_leveling(cursor, user, work_id,
                                context=context)
        for work_id in values.itervalues():
            work_obj.compute_dates(cursor, user, work_id,
                               context=context)
        return res

    def delete(self, cursor, user, ids, context=None):
        work_obj = self.pool.get('project.work')
        if isinstance(ids, (int, long)):
            ids = [ids]

        work_ids = set()
        parent_ids = set()
        pred_succs = self.browse(cursor, user, ids, context=context)
        for pred_succ in pred_succs:
            work_ids.update((pred_succ.predecessor.id,
                             pred_succ.successor.id))

            if pred_succ.predecessor.parent:
                parent_ids.add(pred_succ.predecessor.parent.id)

        res = super(PredecessorSuccessor, self).delete(cursor, user, ids,
                context=context)

        for work_id in work_ids:
            work_obj.reset_leveling(cursor, user, work_id, context=context)

        for parent_id in parent_ids:
            work_obj.compute_dates(cursor, user, parent_id, context=context)

        return res

    def create(self, cursor, user, values, context=None):
        work_obj = self.pool.get('project.work')
        ps_id = super(PredecessorSuccessor, self).create(cursor, user, values,
                context=context)

        pred_succ = self.browse(cursor, user, ps_id, context=context)
        work_obj.reset_leveling(cursor, user, pred_succ.predecessor.id,
                context=context)
        work_obj.reset_leveling(cursor, user, pred_succ.successor.id,
                context=context)

        if pred_succ.predecessor.parent:
            work_obj.compute_dates(cursor, user, pred_succ.predecessor.parent.id,
                    context=context)
        return id

PredecessorSuccessor()


class Leveling(Wizard):
    'Tasks Leveling'
    _name = 'project_plan.work.leveling'

    states = {
        'init': {
            'result': {
                'type': 'action',
                'action': '_leveling',
                'state': 'end',
                },
            },
        }

    def _leveling(self, cursor, user, data, context=None):
        work_obj = self.pool.get('project.work')
        work_obj.create_leveling(cursor, user, data['id'], context=context)
        return {}

Leveling()
