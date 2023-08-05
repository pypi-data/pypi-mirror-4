# from collective.cart.core.error import InfiniteLoopError
# from collective.cart.core.interfaces import IRandomDigits
# from five import grok
# from random import choice
# from string import digits
# from zope.interface import implements


# class RandomDigits(grok.GlobalUtility):
#     implements(IRandomDigits)

#     def _random_number(self, number):
#         return "".join(choice(digits) for d in xrange(number))

#     # def loop(self, number, ids):
#     #     digits = self._random_number(number)
#     #     if digits not in ids:
#     #         return digits

#     def __call__(self, number, ids):
#         if not ids:
#             return self._random_number(number)
#         if len(ids) == 10 ** number:
#             raise InfiniteLoopError(number)
#         digits = self._random_number(number)
#         while digits in ids:
#             digits = self._random_number(number)
#         else:
#             return digits
