"""Subexpressions that make up a parsed grammar

These do the parsing.

"""
# TODO: Make sure all symbol refs are local--not class lookups or
# anything--for speed. And kill all the dots.

import re

from parsimonious.nodes import Node, RegexNode


__all__ = ['Expression', 'Literal', 'Regex', 'Sequence', 'OneOf', 'AllOf',
           'Not', 'Optional', 'ZeroOrMore', 'OneOrMore', 'ExpressionFlattener']


class _DummyCache(object):
    """Fake cache that always misses.

    This never gets used except in tests. TODO: Then what's it doing in here?
    Get it out.

    """
    def get(self, key, default=None):
        return default

    def __setitem__(self, key, value):
        pass

dummy_cache = _DummyCache()


class Expression(object):
    """A thing that can be matched against a piece of text"""

    # Slots are about twice as fast as __dict__-based attributes:
    # http://stackoverflow.com/questions/1336791/dictionary-vs-object-which-is-more-efficient-and-why

    # Top-level expressions--rules--have names. Subexpressions are anonymous: ''.
    __slots__ = ['name']

    def __init__(self, name=''):
        self.name = name

    def parse(self, text):
        """Return a parse tree of ``text``.

        Return ``None`` if the expression doesn't match the full string.

        On a more technical level: initialize the packrat cache and kick off
        the first ``match()`` call.

        """
        # The packrat cache. {(oid, pos): Node tree matched by object `oid` at
        #                                 index `pos`
        #                     ...}
        cache = {}

        node = self.match(text, cache=cache)
        # TODO: Stop doing this, and instead introduce an Empty symbol that
        # matches only at the EOF. Then we don't need both a public parse() and
        # a match(), and you have the option of matching part of a string while
        # still enjoying caching. OTOH, it might be nice to be able to match()
        # or parse() without messing with the grammar.
        if node is None or node.end - node.start != len(text):  # TODO: Why not test just end here?
            # If it was not a complete parse, return None:
            return None
        return node

    def match(self, text, pos=0, cache=dummy_cache):
        """Return the ``Node`` matching this expression at the given position.

        Return ``None`` if it doesn't match there. Check the cache first.

        The default args are just to make the tests easier to write.
        Ordinarily, ``parse()`` calls this and passes in a cache and pos.

        """
        # TODO: Maybe make this really suitable for public calling. Make cache
        # turn into a fresh {} if none is passed in.
        #
        # TODO: Optimize. Probably a hot spot.
        #
        # Is there a way of looking up cached stuff that's faster than hashing
        # this id-pos pair?
        #
        # If this is slow, think about the array module. It might (or might
        # not!) use more RAM, but it'll likely be faster than hashing things
        # all the time. Also, can we move all the allocs up front?
        #
        # To save space, we have lots of choices: (0) Quit caching whole Node
        # objects. Cache just what you need to reconstitute them. (1) Cache
        # only the results of entire rules, not subexpressions (probably a
        # horrible idea for rules that need to backtrack internally a lot). (2)
        # Age stuff out of the cache somehow. LRU?
        #print self.__class__.__name__, self.name
        expr_id = id(self)
        cached = cache.get((expr_id, pos), ())
        if cached is not ():
            return cached
        uncached = self._uncached_match(text, pos, cache)
        cache[(expr_id, pos)] = uncached

        return uncached

    def __unicode__(self):
        return u'<%s%s at 0x%s>' % (
            self.__class__.__name__,
            (' called "%s"' % self.name) if self.name else '',
            id(self))

    def __str__(self):
        return self.__unicode__().encode('utf-8')

    __repr__ = __str__


class Empty(Expression):
    """The empty expression, which matches only at the end of the text

    Stick one of these at the end of your grammar if you want to make it match
    only whole texts.

    """
    # TODO: You know, maybe a kwargs on parse() is easier to understand for the
    # non-having-studied-parsing among us. Plus then you don't have to mess
    # with the grammar if you want to do match() sometimes and search() others.
    # Is Empty useful anywhere but the EOF?

    def _uncached_match(self, text, pos=0, cache=dummy_cache):
        """Return 0 if we're at the EOF, ``None`` otherwise."""
        if pos == len(text):
            return 0


