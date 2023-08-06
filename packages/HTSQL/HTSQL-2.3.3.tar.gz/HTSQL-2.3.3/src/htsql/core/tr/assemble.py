#
# Copyright (c) 2006-2013, Prometheus Research, LLC
#


"""
:mod:`htsql.core.tr.assemble`
=============================

This module implements the assembling process.
"""


from ..util import Printable, Hashable, listof, maybe
from ..adapter import Adapter, adapt, adapt_many
from ..domain import BooleanDomain, UntypedDomain, Record, ID
from .coerce import coerce
from .binding import WeakSegmentBinding
from .flow import (Code, SegmentCode, LiteralCode, FormulaCode, CastCode,
                   RecordCode, IdentityCode, AnnihilatorCode, CorrelationCode,
                   Unit, ColumnUnit, CompoundUnit)
from .term import (PreTerm, Term, UnaryTerm, BinaryTerm, TableTerm,
                   ScalarTerm, FilterTerm, JoinTerm, CorrelationTerm,
                   EmbeddingTerm, ProjectionTerm, OrderTerm, SegmentTerm,
                   QueryTerm)
from .frame import (ScalarFrame, TableFrame, NestedFrame,
                    SegmentFrame, QueryFrame,
                    LiteralPhrase, TruePhrase, CastPhrase,
                    ColumnPhrase, ReferencePhrase, EmbeddingPhrase,
                    FormulaPhrase, Anchor, LeadingAnchor)
from .signature import (Signature, IsEqualSig, IsTotallyEqualSig, IsInSig,
                        IsNullSig, NullIfSig, IfNullSig, CompareSig,
                        AndSig, OrSig, NotSig, SortDirectionSig, ToPredicateSig,
                        FromPredicateSig)


class Claim(Hashable, Printable):
    """
    Represents an export request.

    A :class:`Claim` object represents a request to the broker frame
    to export a unit from the target frame.

    The claim indicates that the ``SELECT`` clause of the broker frame
    must contain a phrase that evaluates the unit.

    The target frame must either coincide with the broker frame or
    be a descendant of the broker frame.  When the target and the
    broker coincide, the broker is responsible for evaluating the
    unit value.  Otherwise, the broker imports the unit value from
    one of its subframes.

    Claim objects are compared by-value.  That is, two claim objects
    are equal if their units, brokers, and targets are equal to each
    other.

    `unit` (:class:`htsql.core.tr.flow.Unit`)
        The exported unit.

    `broker` (an integer)
        The tag of the broker term/frame.  The broker frame is expected
        to export a phrase corresponding to the given unit.

    `target` (an integer)
        The tag of the target term/frame.  The target frame is responsible
        for evaluating the unit.  The target term must be a descendant
        of the broker term or coincide with the broker term.
    """

    def __init__(self, unit, broker, target):
        assert isinstance(unit, Unit)
        assert isinstance(broker, int)
        assert isinstance(target, int)
        self.unit = unit
        self.broker = broker
        self.target = target

    def __basis__(self):
        # Claim objects need by-value comparison to avoid assigning
        # multiple claims for the same unit.
        return (self.unit, self.broker, self.target)

    def __str__(self):
        return "(%s)->%s->%s" % (self.unit, self.broker, self.target)


class Gate(object):
    """
    Encapsulates a dispatching context.

    Dispatching context provides information necessary to demand
    and supply unit claims.

    `is_nullable` (Boolean)
        Indicates that the currently assembled frame is going
        to be joined to the parent frame using an outer join.

        This flag affects the `is_nullable` indicator of
        exported phrases.

    `dispatches` (a dictionary `tag -> tag`)
        Maps a descendant term to the immediate child whose subtree contains
        the term.

        The `dispatches` table is used when generating unit claims
        to determine the broker term by the target term.

        See also the `offsprings` attribute of :class:`htsql.core.tr.term.Term`.

    `routes` (a dictionary `Unit | Flow -> tag`)
        Maps a unit to a term capable of evaluating the unit.

        The `routes` table is used when generating unit claims
        to determine the target term by the unit.

        A key of the `routes` table is either a :class:`htsql.core.tr.flow.Unit`
        node or a :class:`htsql.core.tr.flow.Flow` node.  The latter indicates
        that the corresponding term is capable of exporting any primitive
        unit from the given flow.

        See also the `routes` attribute of :class:`htsql.core.tr.term.Term`.

    Note that `dispatches` and `routes` come from `offsprings` and `routes`
    attributes of :class:`htsql.core.tr.term.Term`.  However they do not have to
    come from the same term!  Typically, `dispatches` comes from the term
    which is currently translated to a frame, and `routes` comes either
    from the same term or from one of its direct children.
    """

    def __init__(self, is_nullable, dispatches, routes):
        # Sanity check on the arguments.  We do not perform a costly check
        # on the keys and the values of the mappings since they come directly
        # from term attributes and it is hard to mess them up.
        assert isinstance(is_nullable, bool)
        assert isinstance(dispatches, dict)
        assert isinstance(routes, dict)
        self.is_nullable = is_nullable
        self.dispatches = dispatches
        self.routes = routes


