import re
import urllib
import operator

from webob import Request
from pkg_resources import iter_entry_points

from pydap.model import *
from pydap.handlers.lib import BaseHandler
from pydap.handlers.helper import constrain
from pydap.lib import get_slice, walk


RELOP = r"<=|<|>=|>|=|!="


def make_middleware(app, global_conf, **kwargs):
    return FunctionMiddleware(app, global_conf=global_conf, **kwargs)


class FunctionMiddleware(object):

    functions = dict((r.name, r.load())
            for r in iter_entry_points('pydap.function'))

    def __init__(self, app, **kwargs):
        self.app = app

    def __call__(self, environ, start_response):
        # Rewrite the constraint expression.
        environ['x-wsgiorg.want_parsed_response'] = True
        query = environ.pop('QUERY_STRING')
        if not query:
            return self.app(environ, start_response)

        # Try to recover the complete dataset from the response, using the
        # "avoiding serialization" specification from wsgi.org
        # (http://wsgi.org/wsgi/Specifications/avoiding_serialization)
        req = Request(environ)
        res = req.get_response(self.app)
        method = getattr(res.app_iter, 'x_wsgiorg_parsed_response', False)
        if not method:
            environ['QUERY_STRING'] = query
            return self.app(environ, start_response)
        template = method(DatasetType)               

        # Now we need to apply the selection on the dataset. First we
        # apply selections which don't have function calls:
        selection = [token for token in urllib.unquote(query).split('&') if token]
        if selection and not re.search(RELOP, selection[0]):
            tokens = combine_functions(tokenize(selection.pop(0)))
            projection = [str(token) for token in tokens 
                    if isinstance(token, (VARIABLE, FUNCTION_CALL))]
        else:
            projection = []

        regular = [token for token in selection if not FUNCTION.match(token)]
        template = constrain(template, '&'.join(regular))

        # ...and now with function calls:
        functions = [token for token in selection if FUNCTION.match(token)]
        for function in functions:
            if re.search(RELOP, function):
                call, op, other = re.split('(%s)' % RELOP, function)
            else:
                call, op, other = function, operator.eq, 1
            sequence = eval_func(template, call, self.functions)
            data = sequence[ sequence.keys()[0] ].data
            valid = op(data, other)
            for sequence in walk(template, SequenceType):
                sequence.data = sequence.data[ valid ]

        # Now we need to apply the projection.
        regular = [token for token in projection if not FUNCTION.match(token)]
        if regular:
            dataset = constrain(template, ','.join(regular))
        else:
            dataset = DatasetType(name=template.name, attributes=template.attributes)
        functions = [token for token in projection if FUNCTION.match(token)]
        for function in functions:
            var = eval_func(template, function, self.functions)
            # find where in the dataset we should put the variable; it could
            # be a sequence that should be merged with an existing sequence.
            var._set_id()
            for child in walk(var):
                parent = reduce(operator.getitem, [dataset] + child.id.split('.')[:-1])
                if child.name not in parent:
                    parent[child.name] = child

        # Return the original response (DDS, DAS, etc.)
        response = BaseHandler.response_map[ environ['pydap.response'] ]
        responder = response(dataset)
        return responder(environ, start_response)
        

def combine_functions(tokens):
    """
    Combine tokens that compose a function into a single FUNCTION_CALL token.

    """
    count = 0
    func_call = []
    for token in tokens:
        if isinstance(token, FUNCTION):
            count += 1
        elif isinstance(token, CLOSE):
            count -= 1
            if count == 0:
                func_call.append(str(token))
                yield FUNCTION_CALL(''.join(func_call))
                func_call = []

        if count > 0:
            func_call.append(str(token))
        else:
            yield token


def eval_func(dataset, function, functions):
    """
    Evaluate a function call.

    """
    tokens = tokenize(function)
    token = tokens.next()
    func = functions[str(token)]
    tokens = combine_functions(tokens)
    args = []
    count = 0
    while not (isinstance(token, CLOSE) and count == 0):
        token = tokens.next()
        if isinstance(token, OPEN):
            count += 1
        elif isinstance(token, CLOSE):
            count -= 1
        elif isinstance(token, (STRING, DATE)):
            args.append(str(token))
        elif isinstance(token, NUMBER):
            args.append(float(str(token)))
        elif isinstance(token, VARIABLE):
            names = [dataset] + re.sub('\[.*?\]', '', str(token)).split('.')
            var = reduce(operator.getitem, names)
            args.append(var)
        elif isinstance(token, FUNCTION_CALL):
            args.append(eval_func(dataset, str(token), functions))

    return func(dataset, *args)


class TOKEN(object):
    regexp = re.compile('.*')

    def __init__(self, input):
        self.input = input  

    def __str__(self):
        return self.input

    @classmethod
    def match(cls, input):
        m = cls.regexp.match(input)
        if m: return m.group(0)


class FUNCTION(TOKEN):
    regexp = re.compile(r'([\w_\.%]+)\(')

    @classmethod
    def match(cls, input):
        m = cls.regexp.match(input)
        if m: return m.group(1)


class FUNCTION_CALL(TOKEN):
    pass


class VARIABLE(TOKEN):
    regexp = re.compile(r'[A-Za-z][\w_\.%]*(\[\d+(:\d+)*\])*')


class STRING(TOKEN):
    regexp = re.compile(r'".+?[^\\]"')


class NUMBER(TOKEN):
    regexp = re.compile("""
        [+-]?         # first, match an optional sign
        (             # then match integers or f.p. mantissas:
            \d+       # start out with a ...
            (
                \.\d* # mantissa of the form a.b or a.
            )?        # ? takes care of integers of the form a
           |\.\d+     # mantissa of the form .b
        )
        ([eE][+-]?\d+)?  # finally, optionally match an exponent
        """, re.VERBOSE)


class OPEN(TOKEN):
    regexp = re.compile('\(')


class CLOSE(TOKEN):
    regexp = re.compile('\)')


class OPERATOR(TOKEN):
    regexp = re.compile('<=|>=|!=|=~|>|<|=')


class COMMA(TOKEN):
    regexp = re.compile(',')


class WHITESPACE(TOKEN):
    regexp = re.compile('(\s|%20)+')


class DATE(TOKEN):
    """This is for GrADS."""
    regexp = re.compile('\d{2}Z\d{2}\w{3}\d{4}')


def tokenize(input, type_=object):
    """
    A simple tokenizer.

    """
    Tokens = [FUNCTION, VARIABLE, STRING, DATE, NUMBER, OPEN, CLOSE, OPERATOR, COMMA, WHITESPACE]
    while input:
        for Token in Tokens:
            m = Token.match(input)
            if m:
                input = input[len(m):]
                token = Token(m)
                if isinstance(token, type_):
                    yield token
                break 
        else:
            raise StopIteration