class Literal(Expression):
    """A string literal

    Use these if you can; they're the fastest.

    """
    __slots__ = ['literal']

    def __init__(self, literal, name=''):
        super(Literal, self).__init__(name)
        self.literal = literal

    def _uncached_match(self, text, pos=0, cache=dummy_cache):
        if text.startswith(self.literal, pos):
            return Node(self.name, text, pos, pos + len(self.literal))


class Regex(Expression):
    """An expression that matches what a regex does.

    Use these as much as you can and jam as much into each one as you can;
    they're fast.

    """
    __slots__ = ['re']

    def __init__(self, pattern, name='', ignore_case=False, locale=False,
                 multiline=False, dot_all=False, unicode=False, verbose=False):
        super(Regex, self).__init__(name)
        self.re = re.compile(pattern, (ignore_case and re.I) |
                                      (locale and re.L) |
                                      (multiline and re.M) |
                                      (dot_all and re.S) |
                                      (unicode and re.U) |
                                      (verbose and re.X))

    def _uncached_match(self, text, pos=0, cache=dummy_cache):
        """Return length of match, ``None`` if no match."""
        m = self.re.match(text, pos)
        if m is not None:
            span = m.span()
            node = RegexNode(self.name, text, pos, pos + span[1] - span[0])
            node.match = m  # TODO: A terrible idea for cache size?
            return node


class _Compound(Expression):
    """An abstract expression which contains other expressions"""

    __slots__ = ['members']

    def __init__(self, *members, **kwargs):
        """``members`` is a sequence of expressions."""
        super(_Compound, self).__init__(kwargs.get('name', ''))
        self.members = members


# TODO: Add round-tripping, so the pretty-printed version of an Expression is
# its PEG DSL representation. Sure makes it easier to debug expression trees.


class Sequence(_Compound):
    """A series of expressions that must match contiguous, ordered pieces of
    the text

    In other words, it's a concatenation operator: each piece has to match, one
    after another.

    """
    def _uncached_match(self, text, pos=0, cache=dummy_cache):
        new_pos = pos
        length_of_sequence = 0
        children = []
        for m in self.members:
            node = m.match(text, new_pos, cache)
            if node is None:
                return None
            children.append(node)
            length = node.end - node.start
            new_pos += length
            length_of_sequence += length
        # Hooray! We got through all the members!
        return Node(self.name, text, pos, pos + length_of_sequence, children)


class OneOf(_Compound):
    """A series of expressions, one of which must match

    Expressions are tested in order from first to last. The first to succeed
    wins.

    """
    def _uncached_match(self, text, pos=0, cache=dummy_cache):
        for m in self.members:
            node = m.match(text, pos, cache)
            if node is not None:
                # Wrap the succeeding child in a node representing the OneOf:
                return Node(self.name, text, pos, node.end, children=[node])


class AllOf(_Compound):
    """A series of expressions, each of which must succeed from the current
    position.

    The returned node is from the last member. If you like, you can think of
    the preceding members as lookaheads.

    """
    def _uncached_match(self, text, pos=0, cache=dummy_cache):
        for m in self.members:
            node = m.match(text, pos, cache)
            if node is None:
                return None
        if node is not None:
            return Node(self.name, text, pos, node.end, children=[node])


class Not(_Compound):
    """An expression that succeeds only if the expression within it doesn't

    In any case, it never consumes any characters; it's a negative lookahead.

    """
    def _uncached_match(self, text, pos=0, cache=dummy_cache):
        # FWIW, the implementation in Parsing Techniques in Figure 15.29 does
        # not bother to cache NOTs directly.
        node = self.members[0].match(text, pos, cache)
        if node is None:
            return Node(self.name, text, pos, pos)


# Quantifiers. None of these is strictly necessary, but they're darn handy.