class AssemblingState(object):
    """
    Encapsulates the state of the assembling process.

    State attributes:

    `gate` (:class:`Gate`)
        The current dispatching context.

    `claim_set` (a set of :class:`Claim`)
        All requested unit claims.

    `claims_by_broker` (a mapping `tag -> [Claim]`)
        Unit claims grouped by the broker.

        A key of the mapping is the broker tag.  A value of the mapping
        is a list of :class:`Claim` objects with the same broker.

    `phrases_by_claim` (a mapping `Claim -> [Phrase]`)
        Satisfied claims.

        A key of the mapping is a :class:`Claim` object.  A value of the
        mapping is a list of :class:`htsql.core.tr.frame.ExportPhrase` objects.
    """

    def __init__(self):
        # The stack of previous gates.
        self.gate_stack = []
        # The current gate (dispatching context).
        self.gate = None
        # The set of all unit claims (used for checking for duplicates).
        self.claim_set = None
        # Unit claims grouped by the broker.
        self.claims_by_broker = None
        # Satisfied unit claims.
        self.phrases_by_claim = None
        # Stencils and other composition state.
        self.subterms_by_segment = {}
        self.stencils_by_term = {}
        self.location_by_term = {}
        self.shift_by_term = {}
        self.name_stack = []
        self.name = None
        self.segment_stack = []
        self.segment = None
        self.correlations_stack = []
        self.correlations = {}

    def push_correlations(self, correlations):
        self.correlations_stack.append(self.correlations)
        self.correlations = correlations

    def pop_correlations(self):
        self.correlations = self.correlations_stack.pop()

    def push_name(self, name):
        assert isinstance(name, maybe(unicode))
        self.name_stack.append(self.name)
        self.name = name

    def pop_name(self):
        self.name = self.name_stack.pop()

    def push_segment(self, code):
        assert isinstance(code, SegmentCode)
        term = self.subterms_by_segment[self.segment][code]
        self.segment_stack.append(self.segment)
        self.segment = term
        self.shift_by_term[term] = 0

    def pop_segment(self):
        self.segment = self.segment_stack.pop()

    def save_subterms(self, term, subterms):
        assert isinstance(term, maybe(SegmentTerm))
        assert isinstance(subterms, listof(SegmentTerm))
        term_by_code = dict((subterm.code, subterm)
                            for subterm in subterms)
        self.subterms_by_segment[term] = term_by_code

    def save_location(self, term, location):
        assert isinstance(term, SegmentTerm)
        assert isinstance(location, maybe(int))
        self.location_by_term[term] = location

    def get_location(self):
        return self.location_by_term[self.segment]

    def save_stencils(self, term, stencils):
        assert isinstance(term, SegmentTerm)
        assert isinstance(stencils, listof(listof(int))) and len(stencils) == 3
        self.stencils_by_term[term] = stencils

    def get_code_stencil(self):
        return self.stencils_by_term[self.segment][0]

    def get_superkey_stencil(self):
        return self.stencils_by_term[self.segment][1]

    def get_key_stencil(self):
        return self.stencils_by_term[self.segment][2]

    def get_next_index(self):
        stencil = self.get_code_stencil()
        index = stencil[self.shift_by_term[self.segment]]
        self.shift_by_term[self.segment] += 1
        return index

    def decompose(self, code):
        return Decompose.__invoke__(code, self)

    def set_tree(self, term):
        """
        Initializes the assembling state.

        This method must be called before assembling any frames.

        `term` (:class:`htsql.core.tr.term.SegmentTerm`)
            The term corresponding to the top-level ``SELECT`` statement.
        """
        assert isinstance(term, SegmentTerm)
        assert not self.gate_stack
        # Use the segment term both as the dispatcher and the router.  We
        # set `is_nullable` to `False`, but the value does not really matter
        # since we never export from the segment frame.
        self.gate = Gate(False, term.offsprings, term.routes)
        # Initialize claim containers.
        self.claim_set = set()
        self.claims_by_broker = {}
        self.phrases_by_claim = {}
        # Initialize `claims_by_broker` with an empty list for each node
        # in the term tree.
        self.claims_by_broker[term.tag] = []
        for offspring in term.offsprings:
            self.claims_by_broker[offspring] = []

    def flush(self):
        """
        Clears the assembling state.
        """
        # Revert all attributes to their pristine state.  We assume that
        # `gate_stack` is already empty.
        self.gate = None
        self.claim_set = None
        self.claims_by_broker = None
        self.phrases_by_claim = None
        self.segment_indexes = None
        self.correlations_stack = []
        self.correlations = {}

    def push_gate(self, is_nullable=None, dispatcher=None, router=None):
        """
        Updates the current dispatching context.

        `is_nullable` (Boolean or ``None``)
            Indicates that the currently assembled frame is to be
            attached to the parent frame using an ``OUTER`` join.

            If ``None``, keeps the current value.

            When satisfying the claims directed to the currently
            constructed frame, this flag is used to determine whether
            the exported values are nullable or not.

        `dispatcher` (:class:`htsql.core.tr.term.Term` or ``None``)
            Specifies the dispatcher term.

            If ``None``, keeps the current dispatcher.

            The dispatcher term (more exactly, the `offsprings` table
            of the term) maps a descendant term to the immediate
            child whose subtree contains the term.

            When generating claims, the dispatcher is used to find
            the broker term by the target term.

            Typically, the dispatcher term is the one currently
            translated to a frame node.

        `router` (:class:`htsql.core.tr.term.Term` or ``None``)
            Specifies the router term.

            If ``None``, uses `dispatcher` as the router term.
            If both `dispatcher` and `router` are ``None``,
            keeps the current router.

            The router term (more exactly, the `routes` table of the
            term) maps a unit to a term capable of evaluating the unit.

            When generating claims, the router is used to find
            the target term by the unit.

            Typically, the router term is the one currently translated
            to a frame node or one of its immediate children.
        """
        # If `is_nullable` is not set, keep the current value.
        if is_nullable is None:
            is_nullable = self.gate.is_nullable
        # Extract the dispatching table from the given `dispatcher` term,
        # keeps the current table if `dispatcher` is not specified.
        if dispatcher is not None:
            dispatches = dispatcher.offsprings
        else:
            dispatches = self.gate.dispatches
        # When changing the dispatcher, we always want to change the router
        # as well.  Thus, when `dispatcher` is specified, but `router` is not,
        # we assume that `router` coincides with `dispatcher`.
        if router is None:
            router = dispatcher
        # Extract the routing table from the given `router` term, keeps
        # the current table if `router` is not specified.
        if router is not None:
            routes = router.routes
        else:
            routes = self.gate.routes
        # Save the current gate and install the new one.
        self.gate_stack.append(self.gate)
        self.gate = Gate(is_nullable, dispatches, routes)

    def pop_gate(self):
        """
        Restores the previous dispatching context.
        """
        self.gate = self.gate_stack.pop()

    def assemble(self, term):
        """
        Assembles a frame node for the given term.

        `term` (:class:`htsql.core.tr.term.Term`)
            A term node.
        """
        # Realize and call the `Assemble` adapter.
        return assemble(term, self)

    def appoint(self, unit):
        """
        Generates a claim for the given unit.

        This method finds the target and the broker terms that are
        capable of evaluating the unit and returns the corresponding
        :class:`Claim` object.

        `unit` (:class:`htsql.core.tr.flow.Unit`)
            The unit to make a claim for.
        """
        # To make a claim, we need to find two terms:
        # - the target term, one that is capable of evaluating the unit;
        # - the broker term, an immediate child which contains the target
        #   term (or, possibly coincides with the target term).
        # We use the current routing and dispatching tables to determine
        # the target and the broker terms respectively.
        # Note that it is a responsibility of the caller to ensure that
        # the current routing table contains the given unit.

        ## Extract the (tag of the) target term from the current routing
        ## table.  Recall that `routes` does not keep primitive units directly,
        ## instead a flow node represents all primitive units that belong
        ## to that flow.
        #if unit.is_primitive:
        #    assert unit.flow in self.gate.routes
        #    target = self.gate.routes[unit.flow]
        #if unit.is_compound:
        #    assert unit in self.gate.routes
        #    target = self.gate.routes[unit]
        assert unit in self.gate.routes, (unit, self.gate.routes)
        target = self.gate.routes[unit]
        # Extract the (tag of the) broker term from the current dispatch
        # table.
        # FIXME?: there is a possibility that the target coincides with
        # the current term -- it may happen, for instance, with scalar units.
        # To handle this case properly, we need to dismantle the unit
        # and appoint all its sub-units.  However currently the compiler
        # takes special care to ensure that scalar units are never routed
        # to the term where they are defined, so we do not bother with
        # handling this case here.
        assert target in self.gate.dispatches
        broker = self.gate.dispatches[target]
        # Generate and return a claim object.
        return Claim(unit, broker, target)

    def forward(self, claim):
        """
        Generates a forward claim for the given claim.

        This function takes a claim targeted to one of the current term's
        descendants and returns a new claim dispatched to the current term's
        immediate child.

        `claim` (:class:`Claim`)
            A claim dispatched to the current term.
        """
        # This function is used when a term gets a claim targeted not
        # to the term itself, but to one of its descendants.  In this
        # case, we need to re-dispatch the claim to the immediate child
        # whose subtree contains the target term.
        assert claim.target in self.gate.dispatches
        broker = self.gate.dispatches[claim.target]
        return Claim(claim.unit, broker, claim.target)

    def schedule(self, code, dispatcher=None, router=None):
        """
        Appoints and assigns claims for all units of the given code.

        `code` (:class:`htsql.core.tr.flow.Code`)
            A code object to schedule.

        `dispatcher` (:class:`htsql.core.tr.term.Term` or ``None``)
            Specifies the dispatcher to use when appointing units.

            If ``None``, keeps the current dispatcher.

        `router` (:class:`htsql.core.tr.term.Term` or ``None``)
            Specifies the router to use when appointing units.

            If ``None``, uses `dispacher` as the router term;
            if both are ``None``, keeps the current router.
        """
        # Update the gate to use the given dispatcher and router.
        self.push_gate(dispatcher=dispatcher, router=router)
        # Iterate over all units included to the given code node.
        for unit in code.units:
            # Generate a claim for the unit.
            claim = self.appoint(unit)
            # Assign the claim to the broker.
            self.demand(claim)
        # Restore the original gate.
        self.pop_gate()

    def evaluate_all(self, code, dispatcher=None, router=None):
        """
        Evaluates the given code node.

        Returns the corresponding :class:`htsql.core.tr.frame.Phrase` node.

        It is assumed that the code node was previously scheduled
        with :meth:`schedule` and all the claims were satisfied.

        `code` (:class:`htsql.core.tr.flow.Code`)
            The code node to evaluate.

        `dispatcher` (:class:`htsql.core.tr.term.Term` or ``None``)
            Specifies the dispatcher to use when appointing units.

            If ``None``, keeps the current dispatcher.

        `router` (:class:`htsql.core.tr.term.Term` or ``None``)
            Specifies the router to use when appointing units.

            If ``None`` uses `dispacher` as the router term;
            if both are ``None``, keeps the current router.
        """
        # Update the gate to use the given dispatcher and router.
        self.push_gate(dispatcher=dispatcher, router=router)
        # Realize and call the `Evaluate` adapter.
        phrases = list(Evaluate.__invoke__(code, self))
        # Restore the original gate.
        self.pop_gate()
        # Return the generated phrase.
        return phrases

    def evaluate(self, code, dispatcher=None, router=None):
        phrases = self.evaluate_all(code, dispatcher, router)
        assert len(phrases) == 1
        [phrase] = phrases
        return phrase

    def demand(self, claim):
        """
        Assigns the given claim to the broker.

        `claim` (:class:`Claim`)
            The claim to assign.
        """
        # Check is the claim (remember, they are compared by value) was
        # already assigned.
        if not claim in self.claim_set:
            # Add it to the list of all claims.
            self.claim_set.add(claim)
            # Assign it to the broker.
            self.claims_by_broker[claim.broker].append(claim)

    def supply(self, claim, *phrases):
        """
        Satisfies the claim.

        `claim` (:class:`Claim`)
            The claim to satisfy.

        `phrases` ([:class:`htsql.core.tr.frame.Phrase`])
            The phrases satisfying the claim.
        """
        # A few sanity checks.  Verify that the claim was actually requested.
        assert claim in self.claim_set
        # Verify that the claim was not satisfied already.
        assert claim not in self.phrases_by_claim
        # Save the phrase.
        self.phrases_by_claim[claim] = list(phrases)

    def to_predicate(self, phrase):
        return FormulaPhrase(ToPredicateSig(), phrase.domain,
                             phrase.is_nullable, phrase.expression, op=phrase)

    def from_predicate(self, phrase):
        return FormulaPhrase(FromPredicateSig(), phrase.domain,
                             phrase.is_nullable, phrase.expression, op=phrase)


