# coding: utf8

from __future__ import unicode_literals, print_function
from efc.rpn_builder.errors import OperandsMissing
from efc.rpn_builder.parser.operands import (SimpleOperand, SingleCellOperand, CellSetOperand,
                                             ErrorOperand, SimpleSetOperand, ValueErrorOperand, Operand)
from efc.rpn_builder.parser.operations import Operation
from efc.utils import TokensLine

from six.moves import range

__all__ = ('RPN',)


class RPN(TokensLine):
    def handle_result(self, result, ws_name, source):
        if len(result) == 1:
            return result[0]
        else:
            # Trying to get first error in result
            for item in (i for i in result if isinstance(i, ErrorOperand)):
                return item

            if isinstance(result[0], SingleCellOperand):
                set_type = CellSetOperand
            elif isinstance(result[0], SimpleOperand):
                set_type = SimpleSetOperand
            else:
                return result

            # Trying to build set from result
            try:
                result_set = set_type(ws_name=ws_name, source=source)
                result_set.add_row(result)
                return result_set
            except ValueErrorOperand as err:
                return err

    def calc(self, ws_name, source):
        result = []

        result_append = result.append
        result_pop = result.pop
        for token in self:
            if isinstance(token, Operand):
                result_append(token)
            elif isinstance(token, Operation):
                try:
                    args = [result_pop() for _ in range(token.operands_count)]
                except IndexError:
                    raise OperandsMissing(token, self)

                args.reverse()

                v = token.eval(*args)
                result_append(v)

        return self.handle_result(result, ws_name, source)