class Optional(_Compound):
    """An expression that succeeds whether or not the contained one does

    If the contained expression succeeds, it goes ahead and consumes what it
    consumes. Otherwise, it consumes nothing.

    """
    def _uncached_match(self, text, pos=0, cache=dummy_cache):
        node = self.members[0].match(text, pos, cache)
        return (Node(self.name, text, pos, pos) if node is None else
                Node(self.name, text, pos, node.end, children=[node]))


# TODO: Merge with OneOrMore.
class ZeroOrMore(_Compound):
    """An expression wrapper like the * quantifier in regexes."""
    def _uncached_match(self, text, pos=0, cache=dummy_cache):
        new_pos = pos
        children = []
        while True:
            node = self.members[0].match(text, new_pos, cache)
            if node is None or not (node.end - node.start):
                # Node was None or 0 length. 0 would otherwise loop infinitely.
                return Node(self.name, text, pos, new_pos, children)
            children.append(node)
            new_pos += node.end - node.start


class OneOrMore(_Compound):
    """An expression wrapper like the + quantifier in regexes.

    You can also pass in an alternate minimum to make this behave like "2 or
    more", "3 or more", etc.

    """
    __slots__ = ['min']

    # TODO: Add max. It should probably succeed if there are more than the max
    # --just not consume them.

    def __init__(self, member, name='', min=1):
        super(OneOrMore, self).__init__(member, name=name)
        self.min = min

    def _uncached_match(self, text, pos=0, cache=dummy_cache):
        new_pos = pos
        children = []
        while True:
            node = self.members[0].match(text, new_pos, cache)
            if node is None:
                break
            children.append(node)
            length = node.end - node.start
            if length == 0:  # Don't loop infinitely.
                break
            new_pos += length
        if len(children) >= self.min:
            return Node(self.name, text, pos, new_pos, children)


class ExpressionFlattener(object):
    """A visitor that turns expression trees back into PEG DSL

    You typically don't need this, but it comes in handy while debugging the
    library. You could also use it to freeze grammars that you
    machine-generate.

    The visit_* methods all return strings. Thus, they all also receive a bunch
    of strings as their second parameters.

    """
    CAPS = re.compile('([A-Z])')

    def mappify(self, expr):
        """Return a map of expression names to stringified expressions."""
        named_exprs = {}
        self.visit(expr, named_exprs)
        return named_exprs

    def stringify(self, expr):
        # TODO: Output ``expr``  first so a Grammar built from the return value
        # will use that as the starting rule.
        return '\n'.join('%s = %s' % (k, v) for k, v in
                         self.mappify(expr).iteritems())

    def visit(self, expr, named_exprs):
        if expr.name not in named_exprs:
            method = getattr(self,
                             'visit' + self.pep8(expr.__class__.__name__))
            dsl = method(expr, [self.visit(e, named_exprs) for e in
                                getattr(expr, 'members', [])])
            if expr.name:
                named_exprs[expr.name] = dsl
        return expr.name or dsl

    def pep8(self, name):
        """Turn NamesLikeThis into names_like_this."""
        return self.CAPS.sub(lambda m: '_' + m.groups()[0].lower(), name)

    def regex_flags_from_bits(self, bits):
        """Return the textual eqivalent of numerically encoded regex flags."""
        flags = 'tilmsux'
        return ''.join(flags[i] if (1 << i) & bits else '' for i in xrange(6))

    def visit_one_or_more(self, expr, (term,)):
        return '%s+' % term

    def visit_zero_or_more(self, expr, (term,)):
        return '%s*' % term

    def visit_optional(self, expr, (term,)):
        return '%s?' % term

    def visit_all_of(self, expr, terms):
        return ' & '.join(terms)

    def visit_one_of(self, expr, terms):
        return ' / '.join(terms)

    def visit_sequence(self, expr, terms):
        return ' '.join(terms)

    def visit_regex(self, regex, visited_children):
        # TODO: Get backslash escaping right.
        return '~"%s"%s' % (regex.re.pattern,
                            self.regex_flags_from_bits(regex.re.flags))

    def visit_literal(self, literal, visited_children):
        # TODO: Get backslash escaping right.
        return '"%s"' % literal.literal