class Assemble(Adapter):
    """
    Translates a term node to a frame node.

    This is an interface adapter, see subclasses for implementations.

    The :class:`Assemble` adapter has the following signature::

        Assemble: (Term, AssemblingState) -> Frame

    The adapter is polymorphic on the `Term` argument.

    `term` (:class:`htsql.core.tr.term.Term`)
        A term node.

    `state` (:class:`AssemblingState`)
        The current state of the assembling process.
    """

    adapt(PreTerm)

    def __init__(self, term, state):
        assert isinstance(term, PreTerm)
        assert isinstance(state, AssemblingState)
        self.term = term
        self.state = state

    def __call__(self):
        # Implement in subclasses.
        raise NotImplementedError("the compile adapter is not implemented"
                                  " for a %r node" % self.term)


class AssembleTerm(Assemble):
    """
    Assembles a frame for a proper term node.

    This adapt :class:`Assemble` for proper term nodes (i.e., not a
    :class:`htsql.core.tr.term.QueryTerm`).

    Attributes:

    `claims` (a list of :class:`Claim`)
        The claims that are dispatched to the term.
    """

    adapt(Term)

    def __init__(self, term, state):
        super(AssembleTerm, self).__init__(term, state)
        # Extract claims dispatched to the given term.
        self.claims = state.claims_by_broker[term.tag]


class AssembleScalar(Assemble):
    """
    Assembles a (scalar) frame for a scalar term.
    """

    adapt(ScalarTerm)

    def __call__(self):
        # A scalar term cannot export anything and thus should never receive
        # any claims.
        assert not self.claims
        # Generate and return a frame node.
        return ScalarFrame(self.term)


