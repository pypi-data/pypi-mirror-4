******************************
Parsing Infix Math Expressions
******************************

Problem
=======

Say you want to put together a grammar that will parse simple mathematical expressions, such as ``1 + 2 * (3 + 4)``.  To do this properly, your grammar needs to do several things:

   * Properly parse decimal numbers
   * Handle the basic "infix" math operators: "+", "-", "*", "/" *(they're called "infix" because they come "in" between their two arguments)*
   * Handle parenthesized sub-expressions (of arbitrary depth)
   * Make it easy to evaluate the expression in the right order (i.e. left-to-right, parens first, etc)
   * Properly account for operator precedence (i.e. multiplication happens before addition/subtraction)

Getting all this right can be a bit tricky, but believe it or not, you can construct a grammar with Modgrammar which does all this automatically (and even evaluates the result for you).  This example will show you how.

Solution
========

Really, the trickiest aspect of getting this right has to do with the concept of operator precedence.  If we want things to be ordered properly in the parsing result tree, the grammar we create must know that, for example, in the expression ``1 + 2 * 3``, the multiplication should be done first, then the addition.  This requires that the grammar have some concept of some expressions being "more desirable" than others when parsing the input text.

The way to do this is to take advantage of the fact that the OR operator in Modgrammar always tries to match in a left-to-right order, which means you can tell it to try to match certain (more desirable) expressions before trying (less desirable) others, so, for example, a simple grammar implementing addition, multiplication, and division (with standard precedences) might look something like the 
following::

    from modgrammar import * 

    class Number (Grammar): 
        grammar = (OPTIONAL('-'), WORD('0-9'), OPTIONAL('.', WORD('0-9'))) 

    class ParenExpr (Grammar): 
        grammar = (L('('), REF('Expr'), L(')')) 

    class P0Term (Grammar): 
        grammar = (ParenExpr | Number) 

    class P0Expr (Grammar): 
        grammar = (P0Term, L('/'), P0Term) 

    class P1Term (Grammar): 
        grammar = (P0Expr | ParenExpr | Number) 

    class P1Expr (Grammar): 
        grammar = (P1Term, L('*'), P1Term) 

    class P2Term (Grammar): 
        grammar = (P0Expr | P1Expr | ParenExpr | Number) 

    class P2Expr (Grammar): 
        grammar = (P2Term, L('+') | L('-'), P2Term) 

    class Expr (Grammar): 
        grammar = (P2Expr | P1Expr | P0Expr | ParenExpr | Number) 

As you can see, for each precedence "tier", we define an expression grammar where its terms can either be a number or a higher-precedence expression, and we always try to match the highest-precedence expression first. 

(Note that the exception is the final :class:`Expr` grammar, where we reverse the order and check in lowest-to-highest precedence, because we want to match the largest possible expression, thus for, say, ``1 * 2 + 3``, it will try to match a P2Expr (and find "1 * 2" "+" "3") before looking for a P1Expr (which would just match "1" "*" "2" and leave a remainder of "+3"). 

There is one problem with all of this, however:  This does correctly order operators of different precedence, but it doesn't deal well with strings of operators that have the same precedence (for example, ``1 + 2 + 3`` gets parsed as "1 + 2" with a remainder of "+ 3").  The obvious way to fix this would be to simply make the grammars recursive (that is, a P2Term could itself be another P2Expr), but the problem with this is that it would lead to what's known as left-recursion (where P2Expr could start with a P2Expr, which could start with a P2Expr, which could...), which pretty obviously results in infinite parsing loops pretty quickly.  We could limit it to only allowing recursion on the right-hand side of the expression, which would fix the left-recursion problem, but has an unfortunate side-effect of making the resulting math expressions seem to evaluate in a right-to-left order, which is not what is usually desired (that is, for example, ``1 - 2 + 3`` would be evaluated as ``1 - (2 + 3)`` (= -4) instead of the expected ``(1 - 2) + 3`` (= 2). 

Luckily, there is another way:  We can just define each type of expression as being a term followed by "one or more" operator+term pairs, so then if you say (for example) ``1 - 2 + 3``, it would give you back an expression object which actually has three terms ("1", "2", and "3", separated by two operators ("-" and "+"), but the operators are guaranteed to be of the same precedence, so when calculating the value of the expression, you can just iterate through them in a left-to-right order and it'll give you the right answer).  The following modified version illustrates this:

.. literalinclude:: ../../modgrammar/examples/infix_precedence.py

You may notice that we also added a :meth:`value` method to each of the grammar classes.  This shows off a nifty additional benefit of Modgrammar:  We can add functionality to the result objects in the parse tree we get back from the parser.  Now, each of the parse result objects we get back will have a :meth:`value` method we can call which will evaluate the expression it parsed and give us back the final value, so we could call it on each of the :class:`Number` objects to find out what number was specified, or more interestingly we can call it on whole sub-expressions (or even the whole :class:`Expr` expression) to get the result of evaluating all of the components and operations in all the right ways.

This can be seen with the example invocation code at the bottom.  If this code is run as a script, it will take an expression from the command line, parse it, call :meth:`value` on the result, and print the answer.

(*Note:* This code is available in the ``examples`` directory as ``infix_precedence.py``.  Give it a try!)

