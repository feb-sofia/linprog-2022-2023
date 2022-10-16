from sympy import S, separatevars
import re
import pulp as p


def get_vars(obj, s):
    vlist = []
    rhs = []
    # lhs = []
    # c = []
    rel = []

    for l in s:
        t = S(l, evaluate=False)
        rhs.append(t.rhs)
        rel.append(t.rel_op)

        for x in t.free_symbols:
            vlist.append(str(x))

    obj_t = S(obj, evaluate=False)
    obj_t = separatevars(obj_t)

    for x in obj_t.free_symbols:
        vlist.append(str(x))

    vars = list(set(vlist))
    vars.sort()

    return vars


def prep_eq_string(s):
    s2 = re.sub(r"(\d)([a-zA-Z])", r"\1*\2", s)
    s2 = re.sub(r"\s+", "", s2)
    return s2


def build_solver(vars_c, vars_f, obj, constr):
    # get solver
    model = p.LpProblem("some", p.LpMaximize)
    vars = {}
    vars_lst = []
    constr_lst = []

    for v in vars_c:
        vars[v] = p.LpVariable(v, lowBound=0)
        vars_lst.append(vars[v])

    for v in vars_f:
        vars[v] = vars[v] = p.LpVariable(v)
        vars_lst.append(vars[v])

    # declare objective
    model += eval(obj, {}, vars)

    for c in constr:
        model += eval(c, {}, vars)

    model.solve()

    print("Model status {}".format(p.LpStatus[model.status]))

    return model


def parse_eq(s):
    lst = []
    obj = None
    obj_type = "max"
    free = []

    for l in s.split("\n"):
        l = re.sub(r"\s+", "", l.strip().lower())

        if len(l) == 0:
            continue

        if l.startswith("max") or l.startswith("min"):
            obj = l.replace("max", "").replace("min", "")

            if l.startswith("min"):
                obj_type = "min"

            continue

        if l.startswith("unconstrained"):
            free = l.replace("unconstrained", "").strip().split(",")
            continue

        lst.append(prep_eq_string(l))

    vars = get_vars(prep_eq_string(obj), lst)

    vars_c = list([v for v in vars if v not in free])
    solver = build_solver(vars, free, prep_eq_string(obj), lst)