class AssembleTable(Assemble):
    """
    Assembles a (table) frame for a table term.
    """

    adapt(TableTerm)

    def __call__(self):
        # The actual table entity.
        table = self.term.table
        # Iterate over and satisfy all the claims.
        for claim in self.claims:
            # Sanity checks.
            assert claim.broker == self.term.tag
            assert claim.target == self.term.tag
            # FIXME: Currently, a table term could only expect claims for
            # column units.  In the future, however, we may wish to allow
            # other kinds of units (for instance, to support pseudo-columns).
            # To handle that, we may need to introduce a new adapter
            # dispatched on the unit type.
            assert claim.unit.is_primitive
            assert isinstance(claim.unit, ColumnUnit)
            # The requested column entity.
            column = claim.unit.column
            # More sanity checks.
            assert column.table == table
            # The exported phrase is nullable if the column itself is nullable,
            # but also if the frame is attached to its parent using an
            # `OUTER JOIN`.
            is_nullable = (column.is_nullable or self.state.gate.is_nullable)
            # Satisfy the claim with a column phrase.
            export = ColumnPhrase(self.term.tag, column, is_nullable,
                                  claim.unit)
            self.state.supply(claim, export)
        # Generate and return a frame node.
        return TableFrame(table, self.term)


class AssembleBranch(Assemble):
    """
    Assembles a branch frame.

    This is a default implementation used by all non-terminal (i.e. unary
    or binary) terms.
    """

    adapt_many(UnaryTerm, BinaryTerm)

    def delegate(self):
        # Review all the given claims.
        for claim in self.claims:
            assert claim.broker == self.term.tag
            # If the claim is not targeted to us directly, we are not
            # responsible for evaluating it.  Just forward it to the
            # next hop.
            if claim.target != self.term.tag:
                next_claim = self.state.forward(claim)
                self.state.demand(next_claim)
            # Otherwise, the frame will evaluate the unit of the claim.
            # Dismantle the unit and submit claims for all of its sub-units.
            else:
                # FIXME: Here we assume that a claim targeted to a non-leaf
                # term is always compound.  This may (or may not) change
                # in the future.
                assert claim.unit.is_compound
                self.state.schedule(claim.unit.code)

    def assemble_include(self):
        # Assemle the `FROM` list; should be overridden in subclasses.
        return []

    def assemble_embed(self):
        # Assemble the embedded frames; override in subclasses.
        # The default implementations assumes there are no embedded subframes.
        return []

    def assemble_select(self):
        # Assemble the `SELECT` clause and satisfy all the claims; may be
        # overridden in subclasses.

        # Note that this method is called after `assemble_include()` and
        # `assemble_embed()`, so any claims requested by `delegate()` should
        # be already satisfied.

        # List of `SELECT` phrases.
        select = []
        # A mapping: `phrase` -> the position of the phrase in the `select`
        # list.  We use it to avoid duplicates in the `SELECT` list.
        index_by_phrase = {}

        # For each of the claims:
        # - generate a phrase corresponding to the unit of the claim;
        # - add the phrase to the `SELECT` list;
        # - satisfy the claim with a reference to the generated phrase.
        for claim in self.claims:

            # Generate a phrase corresponding to the claim.  Check if
            # the claim is not targeted to us directly -- then it was
            # targeted to one of our descendants.
            if claim.target != self.term.tag:
                # Generate a forward claim (again).
                next_claim = self.state.forward(claim)
                # We expect the forward claim to be already satisfied.
                assert next_claim in self.state.phrases_by_claim
                # Get the export phrase that satisfied the claim.
                phrases = self.state.phrases_by_claim[next_claim]
            # Otherwise, the claim is targeted to us and we are responsible
            # for evaluating the unit of the claim.
            else:
                # Since it is a branch term, the unit must be compound.
                # So we evaluate the code expression of the unit.
                phrases = self.state.evaluate_all(claim.unit.code)

            export = []
            for phrase in phrases:
                # Check if the generated phrase is a duplicate.  Even though
                # all claims are unique, different claims may still produce
                # identical phrases.  Therefore an extra check here is necessary.
                if phrase not in index_by_phrase:
                    # So it is not a duplicate: add it to the `SELECT` list.
                    index = len(select)
                    select.append(phrase)
                    index_by_phrase[phrase] = index

                # Generate an export reference to the phrase.
                index = index_by_phrase[phrase]
                domain = phrase.domain
                # The reference is nullable if the referenced phrase itself is
                # nullable or the assembled frame is to be attached using an
                # `OUTER JOIN`.
                is_nullable = (phrase.is_nullable or
                               self.state.gate.is_nullable)
                reference = ReferencePhrase(self.term.tag, index, domain,
                                            is_nullable, claim.unit)
                export.append(reference)
            # Satisfy the claim with the generated reference.
            self.state.supply(claim, *export)

        # It might happen (though with the way the compiler generates the term
        # tree, it is probably impossible) that the frame has no claims
        # dispatched to it and therefore the `SELECT` list is empty.  Since
        # SQL syntax does not permit an empty `SELECT` list, we add a dummy
        # phrase to the list.
        if not select:
            select = [TruePhrase(self.term.expression)]
        # All claims are satisfied; return the generated `SELECT` list.
        return select

    def assemble_where(self):
        # Assemble the `WHERE` clause; could be overridden in subclasses.
        return None

    def assemble_group(self):
        # Assemble the `GROUP BY` clause; could be overridden in subclasses.
        return []

    def assemble_having(self):
        # Assemble the `HAVING` clause; could be overridden in subclasses.
        return None

    def assemble_order(self):
        # Assemble the `ORDER BY` clause; could be overridden in subclasses.
        return []

    def assemble_limit(self):
        # Assemble the `LIMIT` clause; could be overridden in subclasses.
        return None

    def assemble_offset(self):
        # Assemble the `OFFSET` clause; could be overridden in subclasses.
        return None

    def assemble_frame(self, include, embed, select,
                       where, group, having,
                       order, limit, offset):
        # Assemble a frame node with the given clauses; could be overridden
        # in subclasses.
        return NestedFrame(include, embed, select,
                           where, group, having,
                           order, limit, offset, self.term)

    def __call__(self):
        # Review the given claims and dispatch new ones.
        self.delegate()
        # Assemble a `FROM` clause.
        include = self.assemble_include()
        # Assemble all embedded frames.
        embed = self.assemble_embed()
        # Assemble the `SELECT` clause and satisfy the claims.
        select = self.assemble_select()
        # Assemble the remaining clauses of the frame.
        where = self.assemble_where()
        group = self.assemble_group()
        having = self.assemble_having()
        order = self.assemble_order()
        limit = self.assemble_limit()
        offset = self.assemble_offset()
        # Generate and return a frame node.
        return self.assemble_frame(include, embed, select,
                                   where, group, having,
                                   order, limit, offset)


class AssembleUnary(AssembleBranch):
    """
    Assembles a frame for an unary term.

    This is a default implementation used by all unary terms.
    """

    adapt(UnaryTerm)
    # Note that `AssembleUnary` is inherited from `AssembleBranch` (not
    # `Assemble`) to indicate relative priority of these two implementations.

    def assemble_include(self):
        # Assemble the `FROM` list.  All unary terms have just one child,
        # so they could all share the same implementation.

        # Set up the dispatch context for the child term.
        self.state.push_gate(is_nullable=False, dispatcher=self.term.kid)
        # Assemble the frame by the child term.
        frame = self.state.assemble(self.term.kid)
        # Restore the original dispatch context.
        self.state.pop_gate()
        # Generate a `JOIN` clause.  Since it is the first (and the only)
        # subframe, the `JOIN` clause has no join condition.
        anchor = LeadingAnchor(frame)
        # Return a `FROM` list with a single subframe.
        return [anchor]


class AssembleFilter(Assemble):
    """
    Assembles a frame for a filter term.
    """

    adapt(FilterTerm)

    def delegate(self):
        # Call the super `delegate()` to review and forward claims.
        super(AssembleFilter, self).delegate()
        # Appoint and assign claims for the `filter` expression.
        # Note that we route the filter units against the term's child --
        # it could do routing because we injected `filter` to the `kid`
        # term when the filter term was compiled.  (However since the filter
        # term contains all the routes of its child, we could have routed
        # the filter against the parent term with the same effect.)
        self.state.schedule(self.term.filter,
                            router=self.term.kid)

    def assemble_where(self):
        # Assemble a `WHERE` clause.
        # Evaluate the `filter` expression (we expect all its claims
        # to be already satisfied).
        phrase = self.state.evaluate(self.term.filter,
                                     router=self.term.kid)
        return self.state.to_predicate(phrase)


class AssembleOrder(Assemble):
    """
    Assembles a frame for an order term.
    """

    adapt(OrderTerm)

    def delegate(self):
        # Call the super `delegate()` to review and forward claims.
        super(AssembleOrder, self).delegate()
        # Appoint and assign claims for all code expressions in
        # the order list.
        for code, direction in self.term.order:
            self.state.schedule(code, router=self.term.kid)

    def assemble_order(self):
        # Assemble the `ORDER BY` clause.
        # The list of `(phrase, direction)` pairs.
        order = []
        # Evaluate the code expressions in the order list.
        for code, direction in self.term.order:
            # If a code does not have units, it must be a literal or
            # a scalar function, and thus it cannot affect the ordering
            # of the frame rows.  We can safely weed it out.
            if not code.units:
                continue
            phrase = self.state.evaluate(code, router=self.term.kid)
            phrase = FormulaPhrase(SortDirectionSig(direction),
                                   phrase.domain, phrase.is_nullable,
                                   phrase.expression, base=phrase)
            order.append(phrase)
        return order

    def assemble_limit(self):
        # Assemble the `LIMIT` clause.
        return self.term.limit

    def assemble_offset(self):
        # Assemble the `OFFSET` clause.
        return self.term.offset


class AssembleProjection(Assemble):
    """
    Assembles a frame for a projection term.
    """

    adapt(ProjectionTerm)

    def delegate(self):
        # Update the dispatching context to use the routing table
        # of the child term.
        # Note: a projection term is special in that it does not provide
        # all the routes of its child term.  In particular, when evaluating
        # an aggregate expression, all its units must be appointed against
        # the child's routing table.  Only aggregate units target a projection
        # term directly, therefore updating the routing table should not
        # affect evaluation of any other claims.
        self.state.push_gate(router=self.term.kid)
        # Call the super `delegate()` to review and forward claims.
        super(AssembleProjection, self).delegate()
        # Appoint and assign claims for the projection kernel.
        for code in self.term.kernels:
            self.state.schedule(code)
        # Restore the original dispatching context.
        self.state.pop_gate()

    def assemble_select(self):
        # Just like in `delegate()`, we update the dispatching context
        # to use the routing table of the child term.
        self.state.push_gate(router=self.term.kid)
        # Call the super implementation to generate a `SELECT` list.
        select = super(AssembleProjection, self).assemble_select()
        # Restore the original dispatching context.
        self.state.pop_gate()
        return select

    def assemble_group(self):
        # Assemble a `GROUP BY` clause.
        # The list of phrases included to the clause.
        group = []
        # Evaluate all the code expressions in the kernel.
        for code in self.term.kernels:
            # If a code does not have units, it must be a scalar function
            # or a literal, and therefore it cannot affect the projection.
            # We can safely weed it out.
            if not code.units:
                continue
            phrase = self.state.evaluate(code, router=self.term.kid)
            group.append(phrase)
        # It may happen that the kernel of the projection is empty, which
        # means the range of the projection is the scalar flow.  SQL
        # recognizes scalar projections by detecting an aggregate in
        # the `SELECT` list, so, technically, we could keep the `GROUP BY`
        # list empty.  However, when collapsing frames, we must be able
        # to distinguish between projection (scalar or not) and non-projection
        # frames.  To make it easy, we never generate an empty `GROUP BY`
        # list for projection terms.  When the projection kernel is empty,
        # we just add a dummy literal to the list.  This literal will be
        # removed by the reducing process.
        if not group:
            group = [TruePhrase(self.term.expression)]
        return group


class AssembleJoin(Assemble):
    """
    Assembles a frame for a join term.
    """

    adapt(JoinTerm)

    def delegate(self):
        # Call the super `delegate()` to review and forward claims.
        super(AssembleJoin, self).delegate()
        # Appoint and assign claims for the join condition.
        # The join condition is composed of equality expressions
        # of the form: `lop = rop`, where the the operands are
        # exported from the left child and the right child respectively.
        for joint in self.term.joints:
            self.state.schedule(joint.lop, router=self.term.lkid)
            self.state.schedule(joint.rop, router=self.term.rkid)

    def assemble_include(self):
        # Assemble the `FROM` list.
        # Set up the dispatch context for the first child term.
        # Note that currently right joins are never generated
        # by the compiler, so `is_nullable` is always `False`.
        self.state.push_gate(is_nullable=self.term.is_right,
                             dispatcher=self.term.lkid)
        # Assemble a frame for the first child.
        lframe = self.state.assemble(self.term.lkid)
        # Restore the original dispatch context.
        self.state.pop_gate()
        # Generate a `JOIN` clause for the first subframe.
        lanchor = LeadingAnchor(lframe)
        # Set up the dispatch context for the second child term.
        self.state.push_gate(is_nullable=self.term.is_left,
                             dispatcher=self.term.rkid)
        # Assemble a frame for the second child.
        rframe = self.state.assemble(self.term.rkid)
        # Restore the original dispatch context.
        self.state.pop_gate()
        # Generate the join condition, which is a conjunction of equalities
        # of the form: `lop = rop`.  The operands of the equality operator
        # are evaluated against the left subframe and the right subframe
        # respectively.
        equalities = []
        for joint in self.term.joints:
            lop = self.state.evaluate(joint.lop, router=self.term.lkid)
            rop = self.state.evaluate(joint.rop, router=self.term.rkid)
            is_nullable = (lop.is_nullable or rop.is_nullable)
            signature = IsEqualSig(+1)
            equality = FormulaPhrase(signature, coerce(BooleanDomain()),
                                     is_nullable, self.term.expression,
                                     lop=lop, rop=rop)
            equalities.append(equality)
        condition = None
        if equalities:
            is_nullable = any(equality.is_nullable for equality in equalities)
            condition = FormulaPhrase(AndSig(), coerce(BooleanDomain()),
                                      is_nullable, self.term.expression,
                                      ops=equalities)
        elif self.term.is_left or self.term.is_right:
            condition = TruePhrase(self.term.expression)
            condition = self.state.to_predicate(condition)
        # Generate a `JOIN` clause for the second subframe.
        ranchor = Anchor(rframe, condition,
                         self.term.is_left, self.term.is_right)
        # Return the generated `FROM` list.
        return [lanchor, ranchor]


class AssembleEmbedding(Assemble):
    """
    Assembles a frame for an embedding term.
    """

    adapt(EmbeddingTerm)

    def delegate(self):
        # Call the super `delegate()` to review and forward claims.
        super(AssembleEmbedding, self).delegate()

        for code in self.term.correlations:
            self.state.schedule(code, router=self.term.lkid)

    def assemble_include(self):
        # Assemble the `FROM` list.
        # Although embedding is a binary term, only its first child goes
        # to the `FROM` list, so the assembling here practically coincides
        # with the one for a unary term.

        # Set up the dispatch context for the child term.
        self.state.push_gate(is_nullable=False, dispatcher=self.term.lkid)
        # Assemble a frame corresponding to the first child.
        frame = self.state.assemble(self.term.lkid)
        # Restore the original dispatch context.
        self.state.pop_gate()
        # Generate a `JOIN` clause (without any join condition).
        anchor = LeadingAnchor(frame)
        # Return a `FROM` list with a single subframe.
        return [anchor]

    def assemble_embed(self):
        # Assemble the list of embedded frames.

        correlations = {}
        for code in self.term.correlations:
            phrase = self.state.evaluate(code, router=self.term.lkid)
            correlations[code] = phrase
        self.state.push_correlations(correlations)

        # Set up the dispatch context for the embedded term.  An embedded
        # frame is always considered nullable, although it may not be true
        # in some cases.  In practice, nullability of an embedded frame does
        # not affect the translator.
        self.state.push_gate(is_nullable=True, dispatcher=self.term.rkid)
        # Generate a frame for the embedded term.
        frame = self.state.assemble(self.term.rkid)
        # Restore the original dispatch context.
        self.state.pop_gate()
        self.state.pop_correlations()
        # Return a list of subframes embedded to the assembled frame.
        return [frame]


class AssembleCorrelation(Assemble):

    adapt(CorrelationTerm)

    def delegate(self):
        # An embedded frame is special in that its `SELECT` clause could
        # contain only one phrase (corresponding to a correlation unit).
        # It is a responsibility of the compiler to ensure that there is
        # one and only one unit targeted to a correlation term.
        assert len(self.claims) == 1
        # Get the (only) claim.  It must be a compound claim of a correlation
        # unit targeted to the term itself.
        [claim] = self.claims
        assert claim.target == self.term.tag
        assert claim.unit.is_compound
        # Dismantle the unit, appoint and assign its subunits.
        self.state.schedule(claim.unit.code)
        # Note that we do not need to assign the units of `joints`: it is done
        # by our parent, see `AssembleEmbedding.delegate()`.

    def assemble_select(self):
        # Assemble a `SELECT` clause.
        # The (only) claim delegated (and targeted) to the frame.
        [claim] = self.claims
        # All the subunits must be already satisfied, so we could evaluate
        # a phrase corresponding to the claim unit.
        phrase = self.state.evaluate(claim.unit.code)
        # Generate an export phrase and satisfy the claim.
        domain = phrase.domain
        # Values produced by embedded frames are always nullable.
        # FIXME: is it always true? Still, it is safe to assume so, and it is
        # unlikely to significantly degrade the generated SQL.
        is_nullable = True
        export = EmbeddingPhrase(self.term.tag, domain, is_nullable, claim.unit)
        self.state.supply(claim, export)
        # Return the `SELECT` list.
        return [phrase]


class AssembleSegment(Assemble):
    """
    Assembles a frame for a segment term.
    """

    adapt(SegmentTerm)

    def delegate(self):
        # This is a top-level frame, so it can't have claims.
        assert not self.claims
        # Assign all the units in the `SELECT` clause.
        self.state.schedule(self.term.code.code)
        for code in self.term.superkeys:
            self.state.schedule(code)
        if self.term.subtrees:
            for code in self.term.keys:
                self.state.schedule(code)

    def assemble_select(self):
        # Assemble a `SELECT` clause.
        select = []
        stencils = []
        phrase_groups = []
        phrase_groups.append(self.state.evaluate_all(self.term.code.code))
        phrase_groups.append([self.state.evaluate(code)
                              for code in self.term.superkeys])
        if self.term.subtrees:
            phrase_groups.append([self.state.evaluate(code)
                                  for code in self.term.keys])
        else:
            phrase_groups.append([])
        index_by_phrase = {}
        for phrases in phrase_groups:
            stencil = []
            for phrase in phrases:
                if phrase not in index_by_phrase:
                    index = len(select)
                    select.append(phrase)
                    index_by_phrase[phrase] = index
                stencil.append(index_by_phrase[phrase])
            stencils.append(stencil)
        if not select:
            select = [TruePhrase(self.term.code)]
        self.state.save_stencils(self.term, stencils)
        return select

    def assemble_subtrees(self):
        subtrees = []
        duplicates = set()
        for code in self.term.code.code.segments:
            if code in duplicates:
                continue
            duplicates.add(code)
            subterm = self.term.subtrees[code]
            location = len(subtrees)
            self.state.set_tree(subterm)
            self.state.save_location(subterm, location)
            subframe = self.state.assemble(subterm)
            subtrees.append(subframe)
        self.state.save_subterms(self.term,
                                 [frame.term for frame in subtrees])
        return subtrees

    def assemble_frame(self, include, embed, select,
                       where, group, having,
                       order, limit, offset):
        subtrees = self.assemble_subtrees()
        return SegmentFrame(include, embed, select,
                           where, group, having,
                           order, limit, offset,
                           subtrees, self.term)


class AssembleQuery(Assemble):
    """
    Assembles a top-level query frame.
    """

    adapt(QueryTerm)

    def __call__(self):
        # Compile the segment frame.
        segment = None
        compose = None
        if self.term.segment is not None:
            # Initialize the state.
            self.state.set_tree(self.term.segment)
            self.state.save_location(self.term.segment, None)
            self.state.save_subterms(None, [self.term.segment])
            # Compile the segment.
            segment = self.state.assemble(self.term.segment)
            # Generate the compositor.
            self.state.push_name(self.term.binding.profile.tag)
            compose = self.state.decompose(self.term.segment.code)
            # Clean up the state.
            self.state.flush()
        # Generate a frame node.
        return QueryFrame(segment, compose, self.term)


class Evaluate(Adapter):
    """
    Translates a code node to a phrase node.

    This is an interface adapter; see subclasses for implementations.

    The :class:`Evaluate` adapter has the following signature::

        Evaluate(Code, AssemblingState) -> Phrase

    The adapter is polymorphic on the `Code` argument.

    `code` (:class:`htsql.core.tr.flow.Code`)
        The code node to translate.

    `state` (:class:`AssemblingState`)
        The current state of the assembling process.
    """

    adapt(Code)

    def __init__(self, code, state):
        assert isinstance(code, Code)
        assert isinstance(state, AssemblingState)
        self.code = code
        self.state = state

    def __call__(self):
        # Implement in subclasses.
        raise NotImplementedError("the evaluate adapter is not implemented"
                                  " for a %r node" % self.code)


class EvaluateSegment(Evaluate):

    adapt(SegmentCode)

    def __call__(self):
        # Nested segments are serialized into a separate frame tree.
        return []


class EvaluateLiteral(Evaluate):
    """
    Evaluates a literal code.
    """

    adapt(LiteralCode)

    def __call__(self):
        # Keep all attributes, but switch the class.
        if not isinstance(self.code.domain, UntypedDomain):
            yield LiteralPhrase(self.code.value, self.code.domain, self.code)


class EvaluateCast(Evaluate):
    """
    Evaluates a cast code.
    """

    adapt(CastCode)

    def __call__(self):
        # Evaluate the operand and generate a phrase node.
        # Note that the for some source and target domains, the reducer will
        # retranslate a generic cast phrase to a more specific expression.
        base = self.state.evaluate(self.code.base)
        yield CastPhrase(base, self.code.domain, base.is_nullable, self.code)


class EvaluateRecord(Evaluate):

    adapt_many(RecordCode,
               IdentityCode)

    def __call__(self):
        for field in self.code.fields:
            for phrase in self.state.evaluate_all(field):
                yield phrase


class EvaluateAnnihilator(Evaluate):

    adapt(AnnihilatorCode)

    def __call__(self):
        yield self.state.evaluate(self.code.indicator)
        for phrase in self.state.evaluate_all(self.code.code):
            yield phrase


class EvaluateCorrelation(Evaluate):

    adapt(CorrelationCode)

    def __call__(self):
        assert self.code.code in self.state.correlations
        # FIXME: is this correct in case of nested correlated subqueries?
        # FIXME: implement decompose?
        yield self.state.correlations[self.code.code]


class EvaluateFormula(Evaluate):
    """
    Evaluates a formula node.

    The evaluation could be specific to the formula signature and is
    implemented by the :class:`EvaluateBySignature` adapter.
    """

    adapt(FormulaCode)

    def __call__(self):
        # Delegate the evaluation to `EvaluteBySignature`.
        return EvaluateBySignature.__invoke__(self.code, self.state)


class EvaluateBySignature(Adapter):
    """
    Evaluates a formula node.

    This is an auxiliary adapter used to evaluate
    :class:`htsql.core.tr.flow.FormulaCode` nodes.  The adapter is polymorphic
    on the formula signature.

    Unless overridden, the adapter evaluates the arguments of the formula
    and generates a new formula phrase with the same signature.

    `code` (:class:`htsql.core.tr.flow.FormulaCode`)
        The formula node to evaluate.

    `state` (:class:`AssemblingState`)
        The current state of the assembling process.

    Aliases:

    `signature` (:class:`htsql.core.tr.signature.Signature`)
        The signature of the formula.

    `domain` (:class:`htsql.core.tr.domain.Domain`)
        The co-domain of the formula.

    `arguments` (:class:`htsql.core.tr.signature.Bag`)
        The arguments of the formula.
    """

    adapt(Signature)

    @classmethod
    def __dispatch__(interface, code, *args, **kwds):
        # Override the default dispatch since the adapter is polymorphic
        # on the type of the formula signature, not on the formula itself.
        assert isinstance(code, FormulaCode)
        return (type(code.signature),)

    def __init__(self, code, state):
        assert isinstance(code, FormulaCode)
        assert isinstance(state, AssemblingState)
        self.code = code
        self.state = state
        # Extract commonly used attributes of the node.
        self.signature = code.signature
        self.domain = code.domain
        self.arguments = code.arguments

    def __call__(self):
        # Evaluate the arguments of the formula.
        arguments = self.arguments.map(self.state.evaluate)
        # By default, assume that the formula is null-regular.  The adapter
        # should be overridden for nodes where it is not the case.
        is_nullable = any(cell.is_nullable for cell in arguments.cells())
        # Generate a new formula node.
        yield FormulaPhrase(self.signature,
                            self.domain,
                            is_nullable,
                            self.code,
                            **arguments)


class EvaluateIsEqualBase(EvaluateBySignature):

    adapt_many(IsEqualSig, IsInSig, CompareSig)

    def __call__(self):
        for phrase in super(EvaluateIsEqualBase, self).__call__():
            yield self.state.from_predicate(phrase)


class EvaluateIsTotallyEqualBase(EvaluateBySignature):
    """
    Evaluates the total equality (``==``) operator.
    """

    adapt_many(IsTotallyEqualSig, IsNullSig)

    def __call__(self):
        # Override the default implementation since the total equality
        # operator is not null-regular, and, in fact, always not nullable.
        arguments = self.arguments.map(self.state.evaluate)
        phrase = FormulaPhrase(self.signature, self.domain,
                               False, self.code, **arguments)
        yield self.state.from_predicate(phrase)


class EvaluateNullIf(EvaluateBySignature):
    """
    Evaluates the ``null_if()`` operator.
    """

    adapt(NullIfSig)

    def __call__(self):
        # Override the default implementation since the `null_if()`
        # operator is not null-regular, and, in fact, is always nullable.
        arguments = self.arguments.map(self.state.evaluate)
        yield FormulaPhrase(self.signature, self.domain,
                            True, self.code, **arguments)


class EvaluateIfNull(EvaluateBySignature):
    """
    Evaluates the ``if_null()`` operator.
    """

    adapt(IfNullSig)

    def __call__(self):
        # Override the default implementation since the `null_if()`
        # operator is not null-regular.  It is nullable only if all of
        # its arguments are nullable.
        arguments = self.arguments.map(self.state.evaluate)
        is_nullable = all(cell.is_nullable for cell in arguments.cells())
        yield FormulaPhrase(self.signature, self.domain,
                            is_nullable, self.code, **arguments)


class EvaluateAndOrNot(EvaluateBySignature):

    adapt_many(AndSig, OrSig, NotSig)

    def __call__(self):
        arguments = (self.arguments.map(self.state.evaluate)
                                   .map(self.state.to_predicate))
        is_nullable = any(cell.is_nullable for cell in arguments.cells())
        phrase = FormulaPhrase(self.signature,
                               self.domain,
                               is_nullable,
                               self.code,
                               **arguments)
        yield self.state.from_predicate(phrase)


class EvaluateUnit(Evaluate):
    """
    Evaluates a unit.
    """

    adapt(Unit)

    def __call__(self):
        # Generate a claim for a unit (for the second time).
        claim = self.state.appoint(self.code)
        # We expect the claim to be already satisfied.
        assert claim in self.state.phrases_by_claim
        # Return the export phrase corresponding to the claim.
        return self.state.phrases_by_claim[claim]


class Decompose(Adapter):

    adapt(Code)

    def __init__(self, code, state):
        assert isinstance(code, Code)
        assert isinstance(state, AssemblingState)
        self.code = code
        self.state = state

    def __call__(self):
        index = self.state.get_next_index()
        def compose_value(row, stream, index=index):
            return row[index]
        return compose_value


class DecomposeSegment(Decompose):

    adapt(SegmentCode)

    def __call__(self):
        if self.state.segment is None:
            self.state.push_segment(self.code)
            compose_code = self.state.decompose(self.code.code)
            self.state.pop_segment()
            is_single = (isinstance(self.code.binding, WeakSegmentBinding))
            if not is_single:
                def compose_root_segment(row, stream,
                                         compose_code=compose_code):
                    items = []
                    for row in stream:
                        items.append(compose_code(row, stream))
                    return items
                return compose_root_segment
            else:
                def compose_root_value(row, stream,
                                       compose_code=compose_code):
                    items = []
                    for row in stream:
                        items.append(compose_code(row, stream))
                    assert len(items) <= 1
                    if items:
                        return items[0]
                    else:
                        return None
                return compose_root_value
        else:
            key_stencil = self.state.get_key_stencil()
            self.state.push_segment(self.code)
            location = self.state.get_location()
            superkey_stencil = self.state.get_superkey_stencil()
            compose_code = self.state.decompose(self.code.code)
            self.state.pop_segment()
            def compose_nested_segment(row, stream, compose_code=compose_code,
                                       location=location,
                                       key_stencil=key_stencil,
                                       superkey_stencil=superkey_stencil):
                items = []
                key = stream.get(key_stencil)
                substream = stream.substreams[location]
                for row in substream.slice(superkey_stencil, key):
                    items.append(compose_code(row, substream))
                return items
            return compose_nested_segment


class DecomposeCompound(Decompose):

    adapt(CompoundUnit)

    def __call__(self):
        return self.state.decompose(self.code.code)


class DecomposeLiteral(Decompose):

    adapt(LiteralCode)

    def __call__(self):
        if not isinstance(self.code.domain, UntypedDomain):
            return super(DecomposeLiteral, self).__call__()
        def compose_untyped(row, stream, value=self.code.value):
            return value
        return compose_untyped


class DecomposeRecord(Decompose):

    adapt(RecordCode)

    def __call__(self):
        compose_fields = []
        field_names = []
        for field, profile in zip(self.code.fields,
                                  self.code.domain.fields):
            field_names.append(profile.tag)
            self.state.push_name(profile.tag)
            compose_field = self.state.decompose(field)
            self.state.pop_name()
            compose_fields.append(compose_field)
        record_class = Record.make(self.state.name, field_names)
        def compose_record(row, stream, record_class=record_class,
                           compose_fields=compose_fields):
            return record_class(compose_field(row, stream)
                                for compose_field in compose_fields)
        return compose_record


class DecomposeIdentity(Decompose):

    adapt(IdentityCode)

    def __call__(self):
        compose_fields = []
        for field in self.code.fields:
            compose_field = self.state.decompose(field)
            compose_fields.append(compose_field)
        # FIXME: a reference leak?
        id_class = ID.make(self.code.domain.dump)
        def compose_identity(row, stream, compose_fields=compose_fields,
                             id_class=id_class):
            return id_class(compose_field(row, stream)
                            for compose_field in compose_fields)
        return compose_identity


class DecomposeAnnihilator(Decompose):

    adapt(AnnihilatorCode)

    def __call__(self):
        compose_indicator = self.state.decompose(self.code.indicator)
        compose = self.state.decompose(self.code.code)
        def compose_nullable(row, stream,
                             compose_indicator=compose_indicator,
                             compose=compose):
            value = compose(row, stream)
            if compose_indicator(row, stream) is None:
                return None
            return value
        return compose_nullable


def assemble(term, state=None):
    """
    Compiles a new frame node for the given term.

    Returns a :class:`htsql.core.tr.frame.Frame` instance.

    `term` (:class:`htsql.core.tr.term.Term`)
        A term node.

    `state` (:class:`AssemblingState` or ``None``)
        The assembling state to use.  If not set, a new assembling
        state is instantiated.
    """
    # Instantiate a new assembling state if not given one.
    if state is None:
        state = AssemblingState()
    # Realize and apply the `Assemble` adapter; return the generated frame.
    return Assemble.__invoke__(term, state)


